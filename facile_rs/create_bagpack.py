#!/usr/bin/env python3

"""Create a BagIt bag including a DataCite XML file.

Description
-----------

This script creates a BagIt bag using the bagit-python package, but also includes a DataCite XML file
as recommended by the RDA Research Data Repository Interoperability WG.
The assets to be included in the bag are given as positional arguments.

Usage
-----

.. argparse::
    :module: facile_rs.create_bagpack
    :func: create_parser
    :prog: create_bagpack.py

"""
import bagit

from .utils import cli, setup_assets_path
from .utils.checksum import get_sha256, get_sha512
from .utils.exceptions import ParserError
from .utils.http import fetch_dict, fetch_file, fetch_files


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('ASSETS', nargs='*', default=[],
                        help='Assets to be added to the bag.')
    parser.add_argument('--bag-path', dest='BAG_PATH',
                        help='Path to the Bag directory')
    parser.add_argument('--bag-info-locations', '--bag-info-location', dest='BAG_INFO_LOCATIONS',
                        action='append', default=[],
                        help='Locations of the bag-info YAML/JSON files')
    parser.add_argument('--datacite-location', dest='DATACITE_LOCATION',
                        help='Path to the DataCite XML file')
    parser.add_argument('--assets-token', dest='ASSETS_TOKEN',
                        help='Private token, to be used when fetching assets')
    parser.add_argument('--assets-token-name', dest='ASSETS_TOKEN_NAME', default='PRIVATE-TOKEN',
                        help='Name of the header field for the token [default: "PRIVATE-TOKEN"]')
    parser.add_argument('--overwrite', dest='OVERWRITE', action='store_true', env=False,
                        help='Overwrite existing Bag directory')
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')

    return parser


def main(args):
    # setup the bag
    try:
        bag_path = setup_assets_path(args.BAG_PATH, remove_existing=args.OVERWRITE)
    except FileExistsError as e:
        raise ParserError(f'{args.BAG_PATH} already exists. Please remove it or use --overwrite to replace it.') from e

    # collect assets
    fetch_files(args.ASSETS, bag_path, headers={
        args.ASSETS_TOKEN_NAME: args.ASSETS_TOKEN
    })

    # fetch bag-info
    bag_info = {}
    for location in args.BAG_INFO_LOCATIONS:
        bag_info.update(fetch_dict(location))

    # create bag using bagit
    bag = bagit.make_bag(bag_path, bag_info)
    bag.save()

    # fetch datacite.xml and put it in the bag
    datacite_bag_path = bag_path / 'metadata' / 'datacite.xml'
    datacite_bag_path.parent.mkdir()
    fetch_file(args.DATACITE_LOCATION, datacite_bag_path.parent, datacite_bag_path.name, headers={
        args.ASSETS_TOKEN_NAME: args.ASSETS_TOKEN
    })

    with open(bag_path / 'tagmanifest-sha256.txt', 'a') as f:
        f.write(f'{get_sha256(datacite_bag_path)} metadata/datacite.xml\n')

    with open(bag_path / 'tagmanifest-sha512.txt', 'a') as f:
        f.write(f'{get_sha512(datacite_bag_path)} metadata/datacite.xml\n')


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
