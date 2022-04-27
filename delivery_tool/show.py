import logging
import requests

from delivery_tool.artifactory import connect, calculate_by_artifactory
from delivery_tool.exceptions import ApplicationException
from delivery_tool.utils import parse_file
from delivery_tool.variables import ARTIFACTORY_YAML_NAME

log = logging.getLogger(__name__)


def show():
    log.info("### Execute show function ###")
    artifactory_config = parse_file(ARTIFACTORY_YAML_NAME)

    url = artifactory_config['url']
    name_generic = artifactory_config['repositories']['files']
    name_docker = artifactory_config['repositories']['docker']

    try:
        artifactory_instance = connect(url, name_generic)
    except requests.exceptions.RequestException as e:
        raise ApplicationException(f"Cannot connect to Artifactory by url {url}") from e

    calculate_by_artifactory(artifactory_instance, name_generic)
    calculate_by_artifactory(artifactory_instance, name_docker)

