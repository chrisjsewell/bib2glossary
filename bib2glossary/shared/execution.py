import os
import sys
import argparse
import logging
import json

from six import ensure_str

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


def read_param2field(options):
    """read json path to get param2field dict"""
    param2field = {}
    if options.get('param2field', False):
        jsonpath = os.path.abspath(options.get('param2field'))
        if not os.path.exists(jsonpath):
            raise IOError('json path does not exist: {}'.format(jsonpath))
        with open(jsonpath) as file_obj:
            jsondata = json.load(file_obj)
        # validate
        assert isinstance(jsondata, dict)
        for key, val in jsondata.items():
            param2field[ensure_str(key)] = ensure_str(val)
    return param2field


def run_tex_to_bib_shared(sys_args, glossary_type, convert_func, logger):
    """ glossary type should be newglossaryentry or newacronym """

    infile_ext = "tex"

    parser = ErrorParser(
        description='convert a tex file containing \\{0} definitions '
        'to a bibtex file'.format(glossary_type),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("fpath", type=str,
                        help='{} file path'.format(infile_ext),
                        metavar='filepath')
    parser.add_argument("-type", "--entry-type", type=str, metavar='str',
                        default="misc",
                        help="bibtex entry type to use")
    parser.add_argument("-p2f", "--param2field", type=str, metavar='filepath',
                        help="path to a json file defining mapping of"
                        "glossaries parameters to bibtex fields "
                        "(will override defaults)")

    args = parser.parse_args(sys_args)
    options = vars(args)

    setup_logger()

    fpath = os.path.abspath(options.pop('fpath'))
    if not os.path.exists(fpath):
        logger.critical(IOError('input path does not exist: {}'.format(fpath)))
        return ''

    param2field = {}
    try:
        param2field = read_param2field(options)
    except Exception as err:
        logger.critical(err)
        return ''

    with open(fpath) as file_obj:
        in_str = file_obj.read()

    out_str = convert_func(in_str,
                           entry_type=options.get("entry_type"),
                           param2field=param2field,
                           warning_handler=logger.warn)

    if not out_str:
        logger.warn("No '{0}' definitions found".format(glossary_type))

    return out_str


def run_bib_to_tex_shared(sys_args, glossary_type, convert_func, logger):
    """ glossary type should be newglossaryentry or newacronym """

    infile_ext = "bib"

    parser = ErrorParser(
        description='convert a bibtex file to a tex file '
        'containing \\{0} definitions'.format(glossary_type),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("fpath", type=str,
                        help='{} file path'.format(infile_ext),
                        metavar='filepath')
    parser.add_argument("-type", "--entry-type", type=str, metavar='str',
                        help="filter by single bibtex entry type")
    parser.add_argument("-p2f", "--param2field", type=str, metavar='filepath',
                        help="path to a json file defining mapping of"
                        "glossaries parameters to bibtex fields "
                        "(will override defaults)")

    args = parser.parse_args(sys_args)
    options = vars(args)

    setup_logger()

    fpath = os.path.abspath(options.pop('fpath'))
    if not os.path.exists(fpath):
        logger.critical(IOError('input path does not exist: {}'.format(fpath)))
        return ''

    try:
        param2field = read_param2field(options)
    except Exception as err:
        logger.critical(err)
        return ''

    with open(fpath) as file_obj:
        in_str = file_obj.read()

    try:
        out_str_list = convert_func(in_str,
                                    entry_type=options.get('entry_type', None),
                                    param2field=param2field)
    except Exception as err:
        logger.critical(err)
        return ''

    if not out_str_list:
        logger.warn("No bib entries found")

    out_str_list.insert(0, "% Created by bib2glossary")

    return "\n".join(out_str_list) + "\n"
