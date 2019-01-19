import logging

from TexSoup import TexSoup

from bib2glossary.shared.parsing import (raise_IOError, parse_bib, write_bib,
                                         create_msg_error,
                                         create_msg_duplicates,
                                         extract_required_val,
                                         extract_parameters)
from bib2glossary.shared.execution import (run_tex_to_bib_shared,
                                           run_bib_to_tex_shared)

logger = logging.getLogger(__name__)

_DEFAULTP2F = (("name", "journal"),
               ("description", "abstract"),
               ("plural", "series"),
               ("symbol", "volume"),
               ("text", "edition"),
               ("sort", "publisher"))


def bib_to_tex(text_str, entry_type='misc',
               param2field=None):
    """create a list of tex newglossaryentry strings

    Parameters
    ----------
    text_str: str
        the .bib file text
    entry_type: None or str
        if given, filter by entry_type
    param2field: None or dict
        mapping of glossaries parameter to bib field

    Returns
    -------
    glossaries: a list of string

    """
    param2field_default = dict(_DEFAULTP2F)
    if param2field is not None:
        param2field_default.update(param2field)
    param2field = param2field_default.copy()

    assert "description" in param2field
    assert "name" in param2field
    name_field = param2field.get("name")
    descript_field = param2field.get("description")

    entries = parse_bib(text_str)

    glossaries = []
    for key in sorted(entries.keys()):

        fields = entries.get(key)

        if entry_type and entry_type != (fields.get('ENTRYTYPE', '')):
            continue

        if name_field not in fields:
            logger.warn(
                "Skipping {0}: No {1} key found".format(key, name_field))
            continue
        if descript_field not in fields:
            logger.warn("Skipping {0}: No {1} key found".format(
                key, descript_field))
            continue

        options = []
        for param in sorted(param2field.keys()):
            field = param2field[param]
            if field in fields:
                options.append("{0}={{{1}}}".format(param, fields[field]))
        body = "{{{key}}}{{\n    {params}\n}}".format(
            key=key,
            params=",\n    ".join(options))

        glossaries.append("\\newglossaryentry"+body)

    return glossaries


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

    entries = []
    keys = []
    duplicates = {}

    latex_tree = TexSoup(text_str)

    for gterm in latex_tree.find_all("newglossaryentry"):

        row = None  # TODO get first row (for error reporting)
        arguments = list(gterm.args)
        entry = {'ENTRYTYPE': entry_type}

        if len(arguments) != 2:
            msg = create_msg_error(
                "could not parse glossary entry (arguments != 2)", gterm, row)
            warning_handler(msg)
            continue

        key = extract_required_val(arguments[0])
        if key in keys:
            duplicates[key] = duplicates.get(key, []) + [row]
            continue
        entry['ID'] = key

        params, errors = extract_parameters(arguments[1])

        for error in errors:
            msg = create_msg_error(
                "error reading 'parameter' block: {}".format(error),
                gterm, row)
            warning_handler(msg)

        for param_name, param_value in params.items():
            if param_name not in param2field:
                warning_handler(
                    "parameter '{0}' in key '{1}' not recognised".format(
                        param_name, key))
                continue
            if param2field[param_name] in entry:
                warning_handler(
                    "duplicate parameter '{0}' in key '{1}'".format(
                        param_name, key))
                continue
            entry[param2field[param_name]] = param_value

        entries.append(entry)

    return entries, duplicates


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
        msg = create_msg_duplicates(duplicates)
        warning_handler(msg)

    bibtex_str = write_bib(entries)

    return bibtex_str


def run_tex_to_bib(sys_args):
    """ """
    return run_tex_to_bib_shared(sys_args,
                                 "newglossaryentry",
                                 tex_to_bib,
                                 logger)


def run_bib_to_tex(sys_args):
    """ """
    return run_bib_to_tex_shared(sys_args,
                                 "newglossaryentry",
                                 bib_to_tex,
                                 logger)
