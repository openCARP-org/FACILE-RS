#!/usr/bin/env python3

"""Extract and copy the content of reStructuredText docstrings of Python scripts to a Grav CMS repository.

Description
-----------

This script extracts and copies the content of reStructuredText docstrings of Python scripts to a Grav CMS repository.

Contrary to the other pipelines, this script does not copy one file to one page in Grav, but creates a tree of pages
below one page (given by the pipeline header). it processes all ``run.py`` and ``__init__.py`` files.

The PIPELINE and PIPELINE_SOURCE options are used in the same way as in ``run_markdown_pipeline.py``.

In addition, PIPELINE_IMAGES specifies a directory where the images from the docstrings are located and PIPELINE_HEADER
and PIPELINE_FOOTER options point to templates which are prepended and appended to each page.

With the PIPELINE_REFS YML file, you can specify replacements for the references in the rst code.

Please refer to https://git.opencarp.org/openCARP/experiments for an example setup.

Usage
-----

.. argparse::
    :module: facile_rs.run_docstring_pipeline
    :func: create_parser
    :prog: run_docstring_pipeline.py

"""

import argparse
import ast
import logging
import os
import re
import shutil
from pathlib import Path

import frontmatter
import pypandoc
import yaml
from PIL import Image
from resizeimage import resizeimage

from .utils import cli, settings
from .utils.grav import collect_pages

logger = logging.getLogger(__file__)

FIGURE_PATTERN = r'\.\. figure\:\:\s(.+?)\s'

REF_PATTERN = r'\:ref\:\`(.+?)\s\<(.+?)\>\`'

METADATA_PATTERN = r'__(.*)__ = [\']([^\']*)[\']'
METADATA_RUN_PATTERN = r'EXAMPLE_(.*) = [\']([^\']*)[\']'


