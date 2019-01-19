import os
from bib2glossary.tests import TEST_DIR
from bib2glossary.glossaries import (bib_to_tex, tex_to_dict, tex_to_bib,
                                   run_tex_to_bib, run_bib_to_tex)


def test_bib_to_tex():

    text_str = """
@misc{thekey,
  abstract = {the description},
  journal = {name},
  title = {Thekey}
}
@misc{otherkey,
  abstract = {the description of other},
  shorttitle = {OTHER},
  journal = {other name}
}
    """
    glossaries = bib_to_tex(text_str)

    assert glossaries == [
        '\\newglossaryentry{otherkey}{\n    description={the description of other},\n    name={other name}\n}',
        '\\newglossaryentry{thekey}{\n    description={the description},\n    name={name}\n}'
    ]


def test_tex_to_dict():

    text_str = """
\\newglossaryentry{otherkey}{
    name={other name},
    description={the description of other}
}
\\newglossaryentry{thekey}{
    name={name},
    description={the description}
}    """

    bib, _ = tex_to_dict(text_str)

    assert bib == [
        {
            'ENTRYTYPE': 'misc',
            'ID': 'otherkey',
            'journal': 'other name',
            'abstract': 'the description of other'},
        {
            'ENTRYTYPE': 'misc',
            'ID': 'thekey',
            'journal': 'name',
            'abstract': 'the description'}
    ]


def test_tex_to_bib():

    text_str = """
\\newglossaryentry{otherkey}{
    name={other name},
    description={the description of other}
}
\\newglossaryentry{thekey}{
    name={name},
    description={the description}
}    """

    expect_str = """@misc{otherkey,
  abstract = {the description of other},
  journal = {other name}
}

@misc{thekey,
  abstract = {the description},
  journal = {name}
}

"""

    bib_str = tex_to_bib(text_str)

    assert bib_str == expect_str


def test_run_tex_to_bib():

    filepath = os.path.join(TEST_DIR, 'examples', 'glossary.tex')
    outstr = run_tex_to_bib([filepath, "--entry-type", "other"])

    expected = """@other{otherkey,
  abstract = {the description of other},
  journal = {other name}
}

@other{thekey,
  abstract = {the description},
  journal = {name},
  publisher = {sortid}
}

"""
    assert outstr == expected


def test_run_tex_to_bib_with_json():

    filepath = os.path.join(TEST_DIR, 'examples', 'glossary.tex')
    jsonpath = os.path.join(TEST_DIR, 'examples', 'param2field.json')
    outstr = run_tex_to_bib([filepath, "--param2field", jsonpath])

    expected = """@misc{otherkey,
  abstract = {the description of other},
  journal = {other name}
}

@misc{thekey,
  abstract = {the description},
  journal = {name},
  sortfield = {sortid}
}

"""
    assert outstr == expected


def test_run_bib_to_tex():

    filepath = os.path.join(TEST_DIR, 'examples', 'glossary.bib')
    outstr = run_bib_to_tex([filepath, "--entry-type", "misc"])
    expected = """% Created by bib2glossary
\\newglossaryentry{otherkey}{
    description={the description of other},
    name={other name}
}
\\newglossaryentry{thekey}{
    description={the description},
    name={name},
    sort={sortid}
}
"""
    assert outstr == expected


def test_run_bib_to_tex_missing_type():

    filepath = os.path.join(TEST_DIR, 'examples', 'glossary.bib')
    outstr = run_bib_to_tex([filepath, "--entry-type", "other"])
    expected = """% Created by bib2glossary
"""
    assert outstr == expected
