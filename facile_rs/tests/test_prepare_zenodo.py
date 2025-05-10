import json
import sys
from os import path

from facile_rs.utils.cli import main

SCRIPT_DIR = path.dirname(path.realpath(__file__))
METADATA_DIR = path.join(path.dirname(SCRIPT_DIR), 'utils', 'metadata', 'tests')

CODEMETA_LOCATION = path.join(METADATA_DIR, 'codemeta_test.json')
ZENODO_URL = 'https://sandbox.zenodo.org'
ZENODO_TOKEN = 'testtoken'


def test_dry_nocodemeta_cli(monkeypatch, capsys):
    """
    Test the function runs with CLI options and that the Zenodo metadata is printed in
    the standard output in dry mode.
    """
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'zenodo',
                            'prepare',
                            '--zenodo-url', ZENODO_URL,
                            '--zenodo-token', ZENODO_TOKEN,
                            '--dry'
                        ])
    main()
    captured = json.loads(capsys.readouterr().out)
    assert 'metadata' in captured
    assert captured['metadata'].get('title', '') == 'in preparation'


def test_dry_env(monkeypatch, capsys):
    """
    Test the function runs with options set as environment variables and
    that the CodeMeta metadata is handled correctly.
    """
    monkeypatch.setenv('CODEMETA_LOCATION', CODEMETA_LOCATION)
    monkeypatch.setenv('ZENODO_URL', ZENODO_URL)
    monkeypatch.setenv('ZENODO_TOKEN', ZENODO_TOKEN)
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'zenodo',
                            'prepare',
                            '--dry'
                        ])
    main()
    captured = json.loads(capsys.readouterr().out)
    assert 'metadata' in captured
    # Test if the title is correctly set to the name and version of the codemeta file
    with open(CODEMETA_LOCATION) as f:
        codemeta = json.load(f)
    codemeta_name = codemeta.get('name')
    codemeta_version = codemeta.get('version')
    assert captured['metadata'].get('title', '') == f'{codemeta_name} ({codemeta_version}, in preparation)'
