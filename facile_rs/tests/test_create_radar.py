import json
import sys
from os import path

import pytest

from facile_rs.utils.cli import main

SCRIPT_DIR = path.dirname(path.realpath(__file__))
METADATA_DIR = path.join(path.dirname(SCRIPT_DIR), 'utils', 'metadata', 'tests')

CODEMETA_BASENAME = 'codemeta_test.json'
CODEMETA_LOCATION = path.join(METADATA_DIR, CODEMETA_BASENAME)
RADAR_URL = 'https://radar.kit.edu'
RADAR_USERNAME = 'testuser'
RADAR_PASSWORD = 'testpassword'
RADAR_CLIENT_ID = 'testclientid'
RADAR_CLIENT_SECRET = 'testclientsecret'
RADAR_WORKSPACE_ID = 'testworkspaceid'
RADAR_REDIRECT_URL = 'https://example.com'
RADAR_EMAIL = 'testuser@example.com'
RADAR_BACKLINK = 'https://example.com'
ASSETS = [CODEMETA_LOCATION, 'https://www.rfc-editor.org/rfc/rfc2606.txt']


def test_error_radar_asset_exists(monkeypatch, tmp_path, capsys):
    """
    Error is raised when a file with same name as the asset already exists in the radar path.
    """
    radar_path = tmp_path / 'radar_path'
    radar_path.mkdir()
    # Create a dummy file in the radar path to simulate an existing asset
    (radar_path / CODEMETA_BASENAME).touch()
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'radar',
                            'upload',
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--radar-path', str(radar_path),
                            '--radar-url', RADAR_URL,
                            '--radar-username', RADAR_USERNAME,
                            '--radar-password', RADAR_PASSWORD,
                            '--radar-client-id', RADAR_CLIENT_ID,
                            '--radar-client-secret', RADAR_CLIENT_SECRET,
                            '--radar-workspace-id', RADAR_WORKSPACE_ID,
                            '--radar-redirect-url', RADAR_REDIRECT_URL,
                            '--radar-email', RADAR_EMAIL,
                            '--radar-backlink', RADAR_BACKLINK,
                            '--dry',
                            *ASSETS
                        ])
    with pytest.raises(SystemExit, match='^2$'):
        main()
    captured = capsys.readouterr().err
    assert 'already exists' in captured


def test_dry_cli(monkeypatch, tmp_path, capsys):
    """
    Test that the function runs with CLI options, that CodeMeta metadata is retrieved and that the
    Radar metadata is printed to stdout in dry mode.
    """
    radar_path = tmp_path / 'radar_path'
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'radar',
                            'upload',
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--radar-path', str(radar_path),
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
    # Test if the title is correctly set to the name and version of the codemeta file
    with open(CODEMETA_LOCATION) as f:
        codemeta = json.load(f)
    codemeta_name = codemeta.get('name')
    codemeta_version = codemeta.get('version')
    assert captured['descriptiveMetadata'].get('title', '') == f'{codemeta_name} ({codemeta_version})'


def test_assets_env(monkeypatch, tmp_path, capsys):
    """
    Test the function runs with options set as environment variables and
    that assets are collected.
    """
    radar_path = tmp_path / 'radar_path'
    monkeypatch.setenv('RADAR_PATH', str(radar_path))
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
                            'upload',
                            '--dry',
                            *ASSETS
                        ])
    main()
    assert radar_path.is_dir()
    for asset in ASSETS:
        assert (radar_path / path.basename(asset)).is_file()
