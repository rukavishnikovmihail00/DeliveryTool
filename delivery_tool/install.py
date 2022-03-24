import subprocess
import tempfile
import zipfile

import backoff
import requests
import yaml
from artifactory import ArtifactoryPath, RepositoryLocal

from delivery_tool.exceptions import ApplicationException


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10)
def connect(url, name, creds):
    art = ArtifactoryPath(url + '/' + name, auth=(creds['login'], creds['password']))
    return art


def create_repo(config, log, creds):
    url = config['url']
    name = config['repositories']['files']
    
    try:
        art = connect(url, name, creds)
    
        repos = RepositoryLocal(art, name, packageType=RepositoryLocal.GENERIC)
        repos.create()
        log.info("The repository was created successfully")
    except requests.exceptions.RequestException as e:
        raise ApplicationException(f"The repository {name} was not created") from e
 

def install(log, playbook, config, creds, rep):
    tf = tempfile.TemporaryDirectory()

    artifactory_home = config['home_dir']
    url = config['url']
    lic = config['lic_path']
    docker_name = config['repositories']['docker']
    port = config['docker_registry'][config['docker_registry'].rfind(':') + len(':'):]

    data = {'artifactory_home': artifactory_home, 'url': url[:url.rfind('/')], 'lic_path': lic,
            'docker_name': docker_name, 'port': port, 'ip': url[url.find('/') + len('//'):url.rfind(':')]}

    zipfile.ZipFile('delivery-tool-rukavishnikov-0.1.0.pyz').extractall(tf.name)
    zipfile.ZipFile(f"{tf.name}/delivery_tool/ansible.zip").extractall(tf.name)

    with open(f"{tf.name}/ansible/vars.yaml", 'w') as im:  # tf path
        yaml.dump(data, im)

    playbook_path = f"{tf.name}/ansible/{playbook}"
    hosts_path = f"{tf.name}/ansible/hosts"

    log.info(f"Running ansible playbook {playbook}")
    log.info(f"Hosts path is {hosts_path}")

    subprocess.run(['ansible-playbook', '-i', hosts_path, playbook_path])

    if rep:
        create_repo(config, log, creds)





