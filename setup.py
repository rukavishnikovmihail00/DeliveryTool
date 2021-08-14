import re

from setuptools import setup, find_packages
from os import path

HERE = path.abspath(path.dirname(__file__))


def readfile(*parts):
    with open(path.join(HERE, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = readfile(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string')


setup(
    name='delivery-tool-rukavishnikov',
    version=find_version('delivery_tool', '__init__.py'),
    author='Mikhail Rukavishnikov',
    author_email='rukavishnikovmihail00@yandex.ru',
    description='Delivery tool project',
    install_requires=['pyyaml>=5.3.1,<6', 'requests>=2.25.1', 'backoff>=1.10.0', 'dohq-artifactory>=0.7.574', 'docker>=5.0.0', 'docker-compose>=1.29.2'],
    package_data={
        'delivery_tool': [
            'artifactory.yaml', 'content/*', 'hosts', 'rerun-artifactory.yaml', 'config.yaml'
        ]
    },
    packages=find_packages(),
    entry_points={
        'console_scripts':
            ['delivery_tool = delivery_tool.main:main']
        }
)