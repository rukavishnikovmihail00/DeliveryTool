import backoff
import requests
import yaml
from artifactory import ArtifactoryPath, RepositoryLocal
import zipfile
import os
import subprocess
from multiprocessing.dummy import Pool
from functools import partial
from delivery_tool.exceptions import ApplicationException
import tempfile


tf = tempfile.TemporaryDirectory()


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10)
def thread_process(artifactory_url, image):
    image = image[image.rfind('/') + len('/'):]
    image_name = image[image.rfind('/') + len('/'):image.rfind(':')]

    subprocess.run(['skopeo', '--insecure-policy', 'copy', '--dest-tls-verify=false',
                    '--format', 'v2s2', '--src-shared-blob-dir', f"{tf.name}/layers",
                    'oci:' + tf.name + '/images/' + image_name,
                    'docker://' + artifactory_url + '/' + image])


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10)
def connect(url, name, creds):
    art = ArtifactoryPath(url + '/' + name, auth=(creds['login'], creds['password']))
    return art


def upload(config, archive, log, creds):
    exceptions = []
    url = config['url']
    name = config['repositories']['files']
    name_docker = config['repositories']['docker']

    try:
        art = connect(url, name, creds)
    except requests.exceptions.RequestException as e:
        exceptions.append(e)

    res_docker = art.find_repository_local(name_docker)

    rep = art.find_repository_local(name)
    if rep is None:
        repos = RepositoryLocal(art, name)
        repos.create()
    else:
        repos = rep

    summary_size = 0
    summary_size_docker = 0

    for p in res_docker:
        summary_size_docker += p.stat().size

    res = art.find_repository_local(name)
    for p in res:
        summary_size += p.stat().size

    log.info(f"Summary size of files in {name} is {round(summary_size / 1048576, 2)} MB")
    log.info(f"Summary size of files in {name_docker} is {round(summary_size_docker / 1048576, 2)} MB")

    zipfile.ZipFile(archive).extractall(tf.name)
    
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

    res = art.find_repository_local(name)
    for p in res:
        summary_size_last += p.stat().size

    log.info(f"Summary size of files in {name} after the uploading is {round(summary_size_last / 1048576, 2)} MB")
    log.info(f"Summary size of files in {name_docker} after the uploading is {round(summary_size_docker_last / 1048576, 2)} MB")

    log.info(f"The difference in {name} is {round((summary_size_last - summary_size) / 1048576, 2)} MB")
    log.info(f"The difference in {name_docker} is {round((summary_size_docker_last - summary_size_docker) / 1048576, 2)} MB")

    if exceptions:
        raise ApplicationException("Some files were not uploaded:" + '\n'.join(exceptions))
    if not exceptions:
        log.info("All the files have been uploaded successfully")
