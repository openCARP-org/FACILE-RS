#!/usr/bin/env python3

"""Compile and copy the content of bibtex files to a Grav CMS repository.

Description
-----------

This script compiles and copies the content of bibtex files in a similar way as run_markdown_pipeline.
A CSL can be provided.
Please refer to https://git.opencarp.org/openCARP/publications for an example setup.

Usage
-----

.. argparse::
    :module: facile_rs.run_bibtex_pipeline
    :func: create_parser
    :prog: run_bibtex_pipeline.py

"""
import logging
from pathlib import Path

import frontmatter
import pypandoc

from .utils import cli
from .utils.grav import collect_pages

logger = logging.getLogger(__file__)

TEMPLATE = '''
---
nocite: '@*'
---
'''


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('--grav-path', dest='GRAV_PATH', required=True,
                        help='Path to the grav repository directory.')
    parser.add_argument('--pipeline', dest='PIPELINE', required=True,
                        help='Name of the pipeline as specified in the GRAV metadata.')
    parser.add_argument('--pipeline-source', dest='PIPELINE_SOURCE', required=True,
                        help='Path to the source directory for the pipeline.')
    parser.add_argument('--pipeline-csl', dest='PIPELINE_CSL',
                        help='Path to the source directory for the pipeline.')
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')
    return parser


def main(args):
    # loop over the found pages and write the content into the files
    for page_path, page, source in collect_pages(args.GRAV_PATH, args.PIPELINE):
        source_path = Path(args.PIPELINE_SOURCE).expanduser() / source
        logger.debug('page_path = %s, source_path = %s', page_path, source_path)

        extra_args = [f'--bibliography={source_path}', '--citeproc', '--wrap=preserve']
        if args.PIPELINE_CSL:
            extra_args.append(f'--csl={args.PIPELINE_CSL}')

        page.content = pypandoc.convert_text(TEMPLATE, to='html', format='md',
                                             extra_args=extra_args)

        logger.info('writing publications to %s', page_path)
        open(page_path, 'w').write(frontmatter.dumps(page))


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
