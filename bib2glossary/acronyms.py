import logging

from TexSoup import TexSoup
from TexSoup.data import OArg

from bib2glossary.shared.parsing import (raise_IOError, parse_bib, write_bib,
                                         extract_required_val,
                                         extract_parameters,
                                         create_msg_error,
                                         create_msg_duplicates)
from bib2glossary.shared.execution import (run_tex_to_bib_shared,
                                           run_bib_to_tex_shared)

logger = logging.getLogger(__name__)

_DEFAULTP2F = (("abbreviation", "shorttitle"),
               ("longname", "journal"),
               ("description", "abstract"),
               ("plural", "series"),
               ("longplural", "isbn"),
               ("firstplural", "address"))


def bib_to_tex(text_str, entry_type='misc',
               param2field=None):
    """create a list of tex newacronym strings

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

    entries = parse_bib(text_str)

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
        for param in sorted(param2field.keys()):
            field = param2field[param]
            if field in fields:
                options.append("{0}={{{1}}}".format(param, fields[field]))
        if options:
            body = "[" + ",".join(options) + "]" + body

        acronyms.append("\\newacronym"+body)

    return acronyms


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
            msg = create_msg_error(
                "could not parse acronym (too few arguments)", acronym, row)
            warning_handler(msg)
            continue
        if len(arguments) > 4:
            msg = create_msg_error(
                "could not parse acronym (too many arguments)", acronym, row)
            warning_handler(msg)
            continue

        key = extract_required_val(arguments[-3])
        if key in keys:
            duplicates[key] = duplicates.get(key, []) + [row]
            continue

        entry['ID'] = key
        entry[abbrev_field] = extract_required_val(arguments[-2])
        entry[name_field] = extract_required_val(arguments[-1])

        if len(arguments) == 4:
            options = arguments[0]

            if not isinstance(options, OArg):
                msg = create_msg_error(
                    "expected first argument to be 'optional",
                    acronym, row)
                warning_handler(msg)
                continue

            opt_params, errors = extract_parameters(options)

            for error in errors:
                msg = create_msg_error(
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
                                 "newacronym",
                                 tex_to_bib,
                                 logger)


def run_bib_to_tex(sys_args):
    """ """
    return run_bib_to_tex_shared(sys_args,
                                 "newacronym",
                                 bib_to_tex,
                                 logger)
