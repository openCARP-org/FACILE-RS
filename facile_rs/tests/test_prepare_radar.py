import json
import sys
from os import path

from facile_rs.utils.cli import main

SCRIPT_DIR = path.dirname(path.realpath(__file__))
METADATA_DIR = path.join(path.dirname(SCRIPT_DIR), 'utils', 'metadata', 'tests')

CODEMETA_LOCATION = path.join(METADATA_DIR, 'codemeta_test.json')
RADAR_URL = 'https://radar.kit.edu'
RADAR_USERNAME = 'testuser'
RADAR_PASSWORD = 'testpassword'
RADAR_CLIENT_ID = 'testclientid'
RADAR_CLIENT_SECRET = 'testclientsecret'
RADAR_WORKSPACE_ID = 'testworkspaceid'
RADAR_REDIRECT_URL = 'https://example.com'
RADAR_EMAIL = 'testuser@example.com'
RADAR_BACKLINK = 'https://example.com'


def test_dry_nocodemeta_cli(monkeypatch, capsys):
    """
    Test the function runs with CLI options and that the radar metadata is printed in
    the standard output in dry mode.
    """
    monkeypatch.delenv('CODEMETA_LOCATION', raising=False)
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'radar',
                            'prepare',
                            '--radar-url', RADAR_URL,
                            '--radar-username', RADAR_USERNAME,
                            '--radar-password', RADAR_PASSWORD,
                            '--radar-client-id', RADAR_CLIENT_ID,
                            '--radar-client-secret', RADAR_CLIENT_SECRET,
                            '--radar-workspace-id', RADAR_WORKSPACE_ID,
                            '--radar-redirect-url', RADAR_REDIRECT_URL,
                            '--radar-email', RADAR_EMAIL,
                            '--radar-backlink', RADAR_BACKLINK,
                            '--dry'
                        ])
    main()
    captured = json.loads(capsys.readouterr().out)
    assert 'technicalMetadata' in captured
    assert 'descriptiveMetadata' in captured
    assert captured['descriptiveMetadata'].get('title', '') == 'in preparation'


def test_dry_env(monkeypatch, capsys):
    """
    Test the function runs with options set as environment variables and
    that the CodeMeta metadata is handled correctly.
    """
    monkeypatch.setenv('CODEMETA_LOCATION', CODEMETA_LOCATION)
    monkeypatch.setenv('RADAR_URL', RADAR_URL)
    monkeypatch.setenv('RADAR_USERNAME', RADAR_USERNAME)
    monkeypatch.setenv('RADAR_PASSWORD', RADAR_PASSWORD)
    monkeypatch.setenv('RADAR_CLIENT_ID', RADAR_CLIENT_ID)
    monkeypatch.setenv('RADAR_CLIENT_SECRET', RADAR_CLIENT_SECRET)
    monkeypatch.setenv('RADAR_WORKSPACE_ID', RADAR_WORKSPACE_ID)
    monkeypatch.setenv('RADAR_REDIRECT_URL', RADAR_REDIRECT_URL)
    monkeypatch.setenv('RADAR_EMAIL', RADAR_EMAIL)
    monkeypatch.setenv('RADAR_BACKLINK', RADAR_BACKLINK)
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'radar',
                            'prepare',
                            '--dry'
                        ])
    main()
    captured = json.loads(capsys.readouterr().out)
    assert 'technicalMetadata' in captured
    assert 'descriptiveMetadata' in captured

    # Test if the title is correctly set to the name and version of the codemeta file
    with open(CODEMETA_LOCATION) as f:
        codemeta = json.load(f)
    codemeta_name = codemeta.get('name')
    codemeta_version = codemeta.get('version')
    assert captured['descriptiveMetadata'].get('title', '') == f'{codemeta_name} ({codemeta_version}, in preparation)'
