import sys
import argparse
import logging
try:
    from distutils.util import strtobool
except ImportError:
    from distutils import strtobool


class ErrorParser(argparse.ArgumentParser):
    """
    on error; print help string
    """

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


class StoreDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        kv = {}
        if not isinstance(values, (list,)):
            values = (values,)
        for value in values:
            n, v = value.split('=')
            kv[n] = v
        setattr(namespace, self.dest, kv)


def cmndline_prompt(query):
    """ get a prompt from the user

    Parameters
    ----------
    query: str

    Returns
    -------

    """
    val = input("{0} [y/n]: ".format(query))
    try:
        ret = strtobool(val)
    except ValueError:
        sys.stdout.write('Please answer with a y/n\n')
        return cmndline_prompt(query)
    return ret


def setup_logger():
    """stream warnings and errors to stderr """
    root = logging.getLogger()
    root.handlers = []  # remove any existing handlers
    root.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(levelname)8s: %(module)10s: %(message)s')
    stream_handler.setFormatter(formatter)
    stream_handler.propogate = False
    root.addHandler(stream_handler)
