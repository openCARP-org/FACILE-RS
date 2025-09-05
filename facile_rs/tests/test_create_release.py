import ast
import sys

from facile_rs.utils.cli import main

RELEASE_TAG = 'v0.1.0'
RELEASE_DESCRIPTION = 'Release for version 0.1.0'
RELEASE_API_URL = 'https://gitlab.example.com/api/v4/projects/123/releases'
PRIVATE_TOKEN = '1234567890'
ASSETS = ['https://example.com/assets/asset1', 'https://example.com/assets/asset2']


def test_create_release_dry_cli(monkeypatch, capsys):
    """"
    Check release request content in dry mode using CLI options.
    """
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'gitlab',
                            'publish',
                            '--release-tag', RELEASE_TAG,
                            '--release-description', RELEASE_DESCRIPTION,
                            '--release-api-url', RELEASE_API_URL,
                            '--private-token', PRIVATE_TOKEN,
                            '--dry',
                            *ASSETS
                        ])
    main()
    captured = ast.literal_eval(capsys.readouterr().out)
    assert captured['name'] == RELEASE_TAG
    assert captured['tag_name'] == RELEASE_TAG
    assert captured['description'] == RELEASE_DESCRIPTION.strip()
    assert len(captured['assets']['links']) == 2
    assert captured['assets']['links'][0]['url'] == 'https://example.com/assets/asset1'
    assert captured['assets']['links'][1]['name'] == 'asset2'


def test_create_release_dry_env(monkeypatch, capsys):
    """
    Check release request content in dry mode using environment variables.
    """
    monkeypatch.setenv('RELEASE_TAG', RELEASE_TAG)
    monkeypatch.setenv('RELEASE_DESCRIPTION', RELEASE_DESCRIPTION)
    monkeypatch.setenv('RELEASE_API_URL', RELEASE_API_URL)
    monkeypatch.setenv('PRIVATE_TOKEN', PRIVATE_TOKEN)
    monkeypatch.setenv('ASSETS', ' '.join(ASSETS))
    monkeypatch.setattr('sys.argv',
                       [
                           sys.argv[0],
                           'gitlab',
                           'publish',
                           '--dry'
                       ])
    main()
    captured = ast.literal_eval(capsys.readouterr().out)
    assert captured['name'] == RELEASE_TAG
    assert captured['tag_name'] == RELEASE_TAG
    assert captured['description'] == RELEASE_DESCRIPTION.strip()
    assert len(captured['assets']['links']) == 2
    assert captured['assets']['links'][1]['url'] == 'https://example.com/assets/asset2'
    assert captured['assets']['links'][0]['name'] == 'asset1'
