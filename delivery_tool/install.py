import logging
import subprocess
import tempfile
import zipfile

import yaml
from dohq_artifactory import RepositoryLocal

from delivery_tool.artifactory import create_repo
from delivery_tool.utils import parse_file
from delivery_tool.variables import PLAYBOOK_NAME, ARTIFACTORY_YAML_NAME

log = logging.getLogger(__name__)


def install(is_create_repository):
    log.info("### Execute install function ###")
    config = parse_file(ARTIFACTORY_YAML_NAME)
    tf = tempfile.TemporaryDirectory()
    url = config['url']

    data = {'artifactory_home': config['home_dir'],
            'url': url[:url.rfind('/')],
            'lic_path': config['lic_path'],
            'docker_name': config['repositories']['docker'],
            'port': config['docker_registry'][config['docker_registry'].rfind(':') + len(':'):],
            'ip': url[url.find('/') + len('//'):url.rfind(':')]}

    zipfile.ZipFile('delivery-tool-rukavishnikov-0.1.0.pyz').extractall(tf.name)
    zipfile.ZipFile(f"{tf.name}/delivery_tool/ansible.zip").extractall(tf.name)

    with open(f"{tf.name}/ansible/vars.yaml", 'w') as vars_file:  # tf path
        yaml.dump(data, vars_file)

    log.info(f"Running ansible playbook {PLAYBOOK_NAME}")
    subprocess.run(['ansible-playbook', '-i', f"{tf.name}/ansible/hosts", f"{tf.name}/ansible/{PLAYBOOK_NAME}"])

    if is_create_repository:
        log.info("### Create repositories ###")
        create_repo(config['url'], config['repositories']['files'], RepositoryLocal.GENERIC)
        log.info("Create docker repositories")
        create_repo(config['url'], config['repositories']['docker'], RepositoryLocal.DOCKER)



