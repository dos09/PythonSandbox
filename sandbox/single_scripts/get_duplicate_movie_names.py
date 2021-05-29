"""
Find duplicate movies in directory (need to review manually)

For input directory with movies (can have directory nesting)
get some statistics and get list of sorted movies.
(by default will skip most non-movie files such as srt, png...)
This list has to be reviewed manually for duplicates
(movie names can have different formats)
"""
import json
import sys
import os
import logging
import argparse
from collections import namedtuple, defaultdict
import time

LOG = None

Args = namedtuple('Args', ['input_dir', 'write_to_files',
                           'output_dir', 'exclude_extensions'])


def is_ascii(str_val):
    # to be compatible with python < 3.7
    return all(ord(i) < 128 for i in str_val)


def log_time(func):

    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        seconds = time.time() - start_time
        print('Time elapsed: %s (seconds)' % round(seconds))
        return res
        
    return wrapper


@log_time
def run():
    args = read_cli()
    args = sanitize_args(args)
    init_logging()
    LOG.info('Sanitized args: %s', args)
    sort_names(args)
    sort_by_fname_and_parent_dirname(args)


def init_logging():
    h = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)8s] %(message)s',
        '%Y-%m-%d %H:%M:%S')
    h.setFormatter(formatter)
    h.setLevel(logging.INFO)
    logging.basicConfig(handlers=[h], level=logging.INFO)
    global LOG
    LOG = logging.getLogger(__name__)


def fail(err_msg=None):
    raise Exception(err_msg) 

    
def read_cli():
    args = argparse.ArgumentParser()
    args.add_argument('--input-dir', required=True,
                      help='Directory with movies')
    args.add_argument('--output-dir',
                      help='Where to write files (Used for --write-to-files)')
    args.add_argument('--write-to-files', action='store_true',
                      help='Save processing results to files')
    args.add_argument('--exclude-extensions',
                      default='srt,nfo,sub,rar,txt,idx,jpg,zip,png',
                      help='Files with those extensions are skipped')
    args = args.parse_args()
    return args


def sanitize_args(args):
    input_dir = args.input_dir
    if not os.path.isdir(input_dir):
        fail('Input dir is not existing directory')
    
    write_to_files = bool(args.write_to_files)
    output_dir = args.output_dir
    if write_to_files and output_dir:
        if not os.path.isdir(input_dir):
            fail('Output dir is not existing directory')
    
    exclude_extensions = [
        i.strip() for i in args.exclude_extensions.split(',') if i.strip()
    ]
    temp_extensions = set()
    for ext in exclude_extensions:
        if not ext.startswith('.'):
            ext = '.%s' % ext
        
        temp_extensions.add(ext)
    
    exclude_extensions = sorted(temp_extensions)
    return Args(input_dir, write_to_files, output_dir, exclude_extensions)


def sort_names(args):
    skipped_files = []
    non_skipped_files = []
    for fname in traverse_dir(args.input_dir):
        if skip_file(fname, args):
            skipped_files.append(fname)
        else:            
            non_skipped_files.append(fname)
    
    skipped_files = sorted(skipped_files)
    non_skipped_files = sorted(non_skipped_files)
    
    skipped_count = len(skipped_files)
    skipped_json = json.dumps(skipped_files, indent=4)
    non_skipped_count = len(non_skipped_files)
    non_skipped_json = json.dumps(non_skipped_files, indent=4)
    LOG.info('Skipped files (%s):\n%s', skipped_count, skipped_json)
    LOG.info('Non-skipped files (%s):\n%s', non_skipped_count, non_skipped_json)
    if args.write_to_files:
        output_dir = args.output_dir
        fname = 'skipped files (%s)' % skipped_count
        write_to_file(fname, output_dir, skipped_json)
        fname = 'non-skipped files (%s)' % non_skipped_count
        write_to_file(fname, output_dir, non_skipped_json)
        

def traverse_dir(dir_name):
    if not os.path.isdir(dir_name):
        fail('Not directory: %s' % dir_name)
        
    for fname in os.listdir(dir_name):
        fname = os.path.join(dir_name, fname)
        if os.path.isdir(fname):
            for fname in traverse_dir(fname):
                yield fname
        else:
            yield fname


def write_to_file(file_name, output_dir, data):
    if output_dir:
        file_name = os.path.join(output_dir, file_name)
    
    with open(file_name, 'w') as fout:
        fout.write(data)
        fout.write('\n')

    LOG.info('Data written to: %s', os.path.abspath(file_name))


def skip_file(fname, args):
    for ext in args.exclude_extensions:
        if fname.endswith(ext):
            return True
    
    return False


def sort_by_fname_and_parent_dirname(args):
    items = []
    non_ascii = []
    dups_by_fname = defaultdict(list)
    dups_by_parent_dir = defaultdict(list)
    for fname in traverse_dir(args.input_dir):
        if skip_file(fname, args):
            continue
        
        base_name = os.path.basename(fname)
        parent_dir = os.path.basename(os.path.dirname(fname))
        obj = {
            'file_name': base_name,
            'parent_dir': parent_dir,
            'abs_path': fname
        }
        items.append(obj)
        if not is_ascii(base_name) or not is_ascii(parent_dir):
            non_ascii.append(obj)
            
        dups_by_fname[base_name].append(fname)
        dups_by_parent_dir[parent_dir].append(fname)
        
    dups_by_fname = {
        base_name: dups
        for base_name, dups in dups_by_fname.items() if len(dups) > 1
    }
    dups_by_parent_dir = {
        parent_dir: dups
        for parent_dir, dups in dups_by_parent_dir.items() if len(dups) > 1
    }
    
    LOG.info('Files processed: %s', len(items))
    by_fname = sorted(
        '%s --- %s' % (obj['file_name'], obj['abs_path']) 
        for obj in items
    )
    by_parent_dir = sorted(
        '%s --- %s' % (obj['parent_dir'], obj['abs_path'])
        for obj in items
    )
    non_ascii = sorted(non_ascii, key=lambda x: obj['file_name'])
    by_fname = json.dumps(by_fname, indent=4)
    by_parent_dir = json.dumps(by_parent_dir, indent=4)
    non_ascii = json.dumps(non_ascii, indent=4)
    dups_by_fname = json.dumps(dups_by_fname, indent=4, sort_keys=True)
    dups_by_parent_dir = json.dumps(dups_by_parent_dir, indent=4, sort_keys=True)
    LOG.info('Sorted by base file name:\n%s', by_fname)
    LOG.info('Sorted by base parent dirname:\n%s', by_parent_dir)
    LOG.info('Non-ASCII:\n%s', non_ascii)
    LOG.info('Duplicates by base file name:\n%s', dups_by_fname)
    LOG.info('Duplicates by base parent dirname:\n%s', dups_by_parent_dir)
    if args.write_to_files:
        output_dir = args.output_dir
        fname = 'sorted by base file name'
        write_to_file(fname, output_dir, by_fname)
        fname = 'sorted by base parent dirname'
        write_to_file(fname, output_dir, by_parent_dir)
        fname = 'non-ascii'
        write_to_file(fname, output_dir, non_ascii)
        fname = 'duplicates by base file name'
        write_to_file(fname, output_dir, dups_by_fname)
        fname = 'duplicates by base parent dirname'
        write_to_file(fname, output_dir, dups_by_parent_dir)

    
if __name__ == '__main__':
    run()
