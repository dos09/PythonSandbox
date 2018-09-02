import time
import os
import argparse
import re
import logging

from sandbox.common.logging_utils import config_logging
from sandbox.common.input_utils import confirm
from sandbox.common.formatting import format_seconds

LOG = logging.getLogger(__name__)


class RenameFilesException(Exception):
    pass


def get_regex(pattern=None):
    if pattern and isinstance(pattern, str):
        try:
            return re.compile(pattern)
        except Exception:
            msg = 'Can not create regular expression from "%s"' % pattern
            raise RenameFilesException(msg)

    return None


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required=True,
                        help='Files in that directory will be renamed')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Process files inside sub-directories')
    parser.add_argument('--regex', type=get_regex,
                        help=('Will change only files, whose names match the '
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
                 dry_run=None, prefix=None, suffix=None):
        """
        :param dir: files in that dir will be renamed
        :param recursive: if True, will process subdirectories
        :param regex: if provided, the file names must match the regex to be
        renamed
        :param dry_run: if True, no changes will be performed
        :param prefix: will use that to prefix the matched files
        :param suffix: will use that to prefix the matched files
        """
        self.dir = dir
        self.recursive = recursive
        self.regex = regex
        self.dry_run = dry_run
        self.prefix = prefix
        self.suffix = suffix

        self.count_dirs_processed = 0
        self.count_files_changed = 0

        if not os.path.isdir(self.dir):
            raise RenameFilesException('%s is not directory' % self.dir)

        if (bool(self.prefix) + bool(self.suffix)) != 1:
            raise RenameFilesException('Can specify only one: '
                                       'prefix (%s), suffix (%s)' %
                                       (self.prefix, self.suffix))

        if self.prefix:
            self.rename_file = self._rename_using_prefix
        elif self.suffix:
            self.rename_file = self._rename_using_suffix
        else:
            raise RenameFilesException('hohoho')

    def _rename_using_prefix(self, fname):
        """
        :return bool: True if the file name was changed, False otherwise
        """

        if not os.path.isabs(fname):
            raise Exception('Not absolute path')

        dir_name = os.path.dirname(fname)
        old_file_name = os.path.basename(fname)
        if old_file_name.startswith(self.prefix):
            LOG.debug('Already prefixed: %s', fname)
            return False

        if self.regex and not self.regex.search(old_file_name):
            LOG.debug('File %s does not match the provided regex',
                      old_file_name)
            return False

        new_file_name = '%s%s' % (self.prefix, old_file_name)
        msg = 'renaming "%s" -> "%s"' % (old_file_name, new_file_name)
        if self.dry_run:
            LOG.info('(dry run) %s', msg)
            return False

        LOG.debug(msg)
        os.rename(fname, os.path.join(dir_name, new_file_name))
        return True

    def _rename_using_suffix(self, fname):
        """
        :return bool: True if the file name was changed, False otherwise
        """

        if not os.path.isabs(fname):
            raise Exception('Not absolute path')

        dir_name = os.path.dirname(fname)
        old_file_name = os.path.basename(fname)

        if self.regex and not self.regex.search(old_file_name):
            LOG.debug('File %s does not match the provided regex',
                      old_file_name)
            return False

        file_parts = old_file_name.rsplit('.', 1)
        if len(file_parts) == 1:
            file_parts.append('')

        if file_parts[0].endswith(self.suffix):
            LOG.debug('Already suffixed: %s', fname)
            return False

        if file_parts[1]:
            file_parts[1] = '.%s' % file_parts[1]

        new_file_name = ('%s%s%s' %
                         (file_parts[0], self.suffix, file_parts[1]))

        msg = 'renaming "%s" -> "%s"' % (old_file_name, new_file_name)
        if self.dry_run:
            LOG.info('(dry run) %s', msg)
            return False

        LOG.debug(msg)

        os.rename(fname, os.path.join(dir_name, new_file_name))
        return True

    def show_active_vars(self):
        lines = ['This will be used for renaming:', ]
        for k in sorted(self.__dict__.keys()):
            v = self.__dict__[k]
            if v and k != 'rename_file':
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
            suffix=args.suffix)

    def process_files(self, dirname):
        LOG.info('Processing %s', dirname)
        self.count_dirs_processed += 1
        dirs_to_process = []
        dirname = os.path.abspath(dirname)
        count_cur_dir_changed_files = 0
        for item in os.listdir(dirname):
            item = os.path.join(dirname, item)
            if os.path.isdir(item):
                dirs_to_process.append(item)
            else:
                changed = self.rename_file(item)  # changed = True/False
                self.count_files_changed += changed
                count_cur_dir_changed_files += changed

        LOG.info('Files changed in %s: %s',
                 dirname, count_cur_dir_changed_files)

        for _dirname in dirs_to_process:
            if self.recursive:
                self.process_files(_dirname)
            else:
                LOG.debug('Skipping directory %s', _dirname)

    def run(self):
        self.process_files(self.dir)


def _run():
    args = read_args()
    LOG.debug(args)
    worker = Worker.from_args(args)
    worker.show_active_vars()
    if not confirm():
        return
    start_time = time.time()
    worker.run()
    LOG.info('Directories processed: %s', worker.count_dirs_processed)
    LOG.info('Files changed: %s', worker.count_files_changed)
    LOG.info('Renaming files completed for %s',
             format_seconds(time.time() - start_time))


def run():
    try:
        _run()
    except RenameFilesException as ex:
        LOG.error(ex)


if __name__ == '__main__':
    run()