def create_parser(add_help=True):
    parser = argparse.ArgumentParser(add_help=add_help)

    parser.add_argument('--grav-path', dest='grav_path',
                        help='Path to the grav repository directory.')
    parser.add_argument('--pipeline', dest='pipeline',
                        help='Name of the pipeline as specified in the GRAV metadata.')
    parser.add_argument('--pipeline-source', dest='pipeline_source',
                        help='Path to the source directory for the pipeline.')
    parser.add_argument('--pipeline-images', dest='pipeline_images',
                        help='Path to the images directory for the pipeline.')
    parser.add_argument('--pipeline-header', dest='pipeline_header',
                        help='Path to the header template.')
    parser.add_argument('--pipeline-footer', dest='pipeline_footer',
                        help='Path to the footer template.')
    parser.add_argument('--pipeline-refs', dest='pipeline_refs',
                        help='Path to the refs yaml file.')
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

    # compile patterns
    ref_pattern = re.compile(REF_PATTERN)
    figure_pattern = re.compile(FIGURE_PATTERN)

    # get the source path
    source_path = Path(settings.PIPELINE_SOURCE).expanduser()

    # get the images path
    if settings.PIPELINE_IMAGES:
        images_path = Path(settings.PIPELINE_IMAGES).expanduser()
    else:
        images_path = None

    # read header
    if settings.PIPELINE_HEADER:
        header = Path(settings.PIPELINE_HEADER).expanduser().read_text()
    else:
        header = ''
    if settings.OUTPUT_HTML:
        header = "<html><head><meta charset=\"utf-8\"></head><body>" + header

    # read footer
    if settings.PIPELINE_FOOTER:
        footer = Path(settings.PIPELINE_FOOTER).expanduser().read_text()
    else:
        footer = ''
    if settings.OUTPUT_HTML:
        footer = footer + "</body></html>"

    # read refs
    if settings.PIPELINE_REFS:
        refs_path = Path(settings.PIPELINE_REFS).expanduser()
        refs = yaml.safe_load(refs_path.read_text())
    else:
        refs = {}

    # loop over all experiments
    for page_path, page, _ in collect_pages(settings.GRAV_PATH, settings.PIPELINE):
        for root, dirs, files in os.walk(source_path):
            # skip source_path itself
            if root != source_path:
                root_path = Path(root)
                run_path = root_path / 'run.py'
                init_path = root_path / '__init__.py'
                if settings.OUTPUT_HTML:
                    md_path = Path(root.replace(str(source_path), str(page_path.parent)).lower()) / 'default.html'
                else:
                    md_path = Path(root.replace(str(source_path), str(page_path.parent)).lower()) / 'default.md'

                if 'run.py' in files:
                    # read the __init__.py file and obtain the metadata
                    with open(init_path) as f:
                        metadata = dict(re.findall(METADATA_PATTERN, f.read()))

                    # read the run.py file and obtain the metadata
                    with open(run_path) as f:
                        metadata_run = dict(re.findall(METADATA_RUN_PATTERN, f.read()))
                    titleString = ''
                    if 'DESCRIPTIVE_NAME' in metadata_run.keys():
                        titleString = titleString + '<h1>' + metadata_run.get('DESCRIPTIVE_NAME') + '</h1>\n'
                    titleString = titleString \
                            + '<i>See <a href="https://git.opencarp.org/openCARP/experiments/-/blob/master/' \
                            + str(run_path) + '" target="_blank">code</a> in GitLab.</i><br/>\n'
                    if 'AUTHOR' in metadata_run.keys():
                        titleString = titleString + '<i>Author: ' + metadata_run.get('AUTHOR') + '</i>\n'

                    # read the run.py file and obtain the docstring
                    with open(run_path) as f:
                        py_string = f.read()
                        module = ast.parse(py_string)
                        docstring = ast.get_docstring(module)

                    # search for :ref:
                    for m in ref_pattern.finditer(docstring):
                        text, ref = m.group(1), m.group(2)

                        if ref in refs and refs[ref] is not None:
                            target = refs[ref]
                            docstring = docstring.replace(m.group(0), f'`{text} <{target}>`_')
                        else:
                            logger.warning(f'Reference {m.group(0)} missing')
                            docstring = docstring.replace(m.group(0), text)

                    # search for .. figure::
                    images = []
                    for m in figure_pattern.finditer(docstring):
                        figure = m.group(1)
                        image = figure.replace('/images/', '')
                        images.append(image)
                        if settings.OUTPUT_HTML:
                            docstring = docstring.replace(figure, image)
                        else:
                            docstring = docstring.replace(figure, str(Path(root_path.name.lower()) / image))

                    # append image from the metadata to the image list
                    if metadata.get('image'):
                        image_name = metadata.get('image').replace('/images/', '')
                        thumb_name = 'thumb_' + image_name
                        with open(images_path / image_name, 'r+b') as f:
                            with Image.open(f) as image:
                                w, h = image.size
                                if w > 200:
                                    cover = resizeimage.resize_width(image, 200)
                                cover.save(images_path / thumb_name, image.format)
                        images.append(thumb_name)

                    # create content from the docstring using pandoc
                    # we should probably add '--shift-heading-level-by=1' to extra_args but it doesn't
                    # seem to be supported by our pandoc version
                    body = pypandoc.convert_text(docstring, to='html', format='rst',
                                                 extra_args=['--mathjax', '--wrap=preserve'])

                    # convert RST section headers to level 2 headings
                    body = body.replace('<h1 id=', '<h2 id=')
                    body = body.replace('</h1>', '</h2>')
                    content = header + titleString + body + footer

                    # create directories in the grav tree
                    md_path.parent.mkdir(parents=True, exist_ok=True)

                    # update or create markdown file
                    title = metadata.get('title', '')
                    description = metadata.get('description', '')
                    image = metadata.get('image', '').replace('/images/', '')
                    thumb_name = ''
                    if image:
                        thumb_name = 'thumb_' + image


                    try:
                        page = frontmatter.load(md_path)
                        page.content = content
                        page['title'] = title
                        page['description'] = description
                        page['image'] = thumb_name

                    except FileNotFoundError:
                        page = frontmatter.Post(content, title=title, description=description, image=thumb_name)

                    # write the grav file
                    logger.info('writing to %s', md_path)
                    if settings.OUTPUT_HTML:
                        md_path.write_text(content)
                    else:
                        md_path.write_text(frontmatter.dumps(page))

                    # copy images
                    if images_path is not None:
                        for image in images:
                            source = images_path / image
                            destination = md_path.parent / image

                            try:
                                shutil.copy(source, destination)
                                logger.debug(f'Copy image {source} to {destination}')
                            except FileNotFoundError:
                                logger.warning(f'Image {source} missing')

                elif '__init__.py' in files:
                    # create directories in the grav tree
                    md_path.parent.mkdir(parents=True, exist_ok=True)

                    # read the __init__.py file and obtain the metadata
                    with open(init_path) as f:
                        metadata = dict(re.findall(METADATA_PATTERN, f.read()))

                    content = ''
                    metadata = {
                        'title': metadata.get('title', ''),
                        'cards': {
                            'items': '@self.children'
                        }
                    }
                    page = frontmatter.Post(content, **metadata)

                    # write the grav file
                    logger.info('writing to %s', md_path)
                    md_path.write_text(frontmatter.dumps(page))


def main_deprecated():
    cli.cli_call_deprecated(main)


if __name__ == "__main__":
    main_deprecated()
