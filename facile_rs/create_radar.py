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
import json

from .utils import cli, setup_assets_path, setup_tmp_assets_path
from .utils.exceptions import AssetExistsError, ParserError
from .utils.http import fetch_files
from .utils.mail import send_mail
from .utils.metadata import CodemetaMetadata, RadarMetadata
from .utils.radar import create_radar_dataset, fetch_radar_token, update_radar_dataset, upload_radar_assets


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('ASSETS', nargs='*', default=[],
                        help='Assets to be added to the repository.')
    parser.add_argument('--codemeta-location', dest='CODEMETA_LOCATION', required=True,
                        help='Location of the main codemeta.json JSON file')
    parser.add_argument('--creators-locations', '--creators-location', dest='CREATORS_LOCATIONS',
                        action='append', default=[],
                        help='Locations of codemeta JSON files for additional creators')
    parser.add_argument('--contributors-locations', '--contributors-location', dest='CONTRIBUTORS_LOCATIONS',
                        action='append', default=[],
                        help='Locations of codemeta JSON files for additional contributors')
    parser.add_argument('--no-sort-authors', dest='SORT_AUTHORS', action='store_false', default=True,
                        help='Do not sort authors alphabetically, keep order in codemeta.json file')
    parser.add_argument('--radar-path', dest='RADAR_PATH',
                        help='Path to the local directory, where the assets are collected before upload. '
                             'Optional: if not provided, a temporary directory is used.')
    parser.add_argument('--radar-url', dest='RADAR_URL', required=True,
                        help='URL of the RADAR service.')
    parser.add_argument('--radar-username', dest='RADAR_USERNAME', required=True,
                        help='Username for the RADAR service.')
    parser.add_argument('--radar-password', dest='RADAR_PASSWORD', required=True,
                        help='Password for the RADAR service.')
    parser.add_argument('--radar-client-id', dest='RADAR_CLIENT_ID', required=True,
                        help='Client ID for the RADAR service.')
    parser.add_argument('--radar-client-secret', dest='RADAR_CLIENT_SECRET', required=True,
                        help='Client secret for the RADAR service.')
    parser.add_argument('--radar-workspace-id', dest='RADAR_WORKSPACE_ID', required=True,
                        help='Workspace ID for the RADAR service.')
    parser.add_argument('--radar-redirect-url', dest='RADAR_REDIRECT_URL', required=True,
                        help='Redirect URL for the OAuth workflow of the RADAR service.')
    parser.add_argument('--radar-email', dest='RADAR_EMAIL', required=True,
                        help='Email for the RADAR metadata.')
    parser.add_argument('--radar-backlink', dest='RADAR_BACKLINK', required=True,
                        help='Backlink for the RADAR metadata.')
    parser.add_argument('--smtp-server', dest='SMTP_SERVER',
                        help='SMTP server used to inform about new release. No mail sent if empty.')
    parser.add_argument('--notification-email', dest='NOTIFICATION_EMAIL',
                        help='Recipient address to inform about new release. No mail sent if empty.')
    parser.add_argument('--assets-token', dest='ASSETS_TOKEN',
                        help='Private token, to be used when fetching assets')
    parser.add_argument('--assets-token-name', dest='ASSETS_TOKEN_NAME', default='PRIVATE-TOKEN',
                        help='Name of the header field for the token [default: "PRIVATE-TOKEN"]')
    parser.add_argument('--dry', action='store_true', dest='DRY',
                        help='Perform a dry run, do not upload anything.')
    parser.add_argument('--overwrite', dest='OVERWRITE', action='store_true', env=False,
                        help='Overwrite existing local assets.')
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')
    return parser


def main(args):
    # setup the radar directory
    if args.RADAR_PATH is None:
        radar_path, tmp_dir = setup_tmp_assets_path()
    else:
        radar_path = setup_assets_path(args.RADAR_PATH, exist_ok=True)

    # collect assets
    try:
        fetch_files(args.ASSETS, radar_path, headers={
            args.ASSETS_TOKEN_NAME: args.ASSETS_TOKEN
        }, overwrite=args.OVERWRITE)
    except AssetExistsError as e:
        raise ParserError(f'Could not fetch {e.location}. File {e.file_path} already exists. '
                           'Use --overwrite to overwrite assets.') from e

    # prepare radar payload
    codemeta = CodemetaMetadata()
    codemeta.fetch(args.CODEMETA_LOCATION)
    codemeta.fetch_authors(args.CREATORS_LOCATIONS)
    codemeta.fetch_contributors(args.CONTRIBUTORS_LOCATIONS)
    codemeta.compute_names()
    codemeta.remove_doubles()
    if args.SORT_AUTHORS:
        codemeta.sort_persons()

    codemeta.data['name'] = '{name} ({version})'.format(**codemeta.data)  # override name/title to include version

    if not codemeta.data.get('copyrightHolder'):
        codemeta.data['copyrightHolder'] = [{
            'name': 'The authors'
        }]

    radar_metadata = RadarMetadata(codemeta.data, args.RADAR_EMAIL, args.RADAR_BACKLINK)
    radar_dict = radar_metadata.as_dict()

    if not args.DRY:
        # obtain oauth token
        headers = fetch_radar_token(args.RADAR_URL, args.RADAR_CLIENT_ID, args.RADAR_CLIENT_SECRET,
                                    args.RADAR_REDIRECT_URL, args.RADAR_USERNAME, args.RADAR_PASSWORD)

        # update or create radar dataset
        if radar_dict.get('id'):
            dataset_id = update_radar_dataset(args.RADAR_URL, radar_dict.get('id'), headers, radar_dict)
        else:
            dataset_id = create_radar_dataset(args.RADAR_URL, args.RADAR_WORKSPACE_ID, headers, radar_dict)

        # upload assets
        upload_radar_assets(args.RADAR_URL, dataset_id, headers, args.ASSETS, radar_path)
    else:
        print(json.dumps(radar_dict))

    if args.SMTP_SERVER and args.NOTIFICATION_EMAIL:
        radar_url = f'{args.RADAR_URL}/radar/de/workspace/{args.RADAR_WORKSPACE_ID}.{args.RADAR_CLIENT_ID}'

        send_mail(
            args.SMTP_SERVER, args.RADAR_EMAIL, args.NOTIFICATION_EMAIL,
            'New RADAR release ready to publish',
            'A new RADAR release has been uploaded by a CI pipeline.\n\n'
            f'Please visit {radar_url} to publish this release.'
        )

    try:
        tmp_dir.cleanup()
    except UnboundLocalError:
        pass


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
