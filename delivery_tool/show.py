import logging

import requests

from delivery_tool.artifactory import connect
from delivery_tool.exceptions import ApplicationException
from delivery_tool.utils import parse_file
from delivery_tool.variables import ARTIFACTORY_YAML_NAME

log = logging.getLogger(__name__)


def calculate(artifactory, name_generic, name_docker):
    log.info("Calculate repository size")
    try:
        rep_docker = artifactory.find_repository_local(name_docker)
        rep_generic = artifactory.find_repository_local(name_generic)
    except Exception:
        raise ApplicationException(f"Couldn`t find local repository from specified: {name_generic}, {name_docker}")

    summary_size = 0
    summary_size_docker = 0

    for p in rep_docker:
        summary_size_docker += p.stat().size

    for p in rep_generic:
        summary_size += p.stat().size
    
    return summary_size, summary_size_docker


def show(creds):
    log.info("### Show repository size ###")
    art_config = parse_file(ARTIFACTORY_YAML_NAME)
    url = art_config['url']
    name_generic = art_config['repositories']['files']
    name_docker = art_config['repositories']['docker']

    try:
        art = connect(url, name_generic, creds)
    except requests.exceptions.RequestException as e:
        raise ApplicationException(f"Cannot connect to Artifactory by url {url}") from e

    summary_size_generic, summary_size_docker = calculate(art, name_generic, name_docker)

    log.info(f"Summary size of files in {name_generic} is {round(summary_size_generic/1048576,2)} MB")
    log.info(f"Summary size of files in {name_docker} is {round(summary_size_docker/1048576,2)} MB")