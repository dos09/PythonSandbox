import sys
import os
import logging
import time
import argparse

LOG = None


def init_logging():
    h = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s UTC [%(levelname)8s] %(message)s',
        '%Y-%m-%d %H:%M:%S')
    formatter.converter = time.gmtime
    h.setFormatter(formatter)
    h.setLevel(logging.INFO)
    logging.basicConfig(handlers=[h], level=logging.INFO)


def load_file_names(dir_name, file_names):
    for item_name in os.listdir(dir_name):
        item_name = os.path.join(dir_name, item_name)
        if os.path.isfile(item_name):
            file_names.add(os.path.basename(item_name))
        elif os.path.isdir(item_name):
            load_file_names(item_name, file_names)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir-name', required=True)
    parser.add_argument('--out-file', required=True)
    args = parser.parse_args()
    dir_name = args.dir_name

    init_logging()
    global LOG
    LOG = logging.getLogger(__name__)
    if not os.path.isdir(dir_name):
        raise Exception('%s not existing dir' % dir_name)

    LOG.info('Processing dir: %s', dir_name)
    file_names = set()
    load_file_names(dir_name, file_names)
    LOG.info('File names loaded: %s', len(file_names))
    with open(args.out_file, 'w') as fout:
        for fname in sorted(file_names):
            fout.write('%s\n' % fname)

    LOG.info('Output file %s', os.path.abspath(args.out_file))

    # LOG.info('File names: %s', sorted(file_names))


if __name__ == '__main__':
    run()
