import logging
import os
import shutil
import subprocess
import tempfile
from multiprocessing.dummy import Pool

import requests
import yaml

from delivery_tool.exceptions import ApplicationException
from delivery_tool.utils import parse_file, download_files
from delivery_tool.variables import CONFIG_YAML_NAME

tf = tempfile.TemporaryDirectory()
log = logging.getLogger(__name__)


def thread_process(image):
    oci = image[image.rfind('/') + len('/'):image.rfind(':')]

    if not os.path.exists(f"{tf.name}/content/images/" + oci):
        os.mkdir(f"{tf.name}/content/images/" + oci)

    subprocess.run(['skopeo', 'copy', '--src-tls-verify=false', '--dest-shared-blob-dir', f"{tf.name}/content/layers",
                    'docker://' + image, f"oci:{tf.name}/content/images/" + oci])


def pack():
    log.info("### Execute pack function ###")
    config = parse_file(CONFIG_YAML_NAME)
    
    os.makedirs(f"{tf.name}/content/images")
    os.mkdir(f"{tf.name}/content/layers")

    exceptions = []
    for el in config['files']:
        log.info(el)
        s = el.rfind('/')
        try:
            r = download_files(el)
            with open(f"{tf.name}/content" + el[s:], 'wb') as f:
                f.write(r)
        except requests.exceptions.RequestException as e:
            exceptions.append(e)

    data = {'images': []}
    for el in config['images']:
        data['images'].append(el)

    with open(f"{tf.name}/content/images_info.yaml", 'w') as images_info:
        yaml.dump(data, images_info)

    log.info("### Pull docker images ###")
    pool = Pool(4)
    threads = pool.map(thread_process, config['images'])
    pool.close()
    pool.join()

    if exceptions:
        raise ApplicationException("Some files were not downloaded:" + '\n'.join(exceptions))
    else:
        log.info("All the files have been downloaded successfully")
        log.info("Create archive")
        shutil.make_archive('ArchContent', 'zip', f"{tf.name}/content")
        log.info("Archive has been created")
