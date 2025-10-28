#!/usr/bin/env python3
import datetime
import logging
import shutil

import frontmatter
from slugify import slugify

from .utils import cli
from .utils.grav import collect_pages
from .utils.http import fetch_dict

logger = logging.getLogger(__file__)

DATACITE_URL = 'https://api.datacite.org/dois/'
DATACITE_HEADERS = {
    'User-Agent': 'FACILE-RS/1.0 (https://git.opencarp.org/openCARP/FACILE-RS)'
}

def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('--grav-path', dest='GRAV_PATH', required=True,
                        help='Path to the grav repository directory.')
    parser.add_argument('--pipeline', dest='PIPELINE', required=True,
                        help='Name of the pipeline as specified in the GRAV metadata.')
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')
    return parser


def main(args):
    # loop over the found pages and write the content into the files
    for page_path, page, source in collect_pages(args.GRAV_PATH, args.PIPELINE):
        catalog_metadata = []

        # add pages from zenodo communities
        for catalog_location in page.metadata.get('catalog_locations', []):
            catalog_response = fetch_dict(catalog_location)

            if list(catalog_response.keys()) == ['hits', 'aggregations', 'links']:
                for hit in catalog_response['hits']['hits']:
                    metadata = hit['metadata']

                    catalog_metadata.append({
                        'doi': metadata.get('doi'),
                        'title': metadata.get('title'),
                        'description': metadata.get('description'),
                        'publication_date': metadata.get('publication_date'),
                        'publication_year': datetime.date.fromisoformat(metadata.get('publication_date')).year,
                        'resource_type': metadata.get('resource_type')['title'],
                        'creators': metadata.get('creators'),
                        'keywords': metadata.get('keywords'),
                        'version': metadata.get('version'),
                        'license': metadata.get('license')['id'].upper()
                    })
            else:
                raise RuntimeError('This pipeline can only process input from the invenio API.')

        # add pages from individual dois by querying datacite
        for doi in page.metadata.get('catalog_dois', []):
            datacite_response = fetch_dict(DATACITE_URL + doi, DATACITE_HEADERS)
            datacite_metadata = datacite_response.get('data', {}).get('attributes')

            catalog_metadata.append({
                'doi': doi,
                'title': get_datacite_title(datacite_metadata),
                'description': get_datacite_description(datacite_metadata),
                'publication_date': get_datacite_publication_date(datacite_metadata),
                'publication_year': datacite_metadata.get('publicationYear'),
                'resource_type': datacite_metadata['types'].get('resourceType'),
                'creators': [
                    {
                        'name': creator['name'],
                        'orcid': get_datacite_orcid(creator),
                    } for creator in datacite_metadata.get('creators', [])
                ],
                'keywords': [subject['subject'] for subject in datacite_metadata.get('subjects')],
                'version': datacite_metadata.get('version'),
                'license': get_datacite_license(datacite_metadata)
            })

        for metadata in catalog_metadata:
            metadata['slug'] = slugify(metadata['title'])
            metadata['doi_url'] = f'https://doi.org/{doi}'

            md_path = page_path.parent / metadata['slug'] / 'catalog-item.md'

            # create directories in the grav tree
            md_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                catalog_page = frontmatter.load(md_path)
                catalog_page.content = metadata['description']
                catalog_page.metadata.update(metadata)
            except FileNotFoundError:
                catalog_page = frontmatter.Post(metadata['description'], **metadata)

            # write the grav file
            logger.debug('writing to %s', md_path)
            md_path.write_text(frontmatter.dumps(catalog_page))


        for file_path in page_path.parent.iterdir():
            if file_path.is_dir() and file_path.stem not in [metadata['slug'] for metadata in catalog_metadata]:
                shutil.rmtree(file_path)


def get_datacite_title(metadata):
    for title in metadata.get('titles', []):
        return title['title']


def get_datacite_description(metadata):
    for description in metadata.get('descriptions', []):
        if description['descriptionType'] == 'Abstract':
            return description['description']


def get_datacite_publication_date(metadata):
    for date_type in ['Issued', 'Created']:
        for date in metadata.get('dates', []):
            if date['dateType'] == date_type:
                return date['date']


def get_datacite_orcid(creator):
    for name_identifier in creator.get('nameIdentifiers', []):
        if name_identifier['nameIdentifierScheme'] == 'ORCID':
            return name_identifier['nameIdentifier']


def get_datacite_license(metadata):
    for rights in metadata.get('rightsList', []):
        return rights['rights']
