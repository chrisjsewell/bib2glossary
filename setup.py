#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
from importlib import import_module
from setuptools import setup  # , find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
with open('test_requirements.txt') as f:
    test_requirements = f.read().splitlines()

with io.open('README.md') as readme:
    description = readme.read()

setup(
    name='bib2glossary',
    version=import_module('bib2glossary').__version__,
    description='A small package to convert between a '
                'latex bib file and a tex file containing glossaries entries',
    long_description=description,
    python_requires='>=3',  # TexSoup breaks python 2 compatibility
    install_requires=requirements,
    tests_require=test_requirements,
    license='GPL',
    author='Chris Sewell',
    author_email='chrisj_sewell@hotmail.com',
    url='https://github.com/chrisjsewell/bib2glossary',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    keywords='latex biblatex bibtex glossaries acronyms',
    zip_safe=True,
    include_package_data=True,
    package_data={},
    scripts=['bin/acronym2bib',
             'bin/bib2acronym',
             'bin/glossary2bib',
             'bin/bib2glossary'],
)
