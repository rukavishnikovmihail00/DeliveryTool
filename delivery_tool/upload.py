import logging
import os
import subprocess
import tempfile
import zipfile
from functools import partial
from multiprocessing.dummy import Pool

import backoff
import requests
import yaml
from artifactory import RepositoryLocal

from delivery_tool.artifactory import connect, calculate_by_repository
from delivery_tool.exceptions import ApplicationException
from delivery_tool.utils import parse_file
from delivery_tool.variables import ARCHIVE_NAME, ARTIFACTORY_YAML_NAME

tf = tempfile.TemporaryDirectory()
log = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10)
def thread_process(artifactory_url, image):
    image = image[image.rfind('/') + len('/'):]
    image_name = image[image.rfind('/') + len('/'):image.rfind(':')]

    subprocess.run(['skopeo', '--insecure-policy', 'copy', '--dest-tls-verify=false',
                    '--format', 'v2s2', '--src-shared-blob-dir', f"{tf.name}/layers",
                    'oci:' + tf.name + '/images/' + image_name,
                    'docker://' + artifactory_url + '/' + image])


def upload():
    log.info("### Execute upload function ###")
    config = parse_file(ARTIFACTORY_YAML_NAME)
    exceptions = []
    url = config['url']
    name_files = config['repositories']['files']
    name_docker = config['repositories']['docker']

    try:
        artifactory = connect(url, name_files)
    except requests.exceptions.RequestException as e:
        raise ApplicationException(f"Couldn`t connect to Artifactory by {url}") from e

    repository_docker = artifactory.find_repository_local(name_docker)
    repository_files = artifactory.find_repository_local(name_files)

    if repository_files is None:
        repository_generic = RepositoryLocal(artifactory, name_files)
        repository_generic.create()
    else:
        repository_generic = repository_files

    size_generic = calculate_by_repository(repository_generic, name_files)
    size_docker = calculate_by_repository(repository_docker, name_docker)

    zipfile.ZipFile(ARCHIVE_NAME).extractall(tf.name)
    
    log.info("Upload docker images")
    subprocess.run(['skopeo', '--insecure-policy', 'login', '--tls-verify=false', '-u', os.getenv('ARTIFACTORY_LOG'), '-p',
                    os.getenv('ARTIFACTORY_PASS'), config['docker_registry']])

    for i in os.listdir(tf.name):
        if (i != 'images') and (i != 'layers') and (i != 'images_info.yaml'):
            repository_generic.deploy_file(tf.name + '/' + i)
    with open(tf.name + '/images_info.yaml', 'r') as im:
        images_list = yaml.load(im, Loader=yaml.Loader)

    pool = Pool(4)
    try:
        func = partial(thread_process, config['docker_registry'])
    except requests.exceptions.RequestException as e:
        exceptions.append(e)
    threads = pool.map(func, images_list['images'])
    pool.close()
    pool.join()

    if exceptions:
        raise ApplicationException("Some files were not uploaded:" + '\n'.join(exceptions))
    else:
        log.info("All the files have been uploaded successfully")

    new_size_generic = calculate_by_repository(repository_generic, name_files)
    new_size_docker = calculate_by_repository(repository_docker, name_docker)

    log.info(f"The difference in {name_files} is {round((new_size_generic - size_generic) / 1048576, 2)} MB")
    log.info(f"The difference in {name_docker} is {round((new_size_docker - size_docker) / 1048576, 2)} MB")


