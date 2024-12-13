import pytest
import sys
from os import path

from facile_rs.create_zenodo import main

SCRIPT_DIR = path.dirname(path.realpath(__file__))
METADATA_DIR = path.join(path.dirname(SCRIPT_DIR), 'utils', 'metadata', 'tests')

CODEMETA_LOCATION = path.join(METADATA_DIR, 'codemeta_test.json')
CREATORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_authors_test.json')
CONTRIBUTORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_contributors_test.json')
ASSETS = [path.join(METADATA_DIR, 'codemeta_test.json'), '']


def test_error_zenodo_path_exists(monkeypatch, tmp_path, capsys):
    zenodo_path = tmp_path / 'zenodo_path'
    zenodo_path.mkdir()
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--zenodo-path', str(zenodo_path),
                            '--zenodo-url', 'https://sandbox.zenodo.org',
                            '--zenodo-token', '1234567890',
                            '--dry'
                        ])
    with pytest.raises(SystemExit, match='^2$'):
        main()
    captured = capsys.readouterr().err
    assert 'already exists' in captured


def test_cli_dry(monkeypatch, tmp_path):
    zenodo_path = tmp_path / 'zenodo_path'
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--zenodo-path', str(zenodo_path),
                            '--zenodo-url', 'https://sandbox.zenodo.org',
                            '--zenodo-token', '1234567890',
                            '--dry'
                        ])
    main()
