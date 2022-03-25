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

from delivery_tool.artifactory import connect
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


def upload(creds):
    config = parse_file(ARTIFACTORY_YAML_NAME)
    exceptions = []
    url = config['url']
    name = config['repositories']['files']
    name_docker = config['repositories']['docker']

    try:
        artifactory = connect(url, name, creds)
    except requests.exceptions.RequestException as e:
        raise ApplicationException(f"Couldn`t connect to Artifactory by {url}") from e

    res_docker = artifactory.find_repository_local(name_docker)

    rep = artifactory.find_repository_local(name)
    if rep is None:
        repos = RepositoryLocal(artifactory, name)
        repos.create()
    else:
        repos = rep

    summary_size = 0
    summary_size_docker = 0

    for p in res_docker:
        summary_size_docker += p.stat().size

    res = artifactory.find_repository_local(name)
    for p in res:
        summary_size += p.stat().size

    log.info(f"Summary size of files in {name} is {round(summary_size / 1048576, 2)} MB")
    log.info(f"Summary size of files in {name_docker} is {round(summary_size_docker / 1048576, 2)} MB")

    zipfile.ZipFile(ARCHIVE_NAME).extractall(tf.name)
    
    log.info("===== Uploading docker images =====")
    subprocess.run(['skopeo', '--insecure-policy', 'login', '--tls-verify=false', '-u', creds['login'], '-p',
                    creds['password'], config['docker_registry']])

    for i in os.listdir(tf.name):
        if (i != 'images') and (i != 'layers') and (i != 'images_info.yaml'):
            repos.deploy_file(tf.name + '/' + i)

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

    summary_size_last = 0
    summary_size_docker_last = 0

    for p in res_docker:
        summary_size_docker_last += p.stat().size

    res = artifactory.find_repository_local(name)
    for p in res:
        summary_size_last += p.stat().size

    log.info(f"Summary size of files in {name} after the uploading is {round(summary_size_last / 1048576, 2)} MB")
    log.info(f"Summary size of files in {name_docker} after the uploading is {round(summary_size_docker_last / 1048576, 2)} MB")

    log.info(f"The difference in {name} is {round((summary_size_last - summary_size) / 1048576, 2)} MB")
    log.info(f"The difference in {name_docker} is {round((summary_size_docker_last - summary_size_docker) / 1048576, 2)} MB")

    if exceptions:
        raise ApplicationException("Some files were not uploaded:" + '\n'.join(exceptions))
    else:
        log.info("All the files have been uploaded successfully")
