from os import path

import pytest
import yaml

from facile_rs.utils.metadata import CffMetadata, CodemetaMetadata
from facile_rs.utils.metadata.cff import schema_org_identifier_to_cff

# Get current script location
SCRIPT_DIR = path.dirname(path.realpath(__file__))


def create_metadata(codemeta_filename):
    codemeta = CodemetaMetadata()
    codemeta.fetch(path.join(SCRIPT_DIR, codemeta_filename))
    codemeta.compute_names()
    metadata = CffMetadata(codemeta.data)
    return codemeta, metadata


def test_schemaorg_identifier_to_cff():
    schemaorg_id = [{
        "@type": "PropertyValue",
        "propertyID": "DOI",
        "value": "10.35097/1952"
    },
    {
        "@type": "PropertyValue",
        "propertyID": "RADAR",
        "value": "gNzfgsCdFVucufDC"
    }]
    expected_result_0 = {
        "type": "doi",
        "value": "10.35097/1952"
    }
    assert schema_org_identifier_to_cff(schemaorg_id[0]) == expected_result_0
    assert schema_org_identifier_to_cff(schemaorg_id[1]) == {}


@pytest.mark.parametrize("codemeta_filename", [
    'codemeta_test.json',
    'codemeta_isbasedon.json'
])
def test_init(codemeta_filename):
    codemeta, metadata = create_metadata(codemeta_filename)
    assert metadata.data == codemeta.data

@pytest.mark.parametrize(("codemeta_filename", "cff_ref_filename"), [
    ('codemeta_test.json', 'cff_ref.yml'),
    ('codemeta_isbasedon.json', 'cff_isbasedon_ref.yml')
])
def test_conversion(codemeta_filename, cff_ref_filename):
    _, metadata = create_metadata(codemeta_filename)
    print(metadata.to_yaml())
    with open(path.join(SCRIPT_DIR, cff_ref_filename)) as f:
        assert yaml.safe_load(metadata.to_yaml()) == yaml.safe_load(f)
