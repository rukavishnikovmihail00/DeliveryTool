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


def create_repo(config):
    url = config['url']
    name = config['repositories']['files']
    log.info(f"Create repository {name}")

    try:
        art = connect(url, name)

        repos = RepositoryLocal(art, name, packageType=RepositoryLocal.GENERIC)
        repos.create()
        log.info(f"The repository {name} was created successfully")
    except requests.exceptions.RequestException as e:
        raise ApplicationException(f"The repository {name} was not created") from e


def calculate(artifactory, name_generic, name_docker):
    log.info("Calculate repository size")
    try:
        repository_docker = artifactory.find_repository_local(name_docker)
        repository_generic = artifactory.find_repository_local(name_generic)
    except Exception:
        raise ApplicationException(f"Couldn`t find local repository from specified: {name_generic}, {name_docker}")

    summary_size = 0
    summary_size_docker = 0

    for item in repository_docker:
        summary_size_docker += item.stat().size

    for item in repository_generic:
        summary_size += item.stat().size

    return summary_size, summary_size_docker
