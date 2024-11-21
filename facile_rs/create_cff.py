#!/usr/bin/env python3

"""Create a CFF citation file from a CodeMeta metadata file

Description
-----------

This script takes a CodeMeta metadata file as input and generates a CFF (Citation File Format) citation file.
The CFF file contains information about the software, including its authors, contributors, and other metadata.

The script accepts command-line arguments to specify the locations of the CodeMeta metadata file, additional
codemeta JSON files for creators and contributors and the path to the output CFF file.

Usage
-----

.. argparse::
   :module: facile_rs.create_cff
   :func: create_parser
   :prog: create_cff.py

Example usage
-------------

.. code-block:: bash

    python3 create_cff.py \\
        --codemeta-location /path/to/codemeta.json \\
        --creators-location /path/to/creators.json \\
        --cff-path /path/to/output.cff

"""

import argparse
from pathlib import Path

from .utils import cli, settings
from .utils.metadata import CffMetadata, CodemetaMetadata


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)

    parser.add_argument('--codemeta-location', dest='codemeta_location',
                        help='Locations of the main codemeta.json JSON file')
    parser.add_argument('--creators-location', dest='creators_locations', action='append', default=[],
                        help='Locations of codemeta JSON files for additional creators')
    parser.add_argument('--contributors-location', dest='contributors_locations', action='append', default=[],
                        help='Locations of codemeta JSON files for additional contributors')
    parser.add_argument('--cff-path', dest='cff_path',
                        help='Path to the cff output file')
    parser.add_argument('--no-sort-authors', dest='sort_authors', action='store_false',
                        help='Do not sort authors alphabetically, keep order in codemeta.json file')
    parser.set_defaults(sort_authors=True)
    parser.add_argument('--log-level', dest='log_level',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')
    return parser

def main():
    parser = create_parser()

    settings.setup(parser, validate=[
        'CODEMETA_LOCATION'
    ])

    codemeta = CodemetaMetadata()
    codemeta.fetch(settings.CODEMETA_LOCATION)
    codemeta.fetch_authors(settings.CREATORS_LOCATIONS)
    codemeta.fetch_contributors(settings.CONTRIBUTORS_LOCATIONS)
    codemeta.remove_doubles()
    if settings.SORT_AUTHORS:
        codemeta.sort_persons()

    cff_metadata = CffMetadata(codemeta.data)
    cff_yaml = cff_metadata.to_yaml()

    if settings.CFF_PATH:
        Path(settings.CFF_PATH).expanduser().write_text(cff_yaml)
    else:
        print(cff_yaml)


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
