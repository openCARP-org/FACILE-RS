#!/usr/bin/env python3

"""Create an archive in Zenodo.

Description
-----------

This script creates an archive in Zenodo and uploads the assets provided as positional arguments.
The metadata is created similar to create_datacite.

If the Zenodo ID is already present in the CodeMeta file, the existing Zenodo archive is updated instead.

Usage
-----

.. argparse::
    :module: facile_rs.create_zenodo
    :func: create_parser
    :prog: create_zenodo.py

"""

import argparse
import smtplib
from pathlib import Path

from .utils import cli, settings
from .utils.http import fetch_files
from .utils.metadata import CodemetaMetadata, ZenodoMetadata
from .utils.zenodo import create_zenodo_dataset, update_zenodo_dataset, upload_zenodo_assets


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)
    parser.add_argument('assets', nargs='*', default=[],
                        help='Assets to be added to the repository.')
    parser.add_argument('--codemeta-location', dest='codemeta_location',
                        help='Location of the main codemeta.json JSON file')
    parser.add_argument('--creators-location', dest='creators_locations', action='append', default=[],
                        help='Locations of codemeta JSON files for additional creators')
    parser.add_argument('--contributors-location', dest='contributors_locations', action='append', default=[],
                        help='Locations of codemeta JSON files for additional contributors')
    parser.add_argument('--no-sort-authors', dest='sort_authors', action='store_false',
                        help='Do not sort authors alphabetically, keep order in codemeta.json file')
    parser.set_defaults(sort_authors=True)
    parser.add_argument('--zenodo-path', dest='zenodo_path',
                        help='Path to the directory where the assets are collected before upload to Zenodo.')
    parser.add_argument('--zenodo-url', dest='zenodo_url',
                        help='URL of the Zenodo service. Test environment available at https://sandbox.zenodo.org')
    parser.add_argument('--zenodo-token', dest='zenodo_token',
                        help='Zenodo personal token.')
    parser.add_argument('--smtp-server', dest='smtp_server',
                        help='SMTP server used to inform about new release. No mail sent if empty.')
    parser.add_argument('--notification-email', dest='notification_email',
                        help='Recipient address to inform about new release. No mail sent if empty.')
    parser.add_argument('--dry', action='store_true',
                        help='Perform a dry run, do not upload anything.')
    parser.add_argument('--log-level', dest='log_level',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')
    return parser


def main():
    parser = create_parser()

    settings.setup(parser, validate=[
        'CODEMETA_LOCATION',
        'ZENODO_PATH',
        'ZENODO_URL',
        'ZENODO_TOKEN'
    ])

    # setup the bag directory
    zenodo_path = Path(settings.ZENODO_PATH).expanduser()
    if zenodo_path.exists():
        parser.error(f'{zenodo_path} already exists.')
    zenodo_path.mkdir()

    # prepare Zenodo payload
    codemeta = CodemetaMetadata()
    codemeta.fetch(settings.CODEMETA_LOCATION)
    codemeta.fetch_authors(settings.CREATORS_LOCATIONS)
    codemeta.fetch_contributors(settings.CONTRIBUTORS_LOCATIONS)
    codemeta.compute_names()
    codemeta.remove_doubles()
    if settings.SORT_AUTHORS:
        codemeta.sort_persons()

    # override name/title to include version
    codemeta.data['name'] = '{name} ({version})'.format(**codemeta.data)

    zenodo_metadata = ZenodoMetadata(codemeta.data)
    zenodo_dict = zenodo_metadata.as_dict()

    # collect assets
    fetch_files(settings.ASSETS, zenodo_path)

    if not settings.DRY:
        # update or create Zenodo dataset
        zenodo_id = None
        if 'identifier' in codemeta.data and isinstance(codemeta.data['identifier'], list):
            for identifier in codemeta.data['identifier']:
                if identifier.get('propertyID') == 'Zenodo':
                    zenodo_id = identifier['value']

        if zenodo_id:
            print('zenodo_id:', zenodo_id)
            dataset_id = update_zenodo_dataset(settings.ZENODO_URL, zenodo_id, settings.ZENODO_TOKEN, zenodo_dict)
        else:
            print(zenodo_id, 'not found')
            dataset_id = create_zenodo_dataset(settings.ZENODO_URL, settings.ZENODO_TOKEN, zenodo_dict)

        # upload assets
        upload_zenodo_assets(settings.ZENODO_URL, dataset_id, settings.ZENODO_TOKEN, settings.ASSETS, zenodo_path)

        if settings.SMTP_SERVER and settings.NOTIFICATION_EMAIL:
            message = """\
    From: {}
    To: {}
    Subject: {}

    {}
    """.format(
        settings.NOTIFICATION_EMAIL,
        settings.NOTIFICATION_EMAIL,
        "New Zenodo release ready to publish",
        "A new Zenodo release has been uploaded by a CI pipeline.\n\n Please visit"
        f" {settings.ZENODO_URL}/uploads/{dataset_id} to publish this release.")
            server = smtplib.SMTP(settings.SMTP_SERVER)
            server.sendmail(settings.NOTIFICATION_EMAIL, settings.NOTIFICATION_EMAIL, message)
            server.quit()


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
