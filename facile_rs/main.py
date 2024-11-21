#!/usr/bin/env python3

"""FACILE-RS command-line tool, used to call the different scripts of the FACILE-RS project.

Description
-----------

This script is the entry point of the FACILE-RS command-line tool.
It is used to call the different scripts of the FACILE-RS project.
Use subcommands to select a platform (Zenodo, RADAR, ...) or metadata type (CFF, DataCite,...).
Use subsubcommands to select a FACILE-RS functionality.

Usage
-----

.. argparse::
    :module: facile_rs.utils.cli
    :func: create_parser
    :prog: facile-rs

Examples
--------

To generate CFF metadata from a CodeMeta metadata file:

    $ facile-rs cff create --codemeta-location codemeta.json
"""

import argparse
import sys

from .utils import cli


def main():
    # Create the command-line parser
    parser = cli.create_parser()
    args = parser.parse_args()
    # Print help if subcommand is missing
    subcommand = args.subcommand
    if subcommand is None:
        parser.print_help()
        sys.exit(1)
    # args.mode contains the name of the script to execute
    try:
        func = args.func
    except AttributeError:
        print(f"Error: missing subcommand for '{subcommand}'.")
        # Get help for given subcommand
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                subparser = action.choices[subcommand]
                subparser.print_help()
                break
        sys.exit(1)
    # Call the script with the remaining arguments
    command_str = ' '.join(sys.argv[:3])
    sys.argv = [command_str] + sys.argv[3:]
    func()

if __name__ == "__main__":
    main()
