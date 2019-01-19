# bib2glossary

This package is intended to allow for the storage and management of
[latex glossary terms](https://en.wikibooks.org/wiki/LaTeX/Glossary)
in standard reference management packages (such as Zotero),
by converting between `.bib` files
and `.tex` files containing `\newglossaryentry` or `\newacronym` definitions.

To date the only other way to achieve this is *via* [bib2gls](https://tex.stackexchange.com/questions/342544/is-there-a-program-for-managing-glossary-tags). However, it implementation is somewhat complex, and the item types it uses are not supported by Zotero.

In `bib2glossary`, the user may override the default relationships between
reference item fields and glossary term parameters,
by supplying a JSON file, e.g.:

```json
{
    "abbreviation": "abbrevfield"
}
```

The defaults are taken from the `Dictionary Entry` type in [Zotero](https://www.zotero.org/support/kb/item_types_and_fields).

For `\newacronym`:

| Parameter    | Field      |
| ------------ | ---------- |
| misc         | @type      |
| longname     | journal*   |
| abbreviation | shorttitle |
| description  | abstract   |
| plural       | series     |
| longplural   | isbn       |
| firstplural  | address**  |

For `\newglossaryentry`:

| Parameter   | Field     |
| ----------- | --------- |
| misc        | @type     |
| name        | journal*  |
| description | abstract  |
| plural      | series    |
| symbol      | volume    |
| text        | edition   |
| sort        | publisher |

\* This shows as 'Dictionary Title' in Zotero

\*\* This shows as 'Place' in Zotero

[Note: The `title` field is not used, since it is usely used to generate the key.]

## Installation

    >> pip install bib2glossary

## Usage

Conversion of `\newacronym`:

    >> bib2acronym --help
    >> bib2acronym path/to/file.bib --entry-type misc --param2field path/to/file.json

or

    >> acronym2bib --help
    >> acronym2bib path/to/file.tex --entry-type misc --param2field path/to/file.json

Conversion of `\newglossaryentry`:

    >> bib2glossary --help
    >> bib2glossary path/to/file.bib --entry-type misc --param2field path/to/file.json

or

    >> glossary2bib --help
    >> glossary2bib path/to/file.tex --entry-type misc --param2field path/to/file.json

## Implementation

- Parsing of `tex` files is handled by [TexSoup](https://github.com/alvinwan/TexSoup)
- Parsing of `bib` files is handled by [BibtexParser](https://bibtexparser.readthedocs.io)