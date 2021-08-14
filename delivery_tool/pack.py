import backoff
import requests
import shutil
import subprocess
from multiprocessing.dummy import Pool
import os
import yaml
from delivery_tool.exceptions import ApplicationException
import tempfile


tf = tempfile.TemporaryDirectory()


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def download_files(url):
    response = requests.get(url)
    response.raise_for_status()
    return requests.get(url).content


def thread_process(image):
    oci = image[image.rfind('/') + len('/'):image.rfind(':')]

    if not os.path.exists(f"{tf.name}/content/images/" + oci):
        os.mkdir(f"{tf.name}/content/images/" + oci)

    subprocess.run(['skopeo', 'copy', '--src-tls-verify=false', '--dest-shared-blob-dir', f"{tf.name}/content/layers",
                    'docker://' + image, f"oci:{tf.name}/content/images/" + oci])


def pack(config, log):
    exceptions = []
    
    os.makedirs(f"{tf.name}/content/images")
    os.mkdir(f"{tf.name}/content/layers")

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

    with open(f"{tf.name}/content/images_info.yaml", 'w') as im:
        yaml.dump(data, im)

    log.info("===== Pulling docker images =====")

    pool = Pool(4)
    threads = pool.map(thread_process, config['images'])
    pool.close()
    pool.join()

    if exceptions:
        raise ApplicationException("Some files were not downloaded:" + '\n'.join(exceptions))

    if not exceptions:
        log.info("All the files have been downloaded successfully")
        log.info("Starting to create archive")
        shutil.make_archive('ArchContent', 'zip', f"{tf.name}/content")
        log.info("Archive has been created")
