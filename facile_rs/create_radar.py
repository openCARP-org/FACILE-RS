#!/usr/bin/env python3

"""Create an archive in the RADAR service.

Description
-----------

This script creates an archive in the RADAR service and uploads the assets provided as positional arguments.
The metadata is created similar to create_datacite.

If the RADAR ID is already present in the CodeMeta file, the existing RADAR archive is updated instead.

Usage
-----

.. argparse::
    :module: facile_rs.create_radar
    :func: create_parser
    :prog: create_radar.py

"""

import argparse
import smtplib
from pathlib import Path

from .utils import cli, settings
from .utils.http import fetch_files
from .utils.metadata import CodemetaMetadata, RadarMetadata
from .utils.radar import create_radar_dataset, fetch_radar_token, update_radar_dataset, upload_radar_assets


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
    parser.add_argument('--radar-path', dest='radar_path',
                        help='Path to the Radar directory, where the assets are collected before upload.')
    parser.add_argument('--radar-url', dest='radar_url',
                        help='URL of the RADAR service.')
    parser.add_argument('--radar-username', dest='radar_username',
                        help='Username for the RADAR service.')
    parser.add_argument('--radar-password', dest='radar_password',
                        help='Password for the RADAR service.')
    parser.add_argument('--radar-client-id', dest='radar_client_id',
                        help='Client ID for the RADAR service.')
    parser.add_argument('--radar-client-secret', dest='radar_client_secret',
                        help='Client secret for the RADAR service.')
    parser.add_argument('--radar-workspace-id', dest='radar_workspace_id',
                        help='Workspace ID for the RADAR service.')
    parser.add_argument('--radar-redirect-url', dest='radar_redirect_url',
                        help='Redirect URL for the OAuth workflow of the RADAR service.')
    parser.add_argument('--radar-email', dest='radar_email',
                        help='Email for the RADAR metadata.')
    parser.add_argument('--radar-backlink', dest='radar_backlink',
                        help='Backlink for the RADAR metadata.')
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
        'RADAR_PATH',
        'RADAR_URL',
        'RADAR_CLIENT_ID',
        'RADAR_CLIENT_SECRET',
        'RADAR_REDIRECT_URL',
        'RADAR_USERNAME',
        'RADAR_PASSWORD',
        'RADAR_WORKSPACE_ID',
        'RADAR_EMAIL',
        'RADAR_BACKLINK'
    ])

    # setup the bag directory
    radar_path = Path(settings.RADAR_PATH).expanduser()
    if radar_path.exists():
        parser.error(f'{radar_path} already exists.')
    radar_path.mkdir()

    # prepare radar payload
    codemeta = CodemetaMetadata()
    codemeta.fetch(settings.CODEMETA_LOCATION)
    codemeta.fetch_authors(settings.CREATORS_LOCATIONS)
    codemeta.fetch_contributors(settings.CONTRIBUTORS_LOCATIONS)
    codemeta.compute_names()
    codemeta.remove_doubles()
    if settings.SORT_AUTHORS:
        codemeta.sort_persons()

    codemeta.data['name'] = '{name} ({version})'.format(**codemeta.data)  # override name/title to include version

    if not codemeta.data.get('copyrightHolder'):
        codemeta.data['copyrightHolder'] = [{
            'name': 'The authors'
        }]

    radar_metadata = RadarMetadata(codemeta.data, settings.RADAR_EMAIL, settings.RADAR_BACKLINK)
    radar_dict = radar_metadata.as_dict()

    # collect assets
    fetch_files(settings.ASSETS, radar_path)

    if not settings.DRY:
        # obtain oauth token
        headers = fetch_radar_token(settings.RADAR_URL, settings.RADAR_CLIENT_ID, settings.RADAR_CLIENT_SECRET,
                                    settings.RADAR_REDIRECT_URL, settings.RADAR_USERNAME, settings.RADAR_PASSWORD)

        # update or create radar dataset
        if radar_dict.get('id'):
            dataset_id = update_radar_dataset(settings.RADAR_URL, radar_dict.get('id'), headers, radar_dict)
        else:
            dataset_id = create_radar_dataset(settings.RADAR_URL, settings.RADAR_WORKSPACE_ID, headers, radar_dict)

        # upload assets
        upload_radar_assets(settings.RADAR_URL, dataset_id, headers, settings.ASSETS, radar_path)

    if settings.SMTP_SERVER and settings.NOTIFICATION_EMAIL:
        message = """\
From: {}
To: {}
Subject: {}

{}
""".format(
    settings.RADAR_EMAIL,
    settings.NOTIFICATION_EMAIL,
    "New RADAR release ready to publish",
    "A new RADAR release has been uploaded by a CI pipeline.\n\n Please visit"
    " https://radar.kit.edu/radar/de/workspace/{}.{} to publish this release.".format(
        settings.RADAR_WORKSPACE_ID,settings.RADAR_CLIENT_ID
))
        server = smtplib.SMTP(settings.SMTP_SERVER)
        server.sendmail(settings.RADAR_EMAIL, settings.NOTIFICATION_EMAIL, message)
        server.quit()


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
