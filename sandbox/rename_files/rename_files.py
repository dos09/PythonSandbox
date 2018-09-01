import time
import os
import argparse
import re
import logging

from sandbox.common.logging_utils import config_logging
from sandbox.common.input_utils import confirm
from sandbox.common.formatting import format_seconds

LOG = None


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True,
                        help='Files in that directory will be renamed')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Process files inside sub-directories')
    parser.add_argument('-regex', type=re.compile,
                        help=('Will change files, whose names match the '
                              'specified regular expression'))
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what will be modified without doing it')
    parser.add_argument('--debug', action='store_true')
    subparsers = parser.add_subparsers()
    # the below two lines will make the "change" sub-command required
    subparsers.required = True
    subparsers.dest = 'change'
    operation_parser = subparsers.add_parser('change')
    operation_group = operation_parser.add_mutually_exclusive_group(
        required=True)
    operation_group.add_argument(
        '--prefix',
        help=('Prefix the matching files with the provided string'))
    operation_group.add_argument(
        '--suffix',
        help=('Suffix the matching files with the provided string'))
    operation_group.add_argument(
        '--whole-name',
        help=('Rename the matching files with the specified string. '
              'The files per directory will have the sequential number as '
              'suffix in parenthesis'))

    args = parser.parse_args()
    config_logger(args.debug)
    return args


def config_logger(debug=False):
    global LOG
    log_level = logging.DEBUG if debug else logging.INFO
    config_logging(log_level)
    LOG = logging.getLogger(__name__)


class Worker:

    def __init__(self, dir, recursive=None, regex=None,
                 dry_run=None, prefix=None, suffix=None, whole_name=None):
        """
        :param dir: files in that dir will be renamed
        :param recursive: if True, will process subdirectories
        :param dry_run: if True, no changes will be performed
        :param prefix: will use that to prefix the matched files
        :param suffix: will use that to prefix the matched files
        :param whole_name: the whole file name will be changed to that +
        sequential number in parenthesis
        """
        self.dir = dir
        self.recursive = recursive
        self.regex = regex
        self.dry_run = dry_run
        self.prefix = prefix
        self.suffix = suffix
        self.whole_name = whole_name

        if not os.path.isdir(self.dir):
            raise Exception('%s does not exist' % self.dir)

        t = bool(self.prefix) + bool(self.suffix) + bool(self.whole_name)
        if t != 1:
            raise Exception('Can specify only one: '
                            'prefix (%s), suffix (%s), whole_name (%s)' %
                            (self.prefix, self.suffix, self.whole_name))

    def show_active_vars(self):
        lines = ['This will be used for renaming:', ]
        for k in sorted(self.__dict__.keys()):
            v = self.__dict__[k]
            if v:
                lines.append('%s: "%s"' % (k, v))
        LOG.info('\n'.join(lines))

    @staticmethod
    def from_args(args):
        return Worker(
            dir=args.dir,
            recursive=args.recursive,
            regex=args.regex,
            dry_run=args.dry_run,
            prefix=args.prefix,
            suffix=args.suffix,
            whole_name=args.whole_name)
    
def run():
    args = read_args()
    LOG.debug(args)
    worker = Worker.from_args(args)
    worker.show_active_vars()
    if not confirm():
        return
    
    start_time = time.time()
    LOG.info('Renaming files completed for %s',
             format_seconds(time.time() - start_time))
    

if __name__ == '__main__':
    run()

"""
TODO: 
- files changed per directory
- for prefix/suffix check if not already prefixed/suffixed
- save this script somewhere (repository or external drive)
"""
