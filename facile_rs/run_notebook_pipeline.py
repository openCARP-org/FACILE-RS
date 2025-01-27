#!/usr/bin/env python3

"""Create dummy pages and links for a set of Jupyter notebooks in a Grav CMS repository.

Description
-----------

This script parses a tree of Jupyter notebooks and creates dummy pages and links in a Grav CMS repository.

Contrary to the bibtex and markdown pipelines, this script does not copy one file to one page in Grav,
but creates a tree of pages below one page (given by the pipeline header). it processes all ``.ipynb``files.

The PIPELINE and PIPELINE_SOURCE options are used in the same way as in ``run_markdown_pipeline.py``.

Please refer to https://git.opencarp.org/openCARP/onboarding for an example setup.

Usage
-----

.. argparse::
    :module: facile_rs.run_notebook_pipeline
    :func: create_parser
    :prog: run_notebook_pipeline.py

"""

import argparse
import json
import logging
import os
import re
from pathlib import Path

import frontmatter

from .utils import cli, settings
from .utils.grav import collect_pages

logger = logging.getLogger(__file__)


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)

    parser.add_argument('--grav-path', dest='grav_path',
                        help='Path to the grav repository directory.')
    parser.add_argument('--pipeline', dest='pipeline',
                        help='Name of the pipeline as specified in the GRAV metadata.')
    parser.add_argument('--pipeline-source', dest='pipeline_source',
                        help='Path to the source directory for the pipeline.')
    parser.add_argument('--output-html', action='store_true',
                        help='Output HTML files instead of markdown')
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

    # get the source path
    source_path = Path(settings.PIPELINE_SOURCE).expanduser()

    # loop over all notebooks
    for page_path, page, _ in collect_pages(settings.GRAV_PATH, settings.PIPELINE):

        multicard_page = frontmatter.load(page_path)
        for multicard in multicard_page['multicards']:
            multicard_path = Path(source_path) / multicard['key']

            for root, dirs, files in os.walk(multicard_path):
                if '.ipynb_checkpoints' not in root:
                    for file_name in files:
                        if file_name.endswith('.ipynb'):
                            file_path = Path(root) / file_name
                            md_path = Path(root.replace(str(source_path), str(page_path.parent)).lower()) / 'default.md'

                            # create directories in the grav tree
                            md_path.parent.mkdir(parents=True, exist_ok=True)

                            # create page metadata
                            page_metadata = {
                                'notebook_url': str(file_path).replace(str(source_path), '').lstrip('/')
                            }

                            # load the notebook as json and update the page metadata with information of the first cell
                            notebook = json.loads(file_path.read_text())
                            first_cell = next(iter(notebook.get('cells', [])), {})
                            for line in first_cell.get('source', []):
                                for key in ['title', 'subtitle', 'description', 'image', 'thumbnail']:
                                    match = re.match(fr'^{key}:\s(.*?)$', line)
                                    if match:
                                        page_metadata[key] = match.group(1)

                            try:
                                page = frontmatter.load(md_path)
                                page.content = ''
                                page.metadata.update(page_metadata)

                            except FileNotFoundError:
                                page = frontmatter.Post('', **page_metadata)

                            # write the grav file
                            logger.info('writing to %s', md_path)
                            md_path.write_text(frontmatter.dumps(page))


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
