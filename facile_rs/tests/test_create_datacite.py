import sys
from os import path

from facile_rs.utils.cli import main

SCRIPT_DIR = path.dirname(path.realpath(__file__))
METADATA_DIR = path.join(path.dirname(SCRIPT_DIR), 'utils', 'metadata', 'tests')

CODEMETA_LOCATION = path.join(METADATA_DIR, 'codemeta_test.json')
CREATORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_authors_test.json')
CONTRIBUTORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_contributors_test.json')


def test_cli(monkeypatch, tmpdir):
    """"
    Test the Datacite XML file creation using command line arguments
    """
    output_datacite = tmpdir.join('datacite.xml')
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'datacite',
                            'create',
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--creators-location', CREATORS_LOCATIONS,
                            '--contributors-location', CONTRIBUTORS_LOCATIONS,
                            '--datacite-path', str(output_datacite)
                        ])
    main()
    with open(path.join(SCRIPT_DIR, 'datacite_ref.xml')) as datacite_ref:
        assert output_datacite.read() == datacite_ref.read()


def test_env(monkeypatch, tmpdir):
    """
    Test the Datacite XML file creation using environment variables
    """
    output_datacite = tmpdir.join('datacite.xml')
    monkeypatch.setenv('CODEMETA_LOCATION', CODEMETA_LOCATION)
    monkeypatch.setenv('CREATORS_LOCATIONS', CREATORS_LOCATIONS)
    monkeypatch.setenv('CONTRIBUTORS_LOCATIONS', CONTRIBUTORS_LOCATIONS)
    monkeypatch.setenv('DATACITE_PATH', str(output_datacite))
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'datacite',
                            'create',
                        ])
    main()
    with open(path.join(SCRIPT_DIR, 'datacite_ref.xml')) as datacite_ref:
        assert output_datacite.read() == datacite_ref.read()


def test_stdout(monkeypatch, capsys):
    """
    Test the Datacite XML output to stdout
    """
    # Ensure no DATACITE_PATH environment variable is set
    monkeypatch.delenv('DATACITE_PATH', raising=False)
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'datacite',
                            'create',
                            '--codemeta-location', CODEMETA_LOCATION,
                            '--creators-location', CREATORS_LOCATIONS,
                            '--contributors-location', CONTRIBUTORS_LOCATIONS,
                        ])
    main()
    captured = capsys.readouterr().out
    with open(path.join(SCRIPT_DIR, 'datacite_ref.xml')) as datacite_ref:
        # remove the last newline character added by the print function
        assert captured[:-1] == datacite_ref.read()
