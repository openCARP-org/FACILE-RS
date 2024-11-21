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

import argparse
from pathlib import Path

import bagit

from .utils import cli, settings
from .utils.checksum import get_sha256, get_sha512
from .utils.http import fetch_dict, fetch_files


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)

    parser.add_argument('assets', nargs='*', default=[],
                        help='Assets to be added to the bag.')
    parser.add_argument('--bag-path', dest='bag_path',
                        help='Path to the Bag directory')
    parser.add_argument('--bag-info-location', dest='bag_info_locations', action='append', default=[],
                        help='Locations of the bag-info YAML/JSON files')
    parser.add_argument('--datacite-path', dest='datacite_path',
                        help='Path to the DataCite XML file')
    parser.add_argument('--log-level', dest='log_level',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')

    return parser


def main():
    parser = create_parser()

    settings.setup(parser, validate=[
        'BAG_PATH',
        'DATACITE_PATH'
    ])

    # setup the bag
    bag_path = Path(settings.BAG_PATH).expanduser()
    if bag_path.exists():
        parser.error(f'{bag_path} already exists.')
    bag_path.mkdir()

    # collect assets
    fetch_files(settings.ASSETS, bag_path)

    # fetch bag-info
    bag_info = {}
    for location in settings.BAG_INFO_LOCATIONS:
        bag_info.update(fetch_dict(location))

    # create bag using bagit
    bag = bagit.make_bag(bag_path, bag_info)
    bag.save()

    # get datacite.xml and put it in the bag
    datacite_path = Path(settings.DATACITE_PATH).expanduser()
    datacite_xml = datacite_path.read_text()
    datacite_bag_path = bag_path / 'metadata' / 'datacite.xml'
    datacite_bag_path.parent.mkdir()
    datacite_bag_path.write_text(datacite_xml)

    with open(bag_path / 'tagmanifest-sha256.txt', 'a') as f:
        f.write(f'{get_sha256(datacite_path)} metadata/datacite.xml\n')

    with open(bag_path / 'tagmanifest-sha512.txt', 'a') as f:
        f.write(f'{get_sha512(datacite_path)} metadata/datacite.xml\n')


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
