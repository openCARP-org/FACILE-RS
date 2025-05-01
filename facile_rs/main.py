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

from .utils import cli


def main():
    # load the environment
    cli.setup_env()

    # Create the command-line parser
    parser = cli.create_parser()
    args = parser.parse_args()

    # Print help if subcommand is missing
    subcommand = args.subcommand
    if subcommand is None:
        parser.print_help()
    else:
        try:
            module = args.module
        except AttributeError:
            subparser = parser.get_subparser(subcommand)
            subparser.print_help()
        else:
            # setup logs
            cli.setup_logs(args.LOG_LEVEL, args.LOG_FILE)

            # Call the "main" function of the module
            module.main(args)


if __name__ == "__main__":
    main()
