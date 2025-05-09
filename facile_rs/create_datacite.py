#!/usr/bin/env python3

"""Create a DataCite XML file from a CodeMeta JSON file.

Description
-----------

Create a DataCite XML file following the DataCite Metadata Schema 4.3, from one or several CodeMeta metadata files.
The metadata can be provided via a (list of) location(s) given as URL or local file path.

Usage
-----

.. argparse::
   :module: facile_rs.create_datacite
   :func: create_parser
   :prog: create_datacite.py

"""
from pathlib import Path

from .utils import cli
from .utils.metadata import CodemetaMetadata, DataciteMetadata


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('--codemeta-location', dest='CODEMETA_LOCATION', required=True,
                        help='Location of the main codemeta.json JSON file')
    parser.add_argument('--creators-locations', '--creators-location', dest='CREATORS_LOCATIONS',
                        action='append', default=[],
                        help='Locations of codemeta JSON files for additional creators')
    parser.add_argument('--contributors-locations', '--contributors-location', dest='CONTRIBUTORS_LOCATIONS',
                        action='append', default=[],
                        help='Locations of codemeta JSON files for additional contributors')
    parser.add_argument('--datacite-path', dest='DATACITE_PATH',
                        help='Path to the DataCite XML output file')
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
    codemeta.compute_names()
    codemeta.remove_doubles()
    if args.SORT_AUTHORS:
        codemeta.sort_persons()

    datacite_metadata = DataciteMetadata(codemeta.data)
    datacite_xml = datacite_metadata.to_xml()

    if args.DATACITE_PATH:
        Path(args.DATACITE_PATH).expanduser().write_text(datacite_xml)
    else:
        print(datacite_xml)


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
