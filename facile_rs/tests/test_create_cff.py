import sys
from os import path

from facile_rs.utils.cli import main

SCRIPT_DIR = path.dirname(path.realpath(__file__))
METADATA_DIR = path.join(path.dirname(SCRIPT_DIR), 'utils', 'metadata', 'tests')

CODEMETA_LOCATION = path.join(METADATA_DIR, 'codemeta_test.json')
CREATORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_authors_test.json')
CONTRIBUTORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_contributors_test.json')


def test_cli(monkeypatch, tmpdir):
    """
    Test the CFF file creation using command line arguments
    """
    output_cff = tmpdir.join('output.cff')
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'cff',
                            'create',
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--creators-location', CREATORS_LOCATIONS,
                            '--contributors-location', CONTRIBUTORS_LOCATIONS,
                            '--cff-path', str(output_cff)
                        ])
    main()
    with open(path.join(SCRIPT_DIR, 'cff_ref.cff')) as cff_ref:
        assert output_cff.read() == cff_ref.read()


def test_env(monkeypatch, tmpdir):
    """
    Test the CFF file creation using environment variables
    """
    output_cff = tmpdir.join('output.cff')
    monkeypatch.setenv('CODEMETA_LOCATION', CODEMETA_LOCATION)
    monkeypatch.setenv('CREATORS_LOCATIONS', CREATORS_LOCATIONS)
    monkeypatch.setenv('CONTRIBUTORS_LOCATIONS', CONTRIBUTORS_LOCATIONS)
    monkeypatch.setenv('CFF_PATH', str(output_cff))
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'cff',
                            'create'
                        ])
    main()
    with open(path.join(SCRIPT_DIR, 'cff_ref.cff')) as cff_ref:
        assert output_cff.read() == cff_ref.read()

def test_stdout(monkeypatch, capsys):
    """
    Test the CFF output to stdout
    """
    # Ensure no CFF_PATH environment variable is set
    monkeypatch.delenv('CFF_PATH', raising=False)
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'cff',
                            'create',
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--creators-location', CREATORS_LOCATIONS,
                            '--contributors-location', CONTRIBUTORS_LOCATIONS,
                        ])
    main()
    captured = capsys.readouterr().out
    with open(path.join(SCRIPT_DIR, 'cff_ref.cff')) as cff_ref:
        # remove the last newline character added by the print function
        assert captured[:-1] == cff_ref.read()
