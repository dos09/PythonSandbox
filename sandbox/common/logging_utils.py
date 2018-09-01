# TODO: modify so it can log in file
import sys
import logging

def config_logging(log_level=logging.INFO, multi_processing=False):
    h = logging.StreamHandler(stream=sys.stdout)
    formatter = (get_debug_formatter(multi_processing)
                 if log_level == logging.DEBUG else
                 get_non_debug_formatter(multi_processing))
    h.setFormatter(formatter)
    logging.basicConfig(level=log_level, handlers=[h, ])


def get_debug_formatter(multi_processing=False):
    datefmt = '%Y-%m-%d %H:%M:%S'
    if not multi_processing:
        formatter = logging.Formatter(
            fmt=('%(asctime)s - %(filename)s - %(lineno)d - '
                 '[%(levelname)8s] - %(message)s'),
            datefmt=datefmt)
    else:
        formatter = logging.Formatter(
            fmt=('%(asctime)s - %(filename)s - %(lineno)d - '
                 '[%(levelname)8s] (%(process)d) - %(message)s'),
            datefmt=datefmt)

    return formatter


def get_non_debug_formatter(multi_processing=False):
    datefmt = '%Y-%m-%d %H:%M:%S'
    if not multi_processing:
        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)8s] - %(message)s',
            datefmt=datefmt)
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)8s] (%(process)d) - %(message)s',
            datefmt=datefmt)

    return formatter

if __name__ == '__main__':
    config_logging(log_level=logging.DEBUG, multi_processing=False)
    log = logging.getLogger(__name__)
    log.debug('debug msg')
    log.info('info msg')
    log.warning('warning msg')
    log.critical('critical msg')
    log.error('error msg')
