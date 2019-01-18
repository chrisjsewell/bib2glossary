import bibtexparser
import re

_ACRONYM_STR = "\\newacronym{{{key}}}{{{abbrev}}}{{{full}}}"
_ACRONYM_REGEX = "\\\\newacronym\\{(.*)\\}\\{(.*)\\}\\{(.*)\\}"


def bib_to_tex(text_str: str,
               abbrev_field="shorttitle", full_field="abstract"):
    """create a list of tex acronym strings

    Parameters
    ----------
    text_str: str
        the .bib file text
    abbrev_field: str
        the field to use as the abbreviation
    full_key: str
        the field to use as the full name

    Returns
    -------
    acronyms: a list of string

    """

    parser = bibtexparser.bparser.BibTexParser()
    bib = parser.parse(text_str)
    # TODO doesn't appear to check for key duplication
    entries = bib.get_entry_dict()

    acronyms = []
    for key in sorted(entries.keys()):
        fields = entries.get(key)
        acronyms.append(_ACRONYM_STR.format(
            key=key,
            abbrev=fields.get(abbrev_field),
            full=fields.get(full_field)))

    return acronyms


def tex_to_dict(text_str: str, entry_type='misc',
                abbrev_field="shorttitle", full_field="abstract"):
    """create a dictionary of bib entries

    Parameters
    ----------
    text_str: str
        the .tex file string
    entry_type: str
        the entry type for each bib item
    abbrev_field: str
        the field to use as the abbreviation
    full_key: str
        the field to use as the full name

    Returns
    -------
    entries: dict {<key>: {abbrev_field: <abbreviation>, full_field:<fullname>}}
    duplicates: dict {<key>: list of rows}

    """
    regex = re.compile(_ACRONYM_REGEX)
    entries = []
    duplicates = {}
    for row, line in enumerate(text_str.splitlines()):
        for key, abbrev, full in regex.findall(line):
            if key in entries:
                duplicates[key] = duplicates.get(key, []) + [row]
            else:
                entries.append({
                    'ENTRYTYPE': entry_type,
                    'ID': key,
                    abbrev_field: abbrev,
                    full_field: full
                })

    return entries, duplicates


def handle_duplicates(duplicates):
    """ handle duplicates
    """
    # TODO handle duplicates
    pass


def tex_to_bib(text_str: str, entry_type="misc",
               abbrev_field="shorttitle", full_field="abstract"):
    """create a bib file string

    Parameters
    ----------
    text_str: str
        the .tex file string
    entry_type: str
        the entry type for each bib item
    abbrev_field: str
        the field to use as the abbreviation
    full_key: str
        the field to use as the full name

    Returns
    -------
    bib_file: str

    """
    entries, duplicates = tex_to_dict(text_str,
                                      entry_type=entry_type,
                                      abbrev_field=abbrev_field,
                                      full_field=full_field)

    if duplicates:
        handle_duplicates(duplicates)

    bib_database = bibtexparser.bibdatabase.BibDatabase()
    bib_database.entries = entries

    writer = bibtexparser.bwriter.BibTexWriter()
    writer.contents = ['comments', 'entries']
    writer.indent = '  '
    writer.order_entries_by = ('ENTRYTYPE', 'author', 'year')
    bibtex_str = bibtexparser.dumps(bib_database, writer)

    return bibtex_str
