from collections import deque

import bibtexparser
from TexSoup.utils import TokenWithPosition
from TexSoup.data import RArg, OArg, TexNode


def raise_IOError(msg):
    raise IOError


def clean_str(string):
    """ remove linebreaks from string """
    return " ".join(string.splitlines()).strip()


def create_msg_error(msg, node=None, row=None):
    """create error message, optionally including TexNode and row"""
    text = msg.strip()
    if row is not None:
        text = "(row {}) ".format(row) + text
    if isinstance(node, TexNode):
        text = text + ": {}".format(node.name)
    return text


def create_msg_duplicates(duplicates):
    """ handle duplicates

    Parameters
    ----------
    duplicates: dict
        {key: list of rows}
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


def write_bib(entries):
    bib_database = bibtexparser.bibdatabase.BibDatabase()
    bib_database.entries = entries

    writer = bibtexparser.bwriter.BibTexWriter()
    writer.contents = ['comments', 'entries']
    writer.indent = '  '
    writer.order_entries_by = ('ENTRYTYPE', 'author', 'year')
    bibtex_str = bibtexparser.dumps(bib_database, writer)
    return bibtex_str


def parse_bib(text_str):
    parser = bibtexparser.bparser.BibTexParser()
    bib = parser.parse(text_str)
    # TODO doesn't appear to check for key duplication
    entries = bib.get_entry_dict()
    return entries


def extract_required_val(rarg):
    """extract the value of a TexSoup RArg"""
    if not isinstance(rarg, RArg):
        raise ValueError(
            "expected {} to be a required argument".format(type(rarg)))
    return rarg.value


def _extract_parameters(texsoup_exprs):
    """extract the parameters from a TexSoup expression list"""
    expressions = deque(texsoup_exprs)
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


def extract_parameters(argument):
    """extract parameters from a TexSoup OArg or Arg"""

    if not isinstance(argument, (OArg, RArg)):
        raise ValueError(
            "expected {} to be of type OArg or RArg".format(type(argument)))

    opt_params, errors = _extract_parameters(argument.exprs)

    return opt_params, errors

