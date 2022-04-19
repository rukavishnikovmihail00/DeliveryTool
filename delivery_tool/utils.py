import backoff
import requests
import yaml

from delivery_tool.exceptions import ApplicationException


def parse_file(filename):
    try:
        with open(filename, 'r') as f:
            config = yaml.load(f, Loader=yaml.Loader)
    except FileNotFoundError as e:
        raise ApplicationException(f"File {filename} hasn`t been found") from e
    return config


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def download_files(url):
    response = requests.get(url)
    response.raise_for_status()
    return requests.get(url).content
