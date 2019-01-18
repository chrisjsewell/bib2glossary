import sys
import argparse
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