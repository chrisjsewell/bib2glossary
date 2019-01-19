import logging
import os
import argparse
from collections import deque
import json

import bibtexparser
from TexSoup import TexSoup
from TexSoup.utils import TokenWithPosition
from TexSoup.data import RArg, OArg
from six import ensure_str

from bib2glossary.utils import ErrorParser, StoreDict, setup_logger

logger = logging.getLogger(__name__)

_DEFAULTP2F = (("abbreviation", "shorttitle"),
               ("longname", "journal"),
               ("description", "abstract"),
               ("plural", "series"),
               ("longplural", "volume"),
               ("firstplural", "edition"),
               )


def bib_to_tex(text_str, entry_type='misc',
               param2field=None):
    """create a list of tex acronym strings

    Parameters
    ----------
    text_str: str
        the .bib file text
    entry_type: None or str
        if given, filter by entry_type
    param2field: None or dict
        mapping of abbreviation parameter to bib field

    Returns
    -------
    acronyms: a list of string

    """
    param2field_default = dict(_DEFAULTP2F)
    if param2field is not None:
        param2field_default.update(param2field)
    param2field = param2field_default.copy()
    assert "abbreviation" in param2field
    assert "longname" in param2field

    abbrev_field = param2field.pop("abbreviation")
    name_field = param2field.pop("longname")

    parser = bibtexparser.bparser.BibTexParser()
    bib = parser.parse(text_str)
    # TODO doesn't appear to check for key duplication
    entries = bib.get_entry_dict()

    acronyms = []
    for key in sorted(entries.keys()):

        fields = entries.get(key)

        if entry_type and entry_type != (fields.get('ENTRYTYPE', '')):
            continue

        if abbrev_field not in fields:
            logger.warn("Skipping {0}: No {1} key found".format(
                key, abbrev_field))
            continue
        if name_field not in fields:
            logger.warn(
                "Skipping {0}: No {1} key found".format(key, name_field))
            continue

        body = "{{{key}}}{{{abbreviation}}}{{{name}}}".format(
            key=key,
            abbreviation=fields[abbrev_field],
            name=fields[name_field])
        options = []
        for param, field in param2field.items():
            if field in fields:
                options.append("{0}={{{1}}}".format(param, fields[field]))
        if options:
            body = "[" + ",".join(options) + "]" + body

        acronyms.append("\\newacronym"+body)

    return acronyms


def _clean_str(string):
    return " ".join(string.splitlines()).strip()


def create_error_msg(msg, node=None, row=None):
    text = msg.strip()
    if row is not None:
        text = "(row {}) ".format(row) + text
    if node is not None:
        text = text + ": {}".format(node)
    return text


def read_required(rarg):
    if not isinstance(rarg, RArg):
        raise ValueError(
            "expected {} to be a required argument".format(type(rarg)))
    return rarg.value


def read_parameters(expressions):
    """read the parameters from a TexSoup expression"""
    expressions = deque(expressions)
    param_name = None
    params = {}
    errors = []
    while expressions:
        expr = expressions.popleft()
        if isinstance(expr, TokenWithPosition):
            # TODO is this the best way to extract parameter name?
            param_name = expr.text.replace(",", "").replace("=", "").strip()
        elif isinstance(expr, RArg):
            if param_name is None:
                errors.append(
                    "expected expression "
                    "'{}' to precede a parameter name".format(expr))
                break
            if param_name in params:
                errors.append(
                    "parameter '{}' already defined".format(param_name))
            else:
                params[param_name] = expr.value
            param_name = None
        else:
            errors.append(
                "expected expression '{}' ".format(expr) +
                "to be a parameter name or required argument")
            break

    if param_name is not None:
        pass  # allowed since last expr may be new line
        # errors.append(
        #     "parameter '{}' is not assigned a value".format(param_name))

    return params, errors


def raise_IOError(msg):
    raise IOError


