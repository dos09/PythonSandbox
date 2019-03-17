import logging
import argparse
import os

MOVIE_EXTENSIONS = ('mkv', 'avi', 'mp4')
LOG = None

def parse_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('dir')
    arg_parser.add_argument('--debug', action='store_true')
    arg_parser.add_argument('--out-file', help=('''
    File name where to write the movie names.
    If not abspath, it is considered to be in the directory with movies.
    If exists will only add the new names (if any).
    '''))
    args = arg_parser.parse_args()
    if not os.path.isdir(args.dir):
        raise Exception('Invalid dir path provided')

    return args


def init_logging(is_debug=None):
    log_format = '[%(asctime)s] [%(levelname)7s]: %(message)s'
    logging.basicConfig(level=logging.INFO if not is_debug
                        else logging.DEBUG,
                        format=log_format,
                        datefmt='%Y-%m-%d %H-%M-%S')


def movie_names_to_file(dir_name, out_file):
    names = set()
    if not os.path.isabs(out_file):
        out_file = os.path.join(dir_name, out_file)

    if os.path.isfile(out_file):
        with open(out_file) as fin:
            for line in fin:
                names.add(line.strip())

    LOG.info('Movies dir: %s, output file: %s', dir_name, out_file)
    LOG.info('Collecting movie names')
    names.update(get_movie_names(dir_name, dir_name))
    LOG.info('Collected movie names: %s', len(names))
    update_file(names, out_file)


def get_movie_names(root_dir, dir_name):
    LOG.debug('Processing dir: %s', dir_name)
    # sometimes the movie is in directory, sometimes is not
    # sometimes the directory and the file name are different so store both
    movie_names = set()
    root_dir_len = len(root_dir)
    for f in os.listdir(dir_name):
        f = os.path.join(dir_name, f)
        if os.path.isdir(f):
            movie_names.update(get_movie_names(root_dir, f))
            continue

        dot_index = f.rfind('.')
        if dot_index == -1:
            continue

        extension = f[dot_index + 1:]
        if extension not in MOVIE_EXTENSIONS:
            continue
        
        if os.path.basename(f).lower() == 'sample.%s' % extension:
            continue
        
        name = f[root_dir_len+1:]
        LOG.debug('* movie: %s', name)
        movie_names.add(name)
    
    LOG.debug('Done processing dir: %s', dir_name)
    return movie_names

def update_file(names, out_file):
    if not names:
        return
    
    LOG.info('Writing to %s', out_file)
    names = sorted(names)
    with open(out_file, 'w') as fout:
        fout.writelines('%s\n' % name for name in names)

def run():
    args = parse_args()
    init_logging(args.debug)
    global LOG
    LOG = logging.getLogger(__name__)
    movie_names_to_file(args.dir, args.out_file)


if __name__ == '__main__':
    run()

""" 
1. For windows set the console encoding to utf-8:
chcp 65001
2. Run program:
this_file.py /path/to/dir_horrors --out-file downloaded-horror-names.txt
"""
