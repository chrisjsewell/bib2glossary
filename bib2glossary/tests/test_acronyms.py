import os
from bib2glossary.tests import TEST_DIR
from bib2glossary.acronyms import (bib_to_tex, tex_to_dict, tex_to_bib,
                                   run_tex_to_bib, run_bib_to_tex)


def test_bib_to_tex():

    text_str = """
@misc{thekey,
  title = {Thekey},
  shorttitle = {ABRV},
  journal = {Abbreviation}
}
@misc{otherkey,
  title = {Otherkey},
  shorttitle = {OTHER},
  journal = {Abbreviation of other}
}
    """
    acronyms = bib_to_tex(text_str)

    assert acronyms == [
        "\\newacronym{otherkey}{OTHER}{Abbreviation of other}",
        "\\newacronym{thekey}{ABRV}{Abbreviation}"]


def test_bib_to_tex_with_options():

    text_str = """
@misc{thekey,
  title = {Thekey},
  shorttitle = {ABRV},
  journal = {Abbreviation},
  abstract = {a description}
}
@misc{otherkey,
  title = {Otherkey},
  shorttitle = {OTHER},
  journal = {Abbreviation of other},
  series = {OTHERs}
}
    """
    acronyms = bib_to_tex(text_str)

    assert acronyms == [
        "\\newacronym[plural={OTHERs}]{otherkey}{OTHER}{Abbreviation of other}",
        "\\newacronym[description={a description}]{thekey}{ABRV}{Abbreviation}"
    ]


def test_tex_to_dict():

    text_str = """
    \\newacronym{otherkey}{OTHER}{Abbreviation of other}
    \\newacronym{thekey}{ABRV}{Abbreviation}
    """

    bib, _ = tex_to_dict(text_str)

    assert bib == [
        {
            'ENTRYTYPE': 'misc',
            'ID': 'otherkey',
            'journal': 'Abbreviation of other',
            'shorttitle': 'OTHER'},
        {
            'ENTRYTYPE': 'misc',
            'ID': 'thekey',
            'journal': 'Abbreviation',
            'shorttitle': 'ABRV'}
    ]


def test_tex_to_dict_with_options():

    text_str = """
    \\newacronym[description={a description}]{otherkey}{OTHER}{Abbreviation of other}
    \\newacronym[plural={ABRVs},longplural={Abbreviations}]{thekey}{ABRV}{Abbreviation}
    """

    bib, _ = tex_to_dict(text_str)

    assert bib == [
        {
            'ENTRYTYPE': 'misc',
            'ID': 'otherkey',
            'journal': 'Abbreviation of other',
            'shorttitle': 'OTHER',
            'abstract': 'a description'
        },
        {
            'ENTRYTYPE': 'misc',
            'ID': 'thekey',
            'journal': 'Abbreviation',
            'shorttitle': 'ABRV',
            'series': 'ABRVs',
            'isbn': 'Abbreviations'
        }
    ]


def test_tex_to_bib():

    text_str = """
    \\newacronym{otherkey}{OTHER}{Abbreviation of other}
    \\newacronym{thekey}{ABRV}{Abbreviation}
    """

    expect_str = """@misc{otherkey,
  journal = {Abbreviation of other},
  shorttitle = {OTHER}
}

@misc{thekey,
  journal = {Abbreviation},
  shorttitle = {ABRV}
}

"""

    bib_str = tex_to_bib(text_str)

    assert bib_str == expect_str


def test_run_tex_to_bib():

    filepath = os.path.join(TEST_DIR, 'examples', 'acronym.tex')
    outstr = run_tex_to_bib([filepath, "--entry-type", "other"])

    expected = """@other{aa,
  journal = {An Acronyms},
  shorttitle = {AA}
}

@other{asa,
  journal = {A Second Acronym},
  shorttitle = {ASA}
}

@other{awo,
  abstract = {a description \\tesxtrm{abc}},
  journal = {Acronym With Options},
  series = {AWOs},
  shorttitle = {AWO}
}

"""
    assert outstr == expected


def test_run_tex_to_bib_with_json():

    filepath = os.path.join(TEST_DIR, 'examples', 'acronym.tex')
    jsonpath = os.path.join(TEST_DIR, 'examples', 'param2field.json')
    outstr = run_tex_to_bib([filepath, "--param2field", jsonpath])

    expected = """@misc{aa,
  abbrevfield = {AA},
  journal = {An Acronyms}
}

@misc{asa,
  abbrevfield = {ASA},
  journal = {A Second Acronym}
}

@misc{awo,
  abbrevfield = {AWO},
  abstract = {a description \\tesxtrm{abc}},
  journal = {Acronym With Options},
  series = {AWOs}
}

"""
    assert outstr == expected


def test_run_bib_to_tex():

    filepath = os.path.join(TEST_DIR, 'examples', 'acronym.bib')
    outstr = run_bib_to_tex([filepath, "--entry-type", "misc"])
    expected = """% Created by bib2glossary
\\newacronym{aa}{AA}{An Acronym}
\\newacronym{asa}{ASA}{A Second Acronym}
\\newacronym[description={a description},plural={AWOs}]{awo}{AWO}{Acronym With Options}
"""
    assert outstr == expected


def test_run_bib_to_tex_missing_type():

    filepath = os.path.join(TEST_DIR, 'examples', 'acronym.bib')
    outstr = run_bib_to_tex([filepath, "--entry-type", "other"])
    expected = """% Created by bib2glossary
"""
    assert outstr == expected
