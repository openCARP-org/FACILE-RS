#!/usr/bin/env python3

"""Create an empty archive in the RADAR service to reserve a DOI and a RADAR ID.

Description
-----------

This script creates an empty archive in the RADAR service in order to reserve a DOI and a RADAR ID.
Both are stored in the CodeMeta metadata file provided as input and can be later used by the script ``create_radar.py``
to populate the RADAR archive.

Usage
-----

.. argparse::
    :module: facile_rs.prepare_radar
    :func: create_parser
    :prog: prepare_radar.py

"""
from pathlib import Path

from rich import print

from .utils import cli
from .utils.metadata import CodemetaMetadata, RadarMetadata
from .utils.radar import create_radar_dataset, fetch_radar_token, prepare_radar_dataset


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('--codemeta-location', dest='CODEMETA_LOCATION',
                        help='Location of the main codemeta.json JSON file')
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
    parser.add_argument('--keep-previous-doi', action='store_true', dest='KEEP_PREVIOUS_DOI',
                        help='When creating a new version, keep the previous DOI in the Codemeta file, '
                        'in the field "isBasedOn". '
                        'By default, the previous DOI is removed.')
    parser.add_argument('--dry', action='store_true', dest='DRY',
                        help='Perform a dry run, do not upload anything.')
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')
    return parser


def main(args):
    if args.CODEMETA_LOCATION:
        codemeta = CodemetaMetadata()
        codemeta.fetch(args.CODEMETA_LOCATION)

        name = '{name} ({version}, in preparation)'.format(**codemeta.data)
    else:
        name = 'in preparation'

    radar_metadata = RadarMetadata({'name': name}, args.RADAR_EMAIL, args.RADAR_BACKLINK)
    radar_dict = radar_metadata.as_dict()

    if not args.DRY:
        # obtain oauth token
        headers = fetch_radar_token(args.RADAR_URL, args.RADAR_CLIENT_ID, args.RADAR_CLIENT_SECRET,
                                    args.RADAR_REDIRECT_URL, args.RADAR_USERNAME, args.RADAR_PASSWORD)

        # create radar dataset
        dataset_id = create_radar_dataset(args.RADAR_URL, args.RADAR_WORKSPACE_ID, headers, radar_dict)
        dataset = prepare_radar_dataset(args.RADAR_URL, dataset_id, headers)

        doi = dataset.get('descriptiveMetadata', {}).get('identifier', {}).get('value')

        if args.CODEMETA_LOCATION:
            codemeta.update_identifier(new_doi=doi, new_archive_id=dataset_id, archive_type='RADAR',
                                       keep_previous_doi=args.KEEP_PREVIOUS_DOI)

            Path(args.CODEMETA_LOCATION).expanduser().write_text(codemeta.to_json())
        else:
            print(dataset)
    else:
        print(radar_dict)


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
