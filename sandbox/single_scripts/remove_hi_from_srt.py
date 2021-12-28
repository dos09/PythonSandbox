"""
input: .srt file with HI (hearing impaired) or dir with HI .srt files
output: dir with .srt file(s) with removed HI (most of it)
    dir name: srt_hi_removed_<timestamp>

always check "in" and "out" srt files using diff checker like meld
to check if the conversion was ok and no other data was removed
"""

import argparse
import os
from datetime import datetime
import re
import json

# 00:00:06,006 --> 00:00:11,750
TIME_MARKER_REGEX = re.compile('^\d[\d:,-> ]+$')
# - [cheering]
# [applauding]
HI_REGEX = re.compile(r'^(\s*-\s*)?\[.+\]$')


def read_cli():
    p = argparse.ArgumentParser(
        description='Remove hearing impaired (HI) from .srt files'
    )
    p.add_argument('--source', help='single .srt file or dir with .srt files')
    args = p.parse_args()
    return args.source


def gen_out_dir_name(dir_name):
    dir_name = os.path.join(dir_name, 'out_%s' % datetime.now())
    os.mkdir(dir_name)
    print('Will save HI removed .srt files in "%s"' % dir_name)
    return dir_name


def is_srt_file(fname):
    return os.path.isfile(fname) and fname.endswith('.srt')


def read_blocks(fname):

    def init_new_block(block_id):
        return {
            'id': str(block_id),  # for debugging
            'time': None,
            'lines': []
        }

    print('Reading blocks')
    cur_block = init_new_block(1)
    blocks = []
    next_block_id = 2
    # skip BOM, otherwise the first line "1" is read as "\ufeff1"
    with open(fname, encoding='utf-8-sig') as fin:
        first_line = fin.readline().strip()
        if first_line != '1':
            raise Exception('Invalid start of file "%s", first_line = "%s"' % 
                            (fname, first_line))
        # the loop starts from the second line
        for line in fin:
            line = line.rstrip('\n')
            if line.strip() == str(next_block_id):
                if not cur_block['time'] or not cur_block['lines']:
                    raise Exception('Invalid block %s' % cur_block)

                blocks.append(cur_block)
                cur_block = init_new_block(next_block_id)
                next_block_id += 1
            elif TIME_MARKER_REGEX.match(line) and not cur_block['time']:
                cur_block['time'] = line
            else:
                cur_block['lines'].append(line)
        
        if cur_block['time'] is not None:
            blocks.append(cur_block)
    
    print('Blocks read: %s' % len(blocks))
    return blocks


def remove_hi_from_blocks(blocks):
    print('Removing HI from blocks')
    i = 0
    modified_blocks = 0
    while i < len(blocks):
        block = blocks[i]
        lines = block['lines']
        if not lines:
            raise Exception('No lines (text) for block: %s' % block)
        
        new_lines = []
        for line in lines:
            if HI_REGEX.match(line):
                continue
            
            new_lines.append(line)  # include empty line separators
        
        if not new_lines or len(new_lines) == 1 and new_lines[0].strip() == '':
            del blocks[i]
        else:
            i += 1
            if len(lines) != len(new_lines):
                modified_blocks += 1
                block['lines'] = new_lines
        
    return modified_blocks
    

def remove_hi(fname, out_dir):
    print('Removing HI from file: "%s"' % fname)
    stat = {
        'blocks before': None,
        'blocks after': None,
        'blocks removed': None,
        'blocks modified': None
    }
    blocks = read_blocks(fname)
    stat['blocks before'] = len(blocks)
    stat['blocks modified'] = remove_hi_from_blocks(blocks)
    stat['blocks after'] = len(blocks)
    stat['blocks removed'] = stat['blocks before'] - stat['blocks after']
    out_fname = os.path.join(out_dir, os.path.basename(fname))
    print('Writing to output file %s' % out_fname)
    block_id = 1
    with open(out_fname, 'w') as fout:
        # some of the blocks might be removed so block['id'] is not reliable
        for block in blocks: 
            lines = [str(block_id), block['time']]
            lines.extend(block['lines'])
            fout.writelines('%s\n' % line for line in lines)
            block_id += 1
    
    return stat


def run():
    source = read_cli()
    stats = {}
    if os.path.isdir(source):
        out_dir = gen_out_dir_name(source)
        for fname in os.listdir(source):
            fname = os.path.join(source, fname)
            if not is_srt_file(fname):
                continue
            
            stats[fname] = remove_hi(fname, out_dir)
            
    elif is_srt_file(source):
        out_dir = gen_out_dir_name(os.path.dirname(source))
        stats[source] = remove_hi(source, out_dir)
    
    print('stats:\n%s' % json.dumps(stats, indent=4))


if __name__ == '__main__':
    run()
