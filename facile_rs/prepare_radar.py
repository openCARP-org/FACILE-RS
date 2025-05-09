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
import json
from pathlib import Path

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
        doi_url = 'https://doi.org/' + doi

        if args.CODEMETA_LOCATION:
            codemeta.data['@id'] = doi_url
            doi_entry = {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': doi
            }
            radar_entry = {
                '@type': 'PropertyValue',
                'propertyID': 'RADAR',
                'value': dataset_id
            }
            if 'identifier' in codemeta.data and isinstance(codemeta.data['identifier'], list):
                found_doi = False
                found_radar = False
                for identifier in codemeta.data['identifier']:
                    if identifier.get('propertyID') == 'DOI':
                        identifier['value'] = doi
                        found_doi = True
                    elif identifier.get('propertyID') == 'RADAR':
                        identifier['value'] = dataset_id
                        found_radar = True
                if not found_doi:
                    codemeta.data['identifier'].append(doi_entry)
                if not found_radar:
                    codemeta.data['identifier'].append(radar_entry)
            else:
                codemeta.data['identifier'] = [doi_entry, radar_entry]

            Path(args.CODEMETA_LOCATION).expanduser().write_text(codemeta.to_json())
        else:
            print(dataset)
    else:
        print(json.dumps(radar_dict))


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
