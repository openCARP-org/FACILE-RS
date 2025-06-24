#!/usr/bin/env python3

"""Create an empty archive in Zenodo to reserve a DOI and a Zenodo ID.

Description
-----------

This script creates an empty archive in Zenodo in order to reserve a DOI and a Zenodo ID.
Both are stored in the CodeMeta metadata file provided as input and can be later used by the script ``create_zenodo.py``
to populate the Zenodo archive.

Optionally, the script can create a new version from an existing Zenodo record.
See the option --zenodo-version-update for more details.

Usage
-----

.. argparse::
    :module: facile_rs.prepare_zenodo
    :func: create_parser
    :prog: prepare_zenodo.py

"""
import json
from pathlib import Path

from .utils import cli
from .utils.metadata import CodemetaMetadata, ZenodoMetadata
from .utils.zenodo import create_zenodo_dataset, prepare_zenodo_dataset


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('--codemeta-location', dest='CODEMETA_LOCATION',
                        help='Location of the main codemeta.json JSON file')
    parser.add_argument('--zenodo-url', dest='ZENODO_URL', required=True,
                        help='URL of the Zenodo service. Test environment available at https://sandbox.zenodo.org')
    parser.add_argument('--zenodo-token', dest='ZENODO_TOKEN', required=True,
                        help='Zenodo personal token.')
    parser.add_argument('--zenodo-version-update', dest='ZENODO_VERSION_UPDATE', default=None,
                        help='Enable Zenodo version update. Can be "codemeta" or a Zenodo identifier. '
                        'If omitted, a new Zenodo dataset is created without versioning. '
                        'If set to "codemeta", a Zenodo identifier is searched in the CodeMeta file, and a new version is '
                        'created from it (if found). '
                        'Any other value is considered as a Zenodo identifier: a new version will be created from it. ')
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

    zenodo_metadata = ZenodoMetadata({'name': name})
    zenodo_dict = zenodo_metadata.as_dict()

    # Management of Zenodo versioning
    old_zenodo_id = None
    if args.CODEMETA_LOCATION and args.ZENODO_VERSION_UPDATE == 'codemeta':
        # Check if CodeMeta file contains a Zenodo identifier
        identifiers = codemeta.data.get('identifier', [])
        if not isinstance(identifiers, list):
            identifiers = [identifiers]
        for identifier in identifiers:
            if isinstance(identifier, dict) and identifier.get('propertyID') == 'Zenodo':
                old_zenodo_id = identifier.get('value', None)
    elif args.ZENODO_VERSION_UPDATE is not None:
        # Use the provided Zenodo identifier to create a new version
        old_zenodo_id = args.ZENODO_VERSION_UPDATE

    if not args.DRY:
        # create Zenodo dataset
        dataset_id = create_zenodo_dataset(args.ZENODO_URL, args.ZENODO_TOKEN, zenodo_dict, previous_version=old_zenodo_id)
        dataset = prepare_zenodo_dataset(args.ZENODO_URL, dataset_id, args.ZENODO_TOKEN)

        doi = dataset.get('metadata', {}).get('doi', {})
        doi_url = 'https://doi.org/' + doi

        # Update Codemeta file with DOI and Zenodo ID
        if args.CODEMETA_LOCATION:
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

            Path(args.CODEMETA_LOCATION).expanduser().write_text(codemeta.to_json())
        else:
            print(dataset)
    else:
        print(json.dumps(zenodo_dict))


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
