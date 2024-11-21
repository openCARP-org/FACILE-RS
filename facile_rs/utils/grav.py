import logging
import os
from pathlib import Path

import frontmatter

logger = logging.getLogger(__file__)


def collect_pages(grav_path, pipeline_name):
    """
    Collect pages in a GRAV repository which are associated with the given pipeline name.

    :param grav_path: path to the GRAV repository
    :type grav_path: string representing a path segment, or an object implementing the os.PathLike interface
    :param pipeline_name: name of the pipeline
    :type pipeline_name: str
    :return: list of pages as a tuple of (GRAV page location, GRAV page as frontmatter post, source location)
    :rtype: list
    """
    pages_path = Path(grav_path).expanduser() / 'pages'

    # walk the grav repo to find the files with `pipeline: carputils`
    pages = []
    for root, dirs, files in os.walk(pages_path):
        for file_name in files:
            file_path = Path(root) / file_name
            if file_path.suffix == '.md' and file_path.stem not in ['modular']:
                try:
                    page = frontmatter.load(file_path)
                    if page.get('pipeline') == pipeline_name:
                        logger.debug('file_path = %s', file_path)
                        pages.append((file_path, page, page.get('source')))

                except TypeError:
                    # if a file has issues with the metadata, just ignore it
                    pass

    return pages
