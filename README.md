# bib2glossary

## Installation

    >> pip install bib2glossary

## Usage

Currently only conversion of `\newacronym` is implemented:

    >> bib2acronym --help
    usage: bib2acronym [-h] [-a field] [-f field] filepath

    convert a bibtex file to a tex file containing acronym definitions

    positional arguments:
    filepath              bibtex file path

    optional arguments:
    -h, --help            show this help message and exit
    -a field, --abbrev-field field
                            the bib field defining the abbreviation (default: shorttitle)
    -f field, --full-field field
                            the bib field defining the full name (default: abstract)

or

    >> acronym2bib --help
    usage: acronym2bib [-h] [-a field] [-f field] filepath

    convert a tex file containing acronym definitions to a bibtex file

    positional arguments:
    filepath              tex file path

    optional arguments:
    -h, --help            show this help message and exit
    -a field, --abbrev-field field
                            the bib field defining the abbreviation (default: shorttitle)
    -f field, --full-field field
                            the bib field defining the full name (default: abstract)
