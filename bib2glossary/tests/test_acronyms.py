from bib2glossary.acronyms import bib_to_tex, tex_to_dict, tex_to_bib


def test_bib_to_tex():

    text_str = """
@misc{thekey,
  title = {Thekey},
  shorttitle = {ABRV},
  abstract = {Abbreviation}
}
@misc{otherkey,
  title = {Otherkey},
  shorttitle = {OTHER},
  abstract = {Abbreviation of other}
}
    """
    acronyms = bib_to_tex(text_str)

    assert acronyms == [
        "\\newacronym{otherkey}{OTHER}{Abbreviation of other}",
        "\\newacronym{thekey}{ABRV}{Abbreviation}"]


def test_tex_to_dict():

    text_str = """
    \\newacronym{otherkey}{OTHER}{Abbreviation of other}
    \\newacronym{thekey}{ABRV}{Abbreviation}
    """

    bib, _ = tex_to_dict(text_str)

    assert bib == [
        {
            'key': 'otherkey',
            'abstract': 'Abbreviation of other',
            'shorttitle': 'OTHER'},
        {
            'key': 'thekey',
            'abstract': 'Abbreviation',
            'shorttitle': 'ABRV'}
    ]


def test_tex_to_bib():

    text_str = """
    \\newacronym{otherkey}{OTHER}{Abbreviation of other}
    \\newacronym{thekey}{ABRV}{Abbreviation}
    """

    expect_str = """@misc{otherkey,
  abstract = {Abbreviation of other},
  shorttitle = {OTHER}
}

@misc{thekey,
  abstract = {Abbreviation},
  shorttitle = {ABRV}
}

"""

    bib_str = tex_to_bib(text_str)

    assert bib_str == expect_str
