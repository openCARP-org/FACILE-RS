#!/usr/bin/env python3

"""Create a release in GitLab using the GitLab REST API.

Description
-----------

This script creates a release in GitLab using the GitLab REST API.
A tag for the release needs to be created beforehand and provided to the script.

Usage
-----

.. argparse::
   :module: facile_rs.create_release
   :func: create_parser
   :prog: create_release.py

"""
import json
import logging

import requests

from .utils import cli

logger = logging.getLogger(__file__)


def create_parser(add_help=True):
    parser = cli.Parser(add_help=add_help)

    parser.add_argument('ASSETS', nargs='*', default=[],
                        help='Assets to be included in the release.')
    parser.add_argument('--release-tag', dest='RELEASE_TAG', required=True,
                        help='Tag for the release.')
    parser.add_argument('--release-description', dest='RELEASE_DESCRIPTION',
                        help='Description for the release.')
    parser.add_argument('--release-api-url', dest='RELEASE_API_URL', required=True,
                        help='API URL to create the release. Example: https://gitlab.com/api/v4/projects/123/releases')
    parser.add_argument('--private-token', dest='PRIVATE_TOKEN', required=True,
                        help='The PRIVATE_TOKEN to be used with the GitLab API.')
    parser.add_argument('--dry', action='store_true', dest='DRY',
                        help='Perform a dry run, do not perform the final request.')
    parser.add_argument('--log-level', dest='LOG_LEVEL', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='LOG_FILE',
                        help='Path to the log file')

    return parser


def main(args):
    if '/api/v4/projects/' not in args.RELEASE_API_URL or '/releases' not in args.RELEASE_API_URL:
        logger.warning('Warning: the RELEASE_API_URL seems incorrect. '
                       'It should be formed like: https://<gitlab_instance_url>/api/v4/projects/<project_id>/releases')

    assets = []
    for asset_location in args.ASSETS:
        assets.append({
            'name': asset_location.split('/')[-1],
            'url': asset_location
        })

    release_json = {
        'name': args.RELEASE_TAG,
        'tag_name': args.RELEASE_TAG
    }

    if args.RELEASE_DESCRIPTION:
        release_json['description'] = args.RELEASE_DESCRIPTION.strip()

    if assets:
        release_json['assets'] = {
            'links': assets
        }

    if args.DRY:
        print(json.dumps(release_json))
    else:
        logging.debug('release_json = %s', release_json)
        response = requests.post(args.RELEASE_API_URL, headers={
            'Content-Type': 'application/json',
            'Private-Token': args.PRIVATE_TOKEN
        }, json=release_json)
        response.raise_for_status()


def main_deprecated():
    cli.main_deprecated(__name__)


if __name__ == "__main__":
    main_deprecated()
