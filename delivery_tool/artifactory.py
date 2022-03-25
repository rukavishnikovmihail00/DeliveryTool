import logging

import backoff
import requests
from artifactory import RepositoryLocal, ArtifactoryPath

from delivery_tool.exceptions import ApplicationException

log = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10)
def connect(url, name, creds):
    log.info("Connect to artifactory instance")
    art = ArtifactoryPath(url + '/' + name, auth=(creds['login'], creds['password']))
    return art


def create_repo(config, creds):
    url = config['url']
    name = config['repositories']['files']
    log.info(f"Create repository {name}")

    try:
        art = connect(url, name, creds)

        repos = RepositoryLocal(art, name, packageType=RepositoryLocal.GENERIC)
        repos.create()
        log.info(f"The repository {name} was created successfully")
    except requests.exceptions.RequestException as e:
        raise ApplicationException(f"The repository {name} was not created") from e
