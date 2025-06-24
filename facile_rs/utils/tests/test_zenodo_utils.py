import json
import os

import pytest

from facile_rs.utils.http import fetch_files
from facile_rs.utils.zenodo import (
    create_zenodo_dataset,
    delete_zenodo_dataset,
    get_zenodo_dataset,
    prepare_zenodo_dataset,
    update_zenodo_dataset,
    upload_zenodo_assets,
)

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
METADATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'metadata', 'tests')

CODEMETA_LOCATION = os.path.join(METADATA_DIR, 'codemeta_test.json')
MINIMAL_METADATA = {
    'metadata': {
        'language': 'eng',
        'title': 'FACILE-RS tests',
    }
}
ZENODO_METADATA_FILE = os.path.join(SCRIPT_DIR, 'zenodo_metadata.json')
ZENODO_TOKEN_PYTEST = os.getenv("ZENODO_TOKEN_PYTEST")
ZENODO_URL = 'https://sandbox.zenodo.org'


# Skip the tests if no Zenodo token is provided
@pytest.mark.skipif(
    os.getenv("ZENODO_TOKEN_PYTEST") is None,
    reason="ZENODO_TOKEN_PYTEST is not set."
)
def test_zenodo_utils(tmp_path):

    record_id = None

    try:

        # Test record creation
        record_id = create_zenodo_dataset(ZENODO_URL,
                                        ZENODO_TOKEN_PYTEST,
                                        MINIMAL_METADATA)
        assert record_id is not None

        # Test DOI reservation
        response_json = prepare_zenodo_dataset(ZENODO_URL, record_id, ZENODO_TOKEN_PYTEST)
        assert 'metadata' in response_json
        assert response_json['metadata']['title'] == MINIMAL_METADATA['metadata']['title']
        assert 'doi' in response_json['metadata']

        # Test record metadata update
        with open(ZENODO_METADATA_FILE) as f:
            metadata = json.load(f)
        update_zenodo_dataset(ZENODO_URL, record_id, ZENODO_TOKEN_PYTEST, metadata)
        record_json = get_zenodo_dataset(ZENODO_URL, record_id, ZENODO_TOKEN_PYTEST)
        assert 'metadata' in record_json
        assert record_json['metadata']['title'] == metadata['metadata']['title']

        # Test asset upload
        zenodo_path = tmp_path / 'zenodo-path'
        zenodo_path.mkdir()
        assets = [CODEMETA_LOCATION, 'https://www.rfc-editor.org/rfc/rfc2606.txt']
        fetch_files(assets, zenodo_path)
        upload_zenodo_assets(ZENODO_URL, record_id, ZENODO_TOKEN_PYTEST, assets, zenodo_path)
        record_json = get_zenodo_dataset(ZENODO_URL, record_id, ZENODO_TOKEN_PYTEST)
        assert 'files' in record_json
        assert len(record_json['files']) == 2
        for file in record_json['files']:
            assert file['key'] in (os.path.basename(asset) for asset in assets)

    finally:

        if record_id is not None:
            delete_zenodo_dataset(ZENODO_URL, record_id, ZENODO_TOKEN_PYTEST)
