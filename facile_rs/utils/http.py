import json
import logging
import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml

from .exceptions import AssetExistsError

logger = logging.getLogger(__file__)


def fetch_files(locations, path, headers={}, overwrite=False):
    """
    Fetch files from local locations or from URLs and save them at the given path.

    :param locations: list of URL or paths to the files
    :type locations: list of str
    :param path: path where the files should be saved
    :type path: str
    """
    for location in locations:
        fetch_file(location, path, headers=headers, overwrite=overwrite)


def fetch_file(location, path, file_name=None, headers={}, overwrite=False):
    """
    Fetch one file from a local location or an URL and save them at the given path.
    If no file_name is provided it will be created from the location

    :param location: URL or path to the file
    :type locations: str or Path
    :param path: path where the file should be saved
    :type path: str or Path
    :param file_name: name of the file
    :type path: str
    """
    parsed_url = urlparse(location)
    target = path / (file_name or parsed_url.path.split('/')[-1])

    if target.exists() and not overwrite:
        raise AssetExistsError(location, target)

    logger.debug('location = %s, target = %s', location, target)
    if parsed_url.scheme:
        response = requests.get(location, headers=headers)
        response.raise_for_status()
        with open(target, 'wb') as f:
            f.write(response.content)

    else:
        shutil.copyfile(location, target)


def fetch_dict(location):
    """Fetch data from a JSON or YAML file and return it as a dictionary.

    :param location: URL or path to the file (allowed extensions: .json, .yml, .yaml)
    :type location: str
    :return: Dictionary containing file data
    :rtype: dict
    """
    parsed_url = urlparse(location)
    if parsed_url.scheme:
        logger.debug('location = %s', location)

        response = requests.get(location)
        response.raise_for_status()

        if parsed_url.path.endswith('.json'):
            return json.loads(response.text)
        elif parsed_url.path.endswith('.yml') or parsed_url.path.endswith('.yaml'):
            return yaml.safe_load(response.text)
        else:
            raise RuntimeError('{} is not a JSON or YAML file.')
    else:
        path = Path(location).expanduser()
        with open(Path(location).expanduser()) as f:
            if path.suffix == '.json':
                return json.load(f)
            elif path.suffix in ['.yml', '.yaml']:
                return yaml.safe_load(f.read())
            else:
                raise RuntimeError('{} is not a JSON or YAML file.')


def fetch_json(location):
    """
    Fetch JSON data from the given location.

    :param location: URL to the JSON data
    :type location: str
    :return: JSON-encoded response
    """
    response = requests.get(location, headers={'Accept': 'application/json'})
    response.raise_for_status()
    return response.json()
