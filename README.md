# bib2glossary

This package is intended to allow for the storage and management of [latex glossary terms](https://en.wikibooks.org/wiki/LaTeX/Glossary) in standard reference management packages (such as Zotero and Mendeley), by converting a `.bib`
file to a `.tex` file.

To date the only other way to achieve this is *via* [bib2gls](https://tex.stackexchange.com/questions/342544/is-there-a-program-for-managing-glossary-tags). However, it implementation is somewhat complex, and the item types it uses are not supported by Zotero.

In `bib2glossary`, the user may define the relationship between the reference item fields (for common fields see [here](https://www.zotero.org/support/kb/item_types_and_fields)) and glossary term inputs.

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

