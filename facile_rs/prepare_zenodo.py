#!/usr/bin/env python3

"""Create an empty archive in Zenodo to reserve a DOI and a Zenodo ID.

Description
-----------

This script creates an empty archive in Zenodo in order to reserve a DOI and a Zenodo ID.
Both are stored in the CodeMeta metadata file provided as input and can be later used by the script ``create_zenodo.py``
to populate the Zenodo archive.

Usage
-----

.. argparse::
    :module: facile_rs.prepare_zenodo
    :func: create_parser
    :prog: prepare_zenodo.py

"""

import argparse
from pathlib import Path

from .utils import cli, settings
from .utils.metadata import CodemetaMetadata, ZenodoMetadata
from .utils.zenodo import create_zenodo_dataset, prepare_zenodo_dataset


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)
    parser.add_argument('--codemeta-location', dest='codemeta_location',
                        help='Location of the main codemeta.json JSON file')
    parser.add_argument('--zenodo-url', dest='zenodo_url',
                        help='URL of the Zenodo service. Test environment available at https://sandbox.zenodo.org')
    parser.add_argument('--zenodo-token', dest='zenodo_token',
                        help='Zenodo personal token.')
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
        'ZENODO_URL',
        'ZENODO_TOKEN'
    ])

    if settings.CODEMETA_LOCATION:
        codemeta = CodemetaMetadata()
        codemeta.fetch(settings.CODEMETA_LOCATION)
        name = '{name} ({version}, in preparation)'.format(**codemeta.data)
    else:
        name = 'in preparation'

    zenodo_metadata = ZenodoMetadata({'name': name})
    zenodo_dict = zenodo_metadata.as_dict()

    if not settings.DRY:
        # create Zenodo dataset
        dataset_id = create_zenodo_dataset(settings.ZENODO_URL, settings.ZENODO_TOKEN, zenodo_dict)
        dataset = prepare_zenodo_dataset(settings.ZENODO_URL, dataset_id, settings.ZENODO_TOKEN)

        doi = dataset.get('metadata', {}).get('doi', {})
        doi_url = 'https://doi.org/' + doi

        # Update Codemeta file with DOI and Zenodo ID
        if settings.CODEMETA_LOCATION:
            codemeta.data['@id'] = doi_url
            doi_entry = {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': doi
            }
            zenodo_entry = {
                '@type': 'PropertyValue',
                'propertyID': 'Zenodo',
                'value': dataset_id
            }
            if 'identifier' in codemeta.data and isinstance(codemeta.data['identifier'], list):
                found_doi = False
                found_zenodo = False
                for identifier in codemeta.data['identifier']:
                    if identifier.get('propertyID') == 'DOI':
                        identifier['value'] = doi
                        found_doi = True
                    elif identifier.get('propertyID') == 'Zenodo':
                        identifier['value'] = dataset_id
                        found_zenodo = True
                if not found_doi:
                    codemeta.data['identifier'].append(doi_entry)
                if not found_zenodo:
                    codemeta.data['identifier'].append(zenodo_entry)
            else:
                codemeta.data['identifier'] = [doi_entry, zenodo_entry]

            Path(settings.CODEMETA_LOCATION).expanduser().write_text(codemeta.to_json())
        else:
            print(dataset)


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
