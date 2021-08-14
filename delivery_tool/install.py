import zipfile
import backoff
import requests
from artifactory import ArtifactoryPath, RepositoryLocal
import subprocess
import yaml
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
 


def install(log, playbook, config, creds, rep, tf):
    artifactory_home = config['home_dir']
    url = config['url']
    lic = config['lic_path']
    docker_name = config['repositories']['docker']
    port = config['docker_registry'][config['docker_registry'].rfind(':') + len(':'):]

    data = {'artifactory_home': '', 'url': '', 'lic_path': '', 'docker_name': '', 'port': '', 'ip':''}
    data['artifactory_home'] = artifactory_home
    data['url'] = url[:url.rfind('/')]
    data['lic_path'] = lic
    data['docker_name'] = docker_name
    data['port'] = port
    data['ip'] = url[url.find('/')+len('//'):url.rfind(':')]
    
    zipfile.ZipFile('delivery-tool-rukavishnikov-0.1.0.pyz').extractall(tf.name)
    zipfile.ZipFile(f"{tf.name}/delivery_tool/ansible.zip").extractall(tf.name)
    
    
    with open(f"{tf.name}/ansible/vars.yaml", 'w') as im: # tf path
        yaml.dump(data, im)

    playbook = f"{tf.name}/ansible/{playbook}"
    inventory = f"{tf.name}/ansible/hosts"

    log.info("Running ansible playbook")
    subprocess.run(['ansible-playbook', playbook]) 

    if rep:
        create_repo(config, log, creds)





