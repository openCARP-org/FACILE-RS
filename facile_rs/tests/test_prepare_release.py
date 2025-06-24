import json
import sys
from datetime import date

from facile_rs.utils.cli import main

RELEASE_TAG = 'v0.1.0'
RELEASE_DATE = '2024-12-16'
MINIMAL_CODEMETA = """{
    "@context": "https://doi.org/10.5063/schema/codemeta-2.0",
    "@type": "SoftwareSourceCode",
    "name": "CodemetaR",
    "version": "0.0.1",
    "description": "Codemeta defines a 'JSON-LD' format for describing software metadata. This package provides utilities to generate, parse, and modify codemeta.jsonld files automatically for R packages.",
    "license": "https://spdx.org/licenses/GPL-3.0",
    "identifier": "http://dx.doi.org/10.5281/zenodo.XXXX"
}
"""  # noqa: E501


def assertions(initial_codemeta, modified_codemeta, release_tag, release_date):
    """
    Assert that the modified codemeta file has same content as the initial one,
    except for the version and dateModified fields.
    """
    assert modified_codemeta['version'] == release_tag
    assert modified_codemeta['dateModified'] == release_date
    for key in initial_codemeta:
        if key not in ['version', 'dateModified']:
            assert key in modified_codemeta
            assert initial_codemeta[key] == modified_codemeta[key]


def test_cli(monkeypatch, tmp_path):
    """
    Test the prepare_release script using command-line arguments and providing a date.
    """
    codemeta_location = tmp_path / 'codemeta.json'
    codemeta_location.write_text(MINIMAL_CODEMETA)
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'release',
                            'prepare',
                            '--codemeta-location', str(codemeta_location),
                            '--version', RELEASE_TAG,
                            '--date', RELEASE_DATE
                        ])
    main()
    modified_codemeta = json.loads(codemeta_location.read_text())
    initial_codemeta = json.loads(MINIMAL_CODEMETA)
    assertions(initial_codemeta, modified_codemeta, RELEASE_TAG, RELEASE_DATE)


def test_env_nodate(monkeypatch, tmp_path):
    """
    Test the prepare_release script using environment variables and not providing a date.
    """
    codemeta_location = tmp_path / 'codemeta.json'
    codemeta_location.write_text(MINIMAL_CODEMETA)
    monkeypatch.setenv('CODEMETA_LOCATION', str(codemeta_location))
    monkeypatch.setenv('VERSION', RELEASE_TAG)
    monkeypatch.delenv('DATE', raising=False)
    monkeypatch.setattr('sys.argv',
                        [
                            sys.argv[0],
                            'release',
                            'prepare'
                        ])
    main()
    modified_codemeta = json.loads(codemeta_location.read_text())
    initial_codemeta = json.loads(MINIMAL_CODEMETA)
    assertions(initial_codemeta, modified_codemeta, RELEASE_TAG, date.today().strftime('%Y-%m-%d'))
