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

from .utils import cli
from .utils.grav import collect_pages

logger = logging.getLogger(__file__)

FIGURE_PATTERN = r'\.\. figure\:\:\s(.+?)\s'

REF_PATTERN = r'\:ref\:\`(.+?)\s\<(.+?)\>\`'

METADATA_PATTERN = r'__(.*)__ = [\']([^\']*)[\']'
METADATA_RUN_PATTERN = r'EXAMPLE_(.*) = [\']([^\']*)[\']'


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('--grav-path', dest='GRAV_PATH', required=True,
                        help='Path to the grav repository directory.')
    parser.add_argument('--pipeline', dest='PIPELINE', required=True,
                        help='Name of the pipeline as specified in the GRAV metadata.')
    parser.add_argument('--pipeline-source', dest='PIPELINE_SOURCE', required=True,
                        help='Path to the source directory for the pipeline.')
    parser.add_argument('--pipeline-images', dest='PIPELINE_IMAGES',
                        help='Path to the images directory for the pipeline.')
    parser.add_argument('--pipeline-header', dest='PIPELINE_HEADER',
                        help='Path to the header template.')
    parser.add_argument('--pipeline-footer', dest='PIPELINE_FOOTER',
                        help='Path to the footer template.')
    parser.add_argument('--pipeline-refs', dest='PIPELINE_REFS',
                        help='Path to the refs yaml file.')
    parser.add_argument('--output-html', action='store_true', dest='OUTPUT_HTML',
                        help='Output HTML files instead of markdown')
    parser.add_argument('--mathjax-location', dest='MATHJAX_LOCATION',
                        default='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js',
                        help='Location of the MathJax script for math rendering in HTML output. '
                             'This option is only used if --output-html is set. '
                             'Set to empty string to disable MathJax.')
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')
    return parser


def main(args):
    # compile patterns
    ref_pattern = re.compile(REF_PATTERN)
    figure_pattern = re.compile(FIGURE_PATTERN)

    # get the source path
    source_path = Path(args.PIPELINE_SOURCE).expanduser()

    # get the images path
    if args.PIPELINE_IMAGES:
        images_path = Path(args.PIPELINE_IMAGES).expanduser()
    else:
        images_path = None

    # read header
    if args.PIPELINE_HEADER:
        header = Path(args.PIPELINE_HEADER).expanduser().read_text()
    else:
        header = ''
    if args.OUTPUT_HTML:
        header_prefix = "<html><head><meta charset=\"utf-8\">"
        # Add mathjax script for math rendering
        if args.MATHJAX_LOCATION:
            header_prefix += f"<script id=\"MathJax-script\" async src=\"{args.MATHJAX_LOCATION}\"></script>"
        header_prefix += "</head><body>"
        header = header_prefix + header

    # read footer
    if args.PIPELINE_FOOTER:
        footer = Path(args.PIPELINE_FOOTER).expanduser().read_text()
    else:
        footer = ''
    if args.OUTPUT_HTML:
        footer = footer + "</body></html>"

    # read refs
    if args.PIPELINE_REFS:
        refs_path = Path(args.PIPELINE_REFS).expanduser()
        refs = yaml.safe_load(refs_path.read_text())
    else:
        refs = {}

    # loop over all experiments
    for page_path, page, _ in collect_pages(args.GRAV_PATH, args.PIPELINE):
        for root, dirs, files in os.walk(source_path):
            # skip source_path itself
            if root != source_path:
                root_path = Path(root)
                run_path = root_path / 'run.py'
                init_path = root_path / '__init__.py'
                if args.OUTPUT_HTML:
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
                        if args.OUTPUT_HTML:
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

                    q2a_tags = metadata.get('q2a_tags', '')
                    wrapped_q2a_tags = ''
                    if q2a_tags:
                        wrapped_q2a_tags += f'[q2a tags="{q2a_tags}"]\n'

                    content = header + titleString + body + wrapped_q2a_tags + footer

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
                    if args.OUTPUT_HTML:
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
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
