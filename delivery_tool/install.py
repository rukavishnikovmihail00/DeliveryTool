import logging
import subprocess
import tempfile
import zipfile

import yaml

from delivery_tool.artifactory import create_repo
from delivery_tool.utils import parse_file
from delivery_tool.variables import PLAYBOOK_NAME, ARTIFACTORY_YAML_NAME

log = logging.getLogger(__name__)


def install(creds, repository):
    config = parse_file(ARTIFACTORY_YAML_NAME)
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

    playbook_path = f"{tf.name}/ansible/{PLAYBOOK_NAME}"
    hosts_path = f"{tf.name}/ansible/hosts"

    log.info(f"Running ansible playbook {PLAYBOOK_NAME}")
    log.info(f"Hosts path is {hosts_path}")

    subprocess.run(['ansible-playbook', '-i', hosts_path, playbook_path])

    if repository:
        create_repo(config, creds)





