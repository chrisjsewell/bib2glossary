import os
from collections import deque
import json

from six import ensure_str
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


def extract_required(rarg):
    """extract the value of a TexSoup RArg"""
    if not isinstance(rarg, RArg):
        raise ValueError(
            "expected {} to be a required argument".format(type(rarg)))
    return rarg.value


def extract_parameters(texsoup_exprs):
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


def extract_options(options):
    """extract parameters from a TexSoup OArg"""

    if not isinstance(options, OArg):
        raise ValueError(
            "expected {} to be of type OArg".format(type(options)))

    opt_params, errors = extract_parameters(options.exprs)

    return opt_params, errors


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
