"""
1. get all iPhone files (everything non-dir), that's not found in already
backed-up dir to new dir
    example path for the iPhone photos:
    "/run/user/1000/gvfs/gphoto2:host=%5Busb%3A001%2C004%5D/DCIM"
2. copy manually everything new to backup dir

This script is handling step "1.", step "2." is manual after reviewing
what's new.
:IMPORTANT:
    different image sources can have same file names but represent different 
    images. We have new file (not backed up) if:
        - new file's content hash
        - or same hash but different size (to avoid possible hash collisions)
"""
import os
import argparse
import hashlib
import shutil
from datetime import datetime


def read_cli_args():
    print('Reading CLI args')
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--iphone-dcim-dir', required=True,
        help=(
            'Example: /run/user/1000/gvfs/gphoto2\:host\=Apple_Inc._iPhone_'
            '16e1f710c0e67883b88e1dde42636e5e651b62c4/DCIM'
        )
    )
    parser.add_argument('--backed-up-files-dir', required=True)
    parser.add_argument('--new-files-dir', required=True)
    parser.add_argument('--ask-to-copy-files', action='store_true')
    return parser.parse_args()

    
def validate_cli_args(args):
    print('Validating CLI args')
    iphone_dcim_dir = args.iphone_dcim_dir
    backed_up_files_dir = args.backed_up_files_dir
    new_files_dir = args.new_files_dir
    data = [
        [iphone_dcim_dir, 'iphone DCIM dir'],
        [backed_up_files_dir, 'backed-up files dir'],
        [new_files_dir, 'new files dir']
    ]
    for t in data:
        if not os.path.isdir(t[0]):
            raise Exception('Not a dir: %s' % t[1])


def read_file_names(cur_dir, fnames):
    for fname in os.listdir(cur_dir):
        fname = os.path.join(cur_dir, fname)
        if os.path.isdir(fname):
            read_file_names(fname, fnames)
        else:
            fnames.append(fname)


def get_file_hash(abs_fname):
    block_size = 65536  # read in 64kb blocks
    hash_algo = hashlib.sha1()
    with open(abs_fname, 'rb') as fin:
        while True:
            data = fin.read(block_size)
            if not data:
                break
            hash_algo.update(data)
    
    return hash_algo.hexdigest()


def calculate_hash_per_file(abs_fnames):
    hash_data_map = {}
    for abs_fname in abs_fnames:
        file_hash = get_file_hash(abs_fname)
        item = {
            'abs_name': abs_fname,
            # 'base_name': os.path.basename(abs_fname),
            'size': os.path.getsize(abs_fname)  # in bytes
        }
        if file_hash in hash_data_map:
            print('DUPLICATE BY HASH IN SAME MASTER DIR: %s' % item)
            continue
         
        hash_data_map[file_hash] = item

    return hash_data_map 


def get_new_file_names(backed_hash_data_map, iphone_hash_data_map):
    new_fnames = []
    for iphone_hash, iphone_fdata in iphone_hash_data_map.items():
        iphone_fname = iphone_fdata['abs_name']
        if iphone_hash not in backed_hash_data_map:
            new_fnames.append(iphone_fname)
            continue
        
        backed_fdata = backed_hash_data_map[iphone_hash]
        if iphone_fdata['size'] != backed_fdata['size']:
            print('SAME HASH, DIFFERENT SIZE, iphone: %s, backed-up: %s' % 
                  (iphone_fname, backed_fdata['abs_name']))
            new_fnames.append(iphone_fname)
    
    return new_fnames


def write_new_files(new_files_dir, new_file_names):
    print('Writing to "%s"' % new_files_dir)
    os.mkdir(new_files_dir)
    for src_abs_fname in new_file_names:
        dest_abs_fname = os.path.join(
            new_files_dir,
            os.path.basename(src_abs_fname)
        )
        shutil.copy2(src_abs_fname, dest_abs_fname)


def run():
    args = read_cli_args()           
    
    validate_cli_args(args)
    iphone_dcim_dir = args.iphone_dcim_dir
    backed_up_files_dir = args.backed_up_files_dir
    print('iPhone DCIM dir: "%s"\nBacked-up files dir: "%s"' % 
          (iphone_dcim_dir, backed_up_files_dir))
    backed_up_file_names = list()
    iphone_file_names = list()
    
    print('Reading backed-up file names from: %s' % backed_up_files_dir)
    read_file_names(backed_up_files_dir, backed_up_file_names)
    print('Read backed-up file names: %s' % len(backed_up_file_names))
    print('Generating hashes per file')
    backed_hash_data_map = calculate_hash_per_file(backed_up_file_names)
    
    print('Reading iPhone file names from: %s' % iphone_dcim_dir)
    read_file_names(iphone_dcim_dir, iphone_file_names)
    print('Read iPhone file names: %s' % len(iphone_file_names))
    print('Generating hashes per file')
    iphone_hash_data_map = calculate_hash_per_file(iphone_file_names)
    new_file_names = \
        get_new_file_names(backed_hash_data_map, iphone_hash_data_map)
    print('new file names: %s' % len(new_file_names))
    if not new_file_names:
        return

    new_files_dir = args.new_files_dir
    new_files_dir = os.path.join(new_files_dir, 'new_files_%s' % datetime.now())
    yes = True
    if args.ask_to_copy_files:
        ans = input('Write new files? y/n (to "%s")\n' % new_files_dir)
        yes = ans.lower().strip() == 'y'
    
    if yes:
        write_new_files(new_files_dir, new_file_names)
    else:
        print('Will skip copying new files:\n%s' % (new_file_names,))


if __name__ == '__main__':
    run()
