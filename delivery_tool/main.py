import logging
import os
import sys
from argparse import ArgumentParser
from datetime import datetime

import yaml

import delivery_tool
from delivery_tool.exceptions import ApplicationException
from delivery_tool.install import install
from delivery_tool.pack import pack
from delivery_tool.show import show
from delivery_tool.upload import upload


def parse():
    parser = ArgumentParser()
    parser.add_argument('--version', action='version', version=delivery_tool.__version__)
    subparsers = parser.add_subparsers(description='', dest='subparser', required=True)
    show_parser = subparsers.add_parser('show', help='show info')
    upload_parser = subparsers.add_parser('upload', help='upload files')
    pack_parser = subparsers.add_parser('pack', help='pack files')
    install_parser = subparsers.add_parser('install', help='Setup option')
    install_parser.add_argument('-r', '--repository', help='add this is you need to create Generic repository', type=bool, default=False)
    args = vars(parser.parse_args())
    return args


def parse_file(yaml_file):
    try:
        with open(yaml_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.Loader)
    except FileNotFoundError as e:
        raise ApplicationException("File named " + yaml_file + " hasn`t been found") from e
    return config


def init_logger(log, name_func):
    log.setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s | %(levelname)s]: %(message)s')

    if not os.path.exists('logs'):
        os.mkdir('logs')
       
    filename = f"logs/delivery-tool-{name_func}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"

    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.INFO)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)


def main():
    log = logging.getLogger()
    try:
        args = parse()
        
        init_logger(log, args['subparser'])
        
        log.info('=========== PROCESS INFORMATION ===========')

        if args['subparser'] == 'show':
            creds = {'login': os.getenv('ARTIFACTORY_LOG'), 'password': os.getenv('ARTIFACTORY_PASS')}
            config = parse_file('artifactory.yaml')
            show(config, creds, log)
        if args['subparser'] == 'upload':
            config = parse_file('artifactory.yaml')
            creds = {'login': os.getenv('ARTIFACTORY_LOG'), 'password': os.getenv('ARTIFACTORY_PASS')}
            upload(config, 'ArchContent.zip', log, creds)
        if args['subparser'] == 'pack':
            config = parse_file('config.yaml')
            pack(config, log)
        if args['subparser'] == 'install':
            if args['repository']:
                rep = True
            else:
                rep = False
            config = parse_file('artifactory.yaml')
            creds = {'login': os.getenv('ARTIFACTORY_LOG'), 'password': os.getenv('ARTIFACTORY_PASS')}
            install(log, 'create.yaml', config, creds, rep)

    except ApplicationException as e:
        log.error(e)
        sys.exit(1)

    except Exception:
        log.exception('Something went wrong')
        sys.exit(2)


if __name__ == '__main__':
    main()