def tex_to_dict(text_str, entry_type='misc',
                param2field=None, warning_handler=None):
    """create a dictionary of bib entries

    Parameters
    ----------
    text_str: str
        the .tex file string
    entry_type: str
        the entry type for each bib item
    param2field: None or dict
        mapping of abbreviation parameter to bib field
    warning_handler: func
        function taking a warning message (default is to raise IOError)

    Returns
    -------
    entries: dict {<key>: {<field>: <value>, ...}}
    duplicates: dict {<key>: [row, ...]}

    """
    if warning_handler is None:
        warning_handler = raise_IOError

    param2field_default = dict(_DEFAULTP2F)
    if param2field is not None:
        param2field_default.update(param2field)
    param2field = param2field_default.copy()
    assert "abbreviation" in param2field
    assert "longname" in param2field

    abbrev_field = param2field.pop("abbreviation")
    name_field = param2field.pop("longname")

    entries = []
    keys = []
    duplicates = {}

    latex_tree = TexSoup(text_str)

    for acronym in latex_tree.find_all("newacronym"):

        row = None  # TODO get first row (for error reporting)
        arguments = list(acronym.args)
        entry = {'ENTRYTYPE': entry_type}

        if len(arguments) < 3:
            msg = create_error_msg(
                "could not parse acronym (too few arguments)", acronym, row)
            warning_handler(msg)
            continue
        if len(arguments) > 4:
            msg = create_error_msg(
                "could not parse acronym (too many arguments)", acronym, row)
            warning_handler(msg)
            continue

        key = read_required(arguments[-3])
        if key in keys:
            duplicates[key] = duplicates.get(key, []) + [row]
            continue

        entry['ID'] = key
        entry[abbrev_field] = read_required(arguments[-2])
        entry[name_field] = read_required(arguments[-1])

        if len(arguments) == 4:
            opts = arguments[0]
            if not isinstance(opts, OArg):
                msg = create_error_msg(
                    "expected first argument to be 'optional",
                    acronym, row)
                warning_handler(msg)
                continue
            opt_params, errors = read_parameters(opts.exprs)
            for error in errors:
                msg = create_error_msg(
                    "error reading 'optional' block: {}".format(error),
                    acronym, row)
                warning_handler(msg)

            for opt_name, opt_value in opt_params.items():
                if opt_name not in param2field:
                    warning_handler(
                        "option '{0}' in key '{1}' not recognised".format(
                            opt_name, key))
                    continue
                if param2field[opt_name] in entry:
                    warning_handler(
                        "duplicate parameter '{0}' in key '{1}'".format(
                            opt_name, key))
                    continue
                entry[param2field[opt_name]] = opt_value

        entries.append(entry)

    return entries, duplicates


def duplicates_msg(duplicates):
    """ handle duplicates
    """
    dupes = []
    for key, rows in duplicates.items():
        row_str = ", ".join([str(row) for row in rows if row is not None])
        if row_str:
            dupes.append("{0} (rows: {1})".format(key, row_str))
        else:
            dupes.append(str(key))
    msg = "Duplicate keys found: " + ", ".join(dupes)

    return msg


def tex_to_bib(text_str, entry_type="misc",
               param2field=_DEFAULTP2F, warning_handler=None):
    """create a bib file string

    Parameters
    ----------
    text_str: str
        the .tex file string
    entry_type: str
        the entry type for each bib item
    param2field: tuple
        mapping of abbreviation parameter to bib field
    warning_handler: func
        function taking a warning message (default is to raise IOError)

    Returns
    -------
    bib_file: str

    """
    if warning_handler is None:
        warning_handler = raise_IOError

    entries, duplicates = tex_to_dict(text_str,
                                      entry_type=entry_type,
                                      param2field=param2field,
                                      warning_handler=warning_handler)

    if duplicates:
        msg = duplicates_msg(duplicates)
        warning_handler(msg)

    bib_database = bibtexparser.bibdatabase.BibDatabase()
    bib_database.entries = entries

    writer = bibtexparser.bwriter.BibTexWriter()
    writer.contents = ['comments', 'entries']
    writer.indent = '  '
    writer.order_entries_by = ('ENTRYTYPE', 'author', 'year')
    bibtex_str = bibtexparser.dumps(bib_database, writer)

    return bibtex_str


def get_param2field(options):
    """read json path to get param2field dict"""
    param2field = {}
    if options.get('param2field', False):
        jpath = os.path.abspath(options.get('param2field'))
        if not os.path.exists(jpath):
            raise IOError('json path does not exist: {}'.format(jpath))
        with open(jpath) as file_obj:
            jdata = json.load(file_obj)
        # validate
        assert isinstance(jdata, dict)
        for key, val in jdata.items():
            param2field[ensure_str(key)] = ensure_str(val)
    return param2field


def run_tex_to_bib(sys_args):

    infile_ext = "tex"

    parser = ErrorParser(
        description='convert a tex file containing \\newacronym definitions '
        'to a bibtex file',
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
        param2field = get_param2field(options)
    except Exception as err:
        logger.critical(err)
        return ''

    with open(fpath) as file_obj:
        in_str = file_obj.read()

    out_str = tex_to_bib(in_str,
                         entry_type=options.get("entry_type"),
                         param2field=param2field,
                         warning_handler=logger.warn)

    if not out_str:
        logger.warn("No acronym definitions found")

    return out_str


def run_bib_to_tex(sys_args):

    infile_ext = "bib"

    parser = ErrorParser(
        description='convert a bibtex file to a tex file '
        'containing \\newacronym definitions',
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
        param2field = get_param2field(options)
    except Exception as err:
        logger.critical(err)
        return ''

    with open(fpath) as file_obj:
        in_str = file_obj.read()

    try:
        out_str_list = bib_to_tex(in_str,
                                  entry_type=options.get('entry_type', None),
                                  param2field=param2field)
    except Exception as err:
        logger.critical(err)
        return ''

    if not out_str_list:
        logger.warn("No bib entries found")

    out_str_list.insert(0, "% Created by bib2glossary")

    return "\n".join(out_str_list) + "\n"
