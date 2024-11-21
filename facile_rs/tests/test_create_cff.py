import sys
from os import path

from facile_rs.create_cff import main

SCRIPT_DIR = path.dirname(path.realpath(__file__))
METADATA_DIR = path.join(path.dirname(SCRIPT_DIR), 'utils', 'metadata', 'tests')

CODEMETA_LOCATION = path.join(METADATA_DIR, 'codemeta_test.json')
CREATORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_authors_test.json')
CONTRIBUTORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_contributors_test.json')


def test_cli(monkeypatch, tmpdir):
    output_cff = tmpdir.join('output.cff')
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--creators-location', CREATORS_LOCATIONS,
                            '--contributors-location', CONTRIBUTORS_LOCATIONS,
                            '--cff-path', str(output_cff)
                        ])
    main()
    with open(path.join(SCRIPT_DIR, 'cff_ref.cff')) as cff_ref:
        assert output_cff.read() == cff_ref.read()


def test_env(monkeypatch, tmpdir):
    output_cff = tmpdir.join('output.cff')
    monkeypatch.setenv('CODEMETA_LOCATION', CODEMETA_LOCATION)
    monkeypatch.setenv('CREATORS_LOCATIONS', CREATORS_LOCATIONS)
    monkeypatch.setenv('CONTRIBUTORS_LOCATIONS', CONTRIBUTORS_LOCATIONS)
    monkeypatch.setenv('CFF_PATH', str(output_cff))
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                        ])
    main()
    with open(path.join(SCRIPT_DIR, 'cff_ref.cff')) as cff_ref:
        assert output_cff.read() == cff_ref.read()
