import logging
import os

import backoff
import requests
from artifactory import RepositoryLocal, ArtifactoryPath

from delivery_tool.exceptions import ApplicationException

log = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10)
def connect(url, name):
    log.info("Connect to artifactory instance")
    art = ArtifactoryPath(url + '/' + name, auth=(os.getenv('ARTIFACTORY_LOG'), os.getenv('ARTIFACTORY_PASS')))
    return art


def create_repo(url, repository_name, repository_type):
    try:
        artifactory_instance = connect(url, repository_name)
        repos = RepositoryLocal(artifactory_instance, repository_name, packageType=repository_type)
        log.info(f"Create repository {repository_name}")
        repos.create()
    except requests.exceptions.RequestException as e:
        raise ApplicationException(f"The repository {repository_name} was not created") from e


def calculate_by_artifactory(artifactory_instance, repository_name):
    try:
        repository = artifactory_instance.find_repository_local(repository_name)
    except Exception:
        raise ApplicationException(f"Couldn`t find local repository from specified: {repository_name}")
    calculate_by_repository(repository, repository_name)


def calculate_by_repository(repository_instance, repository_name):
    log.info(f"Calculate repository {repository_name} size")
    summary_size = 0

    for item in repository_instance:
        summary_size += item.stat().size

    log.info(f"Summary size of files in {repository_name} is {round(summary_size / 1048576, 2)} MB")
    return summary_size
