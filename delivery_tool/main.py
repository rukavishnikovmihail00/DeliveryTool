import logging
import sys

from delivery_tool.exceptions import ApplicationException
from delivery_tool.initialize import parse, init_logger
from delivery_tool.install import install
from delivery_tool.pack import pack
from delivery_tool.show import show
from delivery_tool.upload import upload

log = logging.getLogger(__name__)


def main():
    try:
        args = parse()
        init_logger(args['subparser'])
        
        log.info('### Start Delivery Tool ###')
        if args['subparser'] == 'show':
            show()
        if args['subparser'] == 'upload':
            upload()
        if args['subparser'] == 'pack':
            pack()
        if args['subparser'] == 'install':
            install(args['repository'])

    except ApplicationException as e:
        log.error(e)
        sys.exit(1)
    except Exception:
        log.exception('### Something went wrong ###')
        sys.exit(2)


if __name__ == '__main__':
    main()

