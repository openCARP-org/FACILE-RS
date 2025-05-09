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
from pathlib import Path

from .utils import cli
from .utils.metadata import CffMetadata, CodemetaMetadata


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('--codemeta-location', dest='CODEMETA_LOCATION', required=True,
                        help='Locations of the main codemeta.json JSON file')
    parser.add_argument('--creators-locations', '--creators-location', dest='CREATORS_LOCATIONS',
                        action='append', default=[],
                        help='Locations of codemeta JSON files for additional creators')
    parser.add_argument('--contributors-locations', '--contributors-location', dest='CONTRIBUTORS_LOCATIONS',
                        action='append', default=[],
                        help='Locations of codemeta JSON files for additional contributors')
    parser.add_argument('--cff-path', dest='CFF_PATH',
                        help='Path to the cff output file')
    parser.add_argument('--no-sort-authors', dest='SORT_AUTHORS', action='store_false',
                        help='Do not sort authors alphabetically, keep order in codemeta.json file')
    parser.set_defaults(sort_authors=True)
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')
    return parser

def main(args):
    codemeta = CodemetaMetadata()
    codemeta.fetch(args.CODEMETA_LOCATION)
    codemeta.fetch_authors(args.CREATORS_LOCATIONS)
    codemeta.fetch_contributors(args.CONTRIBUTORS_LOCATIONS)
    codemeta.remove_doubles()
    if args.SORT_AUTHORS:
        codemeta.sort_persons()

    cff_metadata = CffMetadata(codemeta.data)
    cff_yaml = cff_metadata.to_yaml()

    if args.CFF_PATH:
        Path(args.CFF_PATH).expanduser().write_text(cff_yaml)
    else:
        print(cff_yaml)


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
