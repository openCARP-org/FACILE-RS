import sys
from os import path

import pytest

from facile_rs.utils.cli import main

SCRIPT_DIR = path.dirname(path.realpath(__file__))
METADATA_DIR = path.join(path.dirname(SCRIPT_DIR), 'utils', 'metadata', 'tests')

CODEMETA_BASENAME = 'codemeta_test.json'
CODEMETA_LOCATION = path.join(METADATA_DIR, CODEMETA_BASENAME)
CREATORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_authors_test.json')
CONTRIBUTORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_contributors_test.json')
ASSETS = [path.join(METADATA_DIR, 'codemeta_test.json'), '']


def test_error_zenodo_asset_exists(monkeypatch, tmp_path, capsys):
    """
    Error is raised when an object with the same name as an asset already exists in the Zenodo path.
    """
    zenodo_path = tmp_path / 'zenodo_path'
    zenodo_path.mkdir()
    # Create a dummy file in the zenodo path to simulate an existing asset
    (zenodo_path / CODEMETA_BASENAME).touch()
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'zenodo',
                            'upload',
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--zenodo-path', str(zenodo_path),
                            '--zenodo-url', 'https://sandbox.zenodo.org',
                            '--zenodo-token', '1234567890',
                            '--dry',
                            *ASSETS
                        ])
    with pytest.raises(SystemExit, match='^2$'):
        main()
    captured = capsys.readouterr().err
    assert 'already exists' in captured


def test_cli_dry(monkeypatch, tmp_path):
    """
    Test that the function runs with required CLI options in dry mode.
    """
    zenodo_path = tmp_path / 'zenodo_path'
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'zenodo',
                            'upload',
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--zenodo-path', str(zenodo_path),
                            '--zenodo-url', 'https://sandbox.zenodo.org',
                            '--zenodo-token', '1234567890',
                            '--dry'
                        ])
    main()
