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
from datetime import date
from pathlib import Path

from .utils import cli
from .utils.metadata import CodemetaMetadata


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('--codemeta-location', dest='CODEMETA_LOCATION', required=True,
                        help='Location of the main codemeta.json JSON file')
    parser.add_argument('--version', dest='VERSION', required=True,
                        help='Version of the resource')
    parser.add_argument('--date', dest='DATE',
                        help='Date for dateModified (format: \'%%Y-%%m-%%d\')')
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')
    return parser


def main(args):
    codemeta = CodemetaMetadata()
    codemeta.fetch(args.CODEMETA_LOCATION)

    codemeta.data['version'] = args.VERSION
    codemeta.data['dateModified'] = args.DATE or date.today().strftime('%Y-%m-%d')

    Path(args.CODEMETA_LOCATION).expanduser().write_text(codemeta.to_json())


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
