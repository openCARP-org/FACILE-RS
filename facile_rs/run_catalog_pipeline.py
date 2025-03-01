#!/usr/bin/env python3
import logging

import frontmatter
from slugify import slugify

from .utils import cli
from .utils.grav import collect_pages
from .utils.http import fetch_dict

logger = logging.getLogger(__file__)


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('--grav-path', dest='GRAV_PATH', required=True,
                        help='Path to the grav repository directory.')
    parser.add_argument('--pipeline', dest='PIPELINE', required=True,
                        help='Name of the pipeline as specified in the GRAV metadata.')
    parser.add_argument('--catalog-location', dest='CATALOG_LOCATION', required=True,
                        help='Location of the main catalog in JSON format (locally or on Zenodo)')
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')
    return parser


def main(args):
    # loop over the found pages and write the content into the files
    for page_path, page, source in collect_pages(args.GRAV_PATH, args.PIPELINE):
        catalog_data = fetch_dict(args.CATALOG_LOCATION)

        if list(catalog_data.keys()) == ['hits', 'aggregations', 'links']:
            for catalog_item in catalog_data['hits']['hits']:
                title = catalog_item['metadata'].get('title')
                description = catalog_item['metadata'].get('description', '')
                slug = slugify(title)

                md_path = page_path.parent / slug / 'catalog-item.md'

                # create directories in the grav tree
                md_path.parent.mkdir(parents=True, exist_ok=True)

                # create page metadata
                page_metadata = {
                    key: catalog_item['metadata'].get(key)
                    for key in ['title', 'description', 'doi', 'publication_date', 'resource_type',
                                'creators', 'keywords', 'version', 'license']
                }
                page_metadata['slug'] = slug
                page_metadata['doi_url'] = catalog_item['doi_url']

                page_content = description

                try:
                    page = frontmatter.load(md_path)
                    page.content = page_content
                    page.metadata.update(page_metadata)
                except FileNotFoundError:
                    page = frontmatter.Post(page_content, **page_metadata)

                # write the grav file
                logger.info('writing to %s', md_path)
                md_path.write_text(frontmatter.dumps(page))
        else:
            raise RuntimeError('This pipeline can only process input from the invenio API.')
