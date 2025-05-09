import filecmp
import sys
from os import path

import pytest

from facile_rs.utils.cli import main
from facile_rs.utils.http import fetch_dict

SCRIPT_DIR = path.dirname(path.realpath(__file__))
METADATA_DIR = path.join(path.dirname(SCRIPT_DIR), 'utils', 'metadata', 'tests')

BAG_INFO = path.join(SCRIPT_DIR, 'bag-info.yml')
DATACITE_LOCATION = path.join(METADATA_DIR, 'datacite_ref.xml')
CODEMETA_LOCATION = path.join(METADATA_DIR, 'codemeta_test.json')
CREATORS_LOCATIONS = path.join(METADATA_DIR, 'codemeta_authors_test.json')


def test_bag_path_exists(monkeypatch, tmp_path, capsys):
    """
    Error is raised when the bag path already exists
    """
    output_bag = tmp_path / 'bag'
    output_bag.mkdir()

    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'bagpack',
                            'create',
                            '--bag-path', str(output_bag),
                            '--datacite-location', str(DATACITE_LOCATION),
                        ])
    # Check that SystemExit is raised with error code 2
    with pytest.raises(SystemExit, match='^2$'):
        main()
    # Check that the expected error is raised
    captured = capsys.readouterr().err
    assert 'already exists' in captured


def test_bag_cli(monkeypatch, tmp_path):
    """
    Test the bag creation using command line arguments:
        - bag-info.txt is created
        - The assets are copied to the bag/data directory
        - Datacite XML is added to the bag
    """
    output_bag = tmp_path / 'bag'
    assets = [CODEMETA_LOCATION, CREATORS_LOCATIONS]
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'bagpack',
                            'create',
                            '--bag-path', str(output_bag),
                            '--datacite-location', str(DATACITE_LOCATION),
                            *assets
                        ])
    main()
    assert output_bag.exists()
    assert (output_bag / 'bag-info.txt').exists()
    assert (output_bag / 'data' / 'codemeta_test.json').exists()
    assert (output_bag / 'data' / 'codemeta_authors_test.json').exists()
    # Check that the DataCite XML file is added to the bag
    assert (output_bag / 'metadata' / 'datacite.xml').exists()
    assert filecmp.cmp(DATACITE_LOCATION, output_bag / 'metadata' / 'datacite.xml', shallow=False)


def test_bag_env(monkeypatch, tmp_path):
    """
    Test the bag creation using environment variables
        - bag-info.txt is created and populated with the expected elements
        - The assets are copied to the bag/data directory
    """
    output_bag = tmp_path / 'bag'
    assets = [CODEMETA_LOCATION, CREATORS_LOCATIONS]
    monkeypatch.setenv('BAG_PATH', str(output_bag))
    monkeypatch.setenv('BAG_INFO_LOCATIONS', str(BAG_INFO))
    monkeypatch.setenv('DATACITE_LOCATION', str(DATACITE_LOCATION))
    monkeypatch.setenv('ASSETS', ' '.join(assets))
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'bagpack',
                            'create',
                        ])
    main()
    assert output_bag.exists()
    assert (output_bag / 'bag-info.txt').exists()
    assert (output_bag / 'data' / 'codemeta_test.json').exists()
    assert (output_bag / 'data' / 'codemeta_authors_test.json').exists()
    # Check that the DataCite XML file is added to the bag
    assert (output_bag / 'metadata' / 'datacite.xml').exists()
    assert filecmp.cmp(DATACITE_LOCATION, output_bag / 'metadata' / 'datacite.xml', shallow=False)
    # Check that the bag-info file contains the expected elements
    out_bag_info = open(output_bag / 'bag-info.txt').read()
    bag_info = fetch_dict(BAG_INFO)
    for elem in bag_info.keys():
        assert elem in out_bag_info
