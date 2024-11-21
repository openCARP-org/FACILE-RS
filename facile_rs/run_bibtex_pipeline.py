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

import argparse
import logging
from pathlib import Path

import frontmatter
import pypandoc

from .utils import cli, settings
from .utils.grav import collect_pages

logger = logging.getLogger(__file__)

TEMPLATE = '''
---
nocite: '@*'
---
'''


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)

    parser.add_argument('--grav-path', dest='grav_path',
                        help='Path to the grav repository directory.')
    parser.add_argument('--pipeline', dest='pipeline',
                        help='Name of the pipeline as specified in the GRAV metadata.')
    parser.add_argument('--pipeline-source', dest='pipeline_source',
                        help='Path to the source directory for the pipeline.')
    parser.add_argument('--pipeline-csl', dest='pipeline_csl',
                        help='Path to the source directory for the pipeline.')
    parser.add_argument('--log-level', dest='log_level',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')
    return parser


def main():
    parser = create_parser()

    settings.setup(parser, validate=[
        'GRAV_PATH',
        'PIPELINE',
        'PIPELINE_SOURCE'
    ])

    # loop over the found pages and write the content into the files
    for page_path, page, source in collect_pages(settings.GRAV_PATH, settings.PIPELINE):
        source_path = Path(settings.PIPELINE_SOURCE).expanduser() / source
        logger.debug('page_path = %s, source_path = %s', page_path, source_path)

        extra_args = [f'--bibliography={source_path}', '--citeproc', '--wrap=preserve']
        if settings.PIPELINE_CSL:
            extra_args.append(f'--csl={settings.PIPELINE_CSL}')

        page.content = pypandoc.convert_text(TEMPLATE, to='html', format='md',
                                             extra_args=extra_args)

        logger.info('writing publications to %s', page_path)
        open(page_path, 'w').write(frontmatter.dumps(page))


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
