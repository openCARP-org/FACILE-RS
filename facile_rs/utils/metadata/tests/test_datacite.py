import io
from os import path
from xml.dom.minidom import parseString
from xml.sax.saxutils import XMLGenerator

import pytest

from facile_rs.utils.metadata import CodemetaMetadata, DataciteMetadata

# Get current script location
SCRIPT_DIR = path.dirname(path.realpath(__file__))


@pytest.fixture
def create_metadata():
    codemeta = CodemetaMetadata()
    codemeta.fetch(path.join(SCRIPT_DIR, 'codemeta_test.json'))
    codemeta.compute_names()
    metadata = DataciteMetadata(codemeta.data)
    return codemeta, metadata


@pytest.fixture
def create_metadata_schemaorg():
    codemeta = CodemetaMetadata()
    codemeta.fetch(path.join(SCRIPT_DIR, 'codemeta_schemaorg_test.json'))
    codemeta.compute_names()
    metadata = DataciteMetadata(codemeta.data)
    return codemeta, metadata


def test_render_node(create_metadata):
    metadata = DataciteMetadata({})
    metadata.render_node('name', {'key': 'value', 'other': 'val'}, 'Test text')
    dom = parseString(metadata.stream.getvalue())
    assert dom.toxml() == '<?xml version="1.0" ?><name key="value" other="val">Test text</name>'


def test_render_funding_references_codemeta(create_metadata):
    """Test for CodeMeta formatted funding metadata
    """
    _, metadata = create_metadata
    expected_result = """<?xml version="1.0" ?><fundingReferences><fundingReference><funderName>Karlsruhe Institute"""\
        """ of Technology</funderName></fundingReference><fundingReference><funderName>TES_2024_TEST</funderName>"""\
        """</fundingReference></fundingReferences>"""
    metadata.render_funding_references()
    dom = parseString(metadata.stream.getvalue())
    assert dom.toxml() == expected_result


def test_render_funding_references_schemaorg(create_metadata_schemaorg):
    """Test for schema.org formatted funding metadata
    """
    _, metadata = create_metadata_schemaorg
    with open(path.join(SCRIPT_DIR,'datacite_schemaorg_funding_ref.xml')) as f:
        expected_result = f.read()
    metadata.render_funding_references()
    dom = parseString(metadata.stream.getvalue())
    print(dom.toprettyxml())
    assert dom.toprettyxml() == expected_result


def test_init(create_metadata):
    codemeta, metadata = create_metadata
    assert metadata.data == codemeta.data
    assert isinstance(metadata.stream, io.StringIO)
    assert isinstance(metadata.xml, XMLGenerator)


def test_conversion(create_metadata):
    _, metadata = create_metadata
    with open(path.join(SCRIPT_DIR, 'datacite_ref.xml')) as f:
        assert metadata.to_xml() == f.read()
