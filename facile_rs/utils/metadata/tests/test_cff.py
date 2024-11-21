from os import path

import pytest
import yaml

from facile_rs.utils.metadata import CffMetadata, CodemetaMetadata
from facile_rs.utils.metadata.cff import schema_org_identifier_to_cff

# Get current script location
SCRIPT_DIR = path.dirname(path.realpath(__file__))


@pytest.fixture
def create_metadata():
    codemeta = CodemetaMetadata()
    codemeta.fetch(path.join(SCRIPT_DIR, 'codemeta_test.json'))
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


def test_init(create_metadata):
    codemeta, metadata = create_metadata
    assert metadata.data == codemeta.data


def test_conversion(create_metadata):
    _, metadata = create_metadata
    print(metadata.to_yaml())
    with open(path.join(SCRIPT_DIR, 'cff_ref.yml')) as f:
        assert yaml.safe_load(metadata.to_yaml()) == yaml.safe_load(f)
