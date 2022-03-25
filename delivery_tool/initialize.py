import logging
import os
import sys
from argparse import ArgumentParser
from datetime import datetime

import delivery_tool


def parse():
    parser = ArgumentParser()
    parser.add_argument('--version', action='version', version=delivery_tool.__version__)
    subparsers = parser.add_subparsers(description='', dest='subparser', required=True)
    subparsers.add_parser('show', help='show info')
    subparsers.add_parser('upload', help='upload files')
    subparsers.add_parser('pack', help='pack files')
    install_parser = subparsers.add_parser('install', help='Setup option')
    install_parser.add_argument('-r', '--repository', help='add this is you need to create Generic repository', type=bool, default=False)
    args = vars(parser.parse_args())
    return args


def init_logger(name_func):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
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

    root_logger.addHandler(fh)
    root_logger.addHandler(ch)
