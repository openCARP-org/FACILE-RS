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

import argparse
from pathlib import Path

from .utils import cli, settings
from .utils.metadata import CodemetaMetadata, DataciteMetadata


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)

    parser.add_argument('--codemeta-location', dest='codemeta_location',
                        help='Location of the main codemeta.json JSON file')
    parser.add_argument('--creators-location', dest='creators_locations', action='append', default=[],
                        help='Locations of codemeta JSON files for additional creators')
    parser.add_argument('--contributors-location', dest='contributors_locations', action='append', default=[],
                        help='Locations of codemeta JSON files for additional contributors')
    parser.add_argument('--datacite-path', dest='datacite_path',
                        help='Path to the DataCite XML output file')
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
    codemeta.compute_names()
    codemeta.remove_doubles()
    if settings.SORT_AUTHORS:
        codemeta.sort_persons()

    datacite_metadata = DataciteMetadata(codemeta.data)
    datacite_xml = datacite_metadata.to_xml()

    if settings.DATACITE_PATH:
        Path(settings.DATACITE_PATH).expanduser().write_text(datacite_xml)
    else:
        print(datacite_xml)


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
