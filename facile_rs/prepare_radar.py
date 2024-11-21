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

import argparse
from pathlib import Path

from .utils import cli, settings
from .utils.metadata import CodemetaMetadata, RadarMetadata
from .utils.radar import create_radar_dataset, fetch_radar_token, prepare_radar_dataset


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)
    parser.add_argument('--codemeta-location', dest='codemeta_location',
                        help='Location of the main codemeta.json JSON file')
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

    if settings.CODEMETA_LOCATION:
        codemeta = CodemetaMetadata()
        codemeta.fetch(settings.CODEMETA_LOCATION)

        name = '{name} ({version}, in preparation)'.format(**codemeta.data)
    else:
        name = 'in preparation'

    radar_metadata = RadarMetadata({'name': name}, settings.RADAR_EMAIL, settings.RADAR_BACKLINK)
    radar_dict = radar_metadata.as_dict()

    if not settings.DRY:
        # obtain oauth token
        headers = fetch_radar_token(settings.RADAR_URL, settings.RADAR_CLIENT_ID, settings.RADAR_CLIENT_SECRET,
                                    settings.RADAR_REDIRECT_URL, settings.RADAR_USERNAME, settings.RADAR_PASSWORD)

        # create radar dataset
        dataset_id = create_radar_dataset(settings.RADAR_URL, settings.RADAR_WORKSPACE_ID, headers, radar_dict)
        dataset = prepare_radar_dataset(settings.RADAR_URL, dataset_id, headers)

        doi = dataset.get('descriptiveMetadata', {}).get('identifier', {}).get('value')
        doi_url = 'https://doi.org/' + doi

        if settings.CODEMETA_LOCATION:
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

            Path(settings.CODEMETA_LOCATION).expanduser().write_text(codemeta.to_json())
        else:
            print(dataset)


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
