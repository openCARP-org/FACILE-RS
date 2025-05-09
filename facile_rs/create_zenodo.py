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
import json

from .utils import cli, setup_assets_path, setup_tmp_assets_path
from .utils.exceptions import AssetExistsError, ParserError
from .utils.http import fetch_files
from .utils.mail import send_mail
from .utils.metadata import CodemetaMetadata, ZenodoMetadata
from .utils.zenodo import create_zenodo_dataset, update_zenodo_dataset, upload_zenodo_assets


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
    parser.add_argument('--zenodo-path', dest='ZENODO_PATH',
                        help='Path to the local directory, where the assets are collected before upload. '
                             'Optional: if not provided, a temporary directory is used.')
    parser.add_argument('--zenodo-url', dest='ZENODO_URL', required=True,
                        help='URL of the Zenodo service. Test environment available at https://sandbox.zenodo.org')
    parser.add_argument('--zenodo-token', dest='ZENODO_TOKEN', required=True,
                        help='Zenodo personal token.')
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
    # setup the zenodo directory
    if args.ZENODO_PATH is None:
        zenodo_path, tmp_dir = setup_tmp_assets_path()
    else:
        zenodo_path = setup_assets_path(args.ZENODO_PATH, exist_ok=True)

    # collect assets
    try:
        fetch_files(args.ASSETS, zenodo_path, headers={
            args.ASSETS_TOKEN_NAME: args.ASSETS_TOKEN
        }, overwrite=args.OVERWRITE)
    except AssetExistsError as e:
        raise ParserError(f'Could not fetch {e.location}. File {e.file_path} already exists. '
                           'Use --overwrite to overwrite assets.') from e

    # prepare Zenodo payload
    codemeta = CodemetaMetadata()
    codemeta.fetch(args.CODEMETA_LOCATION)
    codemeta.fetch_authors(args.CREATORS_LOCATIONS)
    codemeta.fetch_contributors(args.CONTRIBUTORS_LOCATIONS)
    codemeta.compute_names()
    codemeta.remove_doubles()
    if args.SORT_AUTHORS:
        codemeta.sort_persons()

    # override name/title to include version
    codemeta.data['name'] = '{name} ({version})'.format(**codemeta.data)

    zenodo_metadata = ZenodoMetadata(codemeta.data)
    zenodo_dict = zenodo_metadata.as_dict()

    if not args.DRY:
        # update or create Zenodo dataset
        zenodo_id = None
        if 'identifier' in codemeta.data and isinstance(codemeta.data['identifier'], list):
            for identifier in codemeta.data['identifier']:
                if identifier.get('propertyID') == 'Zenodo':
                    zenodo_id = identifier['value']

        if zenodo_id:
            dataset_id = update_zenodo_dataset(args.ZENODO_URL, zenodo_id, args.ZENODO_TOKEN, zenodo_dict)
        else:
            dataset_id = create_zenodo_dataset(args.ZENODO_URL, args.ZENODO_TOKEN, zenodo_dict)

        # upload assets
        upload_zenodo_assets(args.ZENODO_URL, dataset_id, args.ZENODO_TOKEN, args.ASSETS, zenodo_path)

        if args.SMTP_SERVER and args.NOTIFICATION_EMAIL:
            zenodo_url = f'{args.ZENODO_URL}/uploads/{dataset_id}'

            send_mail(
                args.SMTP_SERVER, args.NOTIFICATION_EMAIL, args.NOTIFICATION_EMAIL,
                'New Zenodo release ready to publish',
                'A new Zenodo release has been uploaded by a CI pipeline.\n\n'
                f'Please visit {zenodo_url} to publish this release.'
            )

    try:
        tmp_dir.cleanup()
    except UnboundLocalError:
        pass

    else:
        print(json.dumps(zenodo_dict))


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
