#!/usr/bin/env python3

"""Updates the CodeMeta file with the given ``version`` and ``date``.

Useful to automatically get the version from a git tag and inject it into the repository's metadata file.
The current date is used if no date is provided.

Usage
-----

.. argparse::
   :module: facile_rs.prepare_release
   :func: create_parser
   :prog: prepare_release.py

"""

import argparse
from datetime import date
from pathlib import Path

from .utils import cli, settings
from .utils.metadata import CodemetaMetadata


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)
    parser.add_argument('--codemeta-location', dest='codemeta_location',
                        help='Location of the main codemeta.json JSON file')
    parser.add_argument('--version', dest='version',
                        help='Version of the resource')
    parser.add_argument('--date', dest='date',
                        help='Date for dateModified (format: \'%%Y-%%m-%%d\')')
    parser.add_argument('--log-level', dest='log_level',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')
    return parser

def main():
    parser = create_parser()

    settings.setup(parser, validate=[
        'CODEMETA_LOCATION',
        'VERSION'
    ])

    codemeta = CodemetaMetadata()
    codemeta.fetch(settings.CODEMETA_LOCATION)

    codemeta.data['version'] = settings.VERSION
    codemeta.data['dateModified'] = settings.DATE or date.today().strftime('%Y-%m-%d')

    Path(settings.CODEMETA_LOCATION).expanduser().write_text(codemeta.to_json())


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
