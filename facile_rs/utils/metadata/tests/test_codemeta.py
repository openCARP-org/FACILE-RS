import json
from os import path

from facile_rs.utils.metadata import CodemetaMetadata

# Get current script location
SCRIPT_DIR = path.dirname(path.realpath(__file__))


def test_fetch():
    """Test fetching a JSON CodeMeta file
    """
    metadata = CodemetaMetadata()
    metadata.fetch(path.join(SCRIPT_DIR, 'codemeta_test.json'))
    with open(path.join(SCRIPT_DIR, 'codemeta_test.json')) as f:
        assert json.load(f) == metadata.data


def test_fetch_authors():
    """Test fetching authors from multiple files containing duplicates.
    """
    metadata = CodemetaMetadata()
    metadata.fetch(path.join(SCRIPT_DIR, 'codemeta_test.json'))
    metadata.fetch_authors([
        path.join(SCRIPT_DIR, 'codemeta_test.json'),
        path.join(SCRIPT_DIR, 'codemeta_authors_test.json')
        ])
    with open(path.join(SCRIPT_DIR, 'codemeta_authors_test.json')) as f:
        for author in json.load(f)['author']:
            assert author in metadata.data['author']


def test_fetch_contributors():
    """Test fetching contributors when initial dataset contains a unique contributor
    """
    metadata = CodemetaMetadata()
    metadata.fetch(path.join(SCRIPT_DIR, 'codemeta_test.json'))
    metadata.fetch_contributors([path.join(SCRIPT_DIR, 'codemeta_contributors_test.json')])
    with open(path.join(SCRIPT_DIR, 'codemeta_contributors_test.json')) as f:
        for contributor in json.load(f)['contributor']:
            print(contributor)
            print(metadata.data['contributor'])
            assert contributor in metadata.data['contributor']


def test_compute_names():
    metadata = CodemetaMetadata()
    metadata.data = {
        'author': [
            {'@type': 'Person', 'familyName': 'Author', 'givenName': 'One'}
        ],
        'contributor': [
            {'@type': 'Person', 'name': 'O Contributor', 'familyName': 'Contributor', 'givenName': 'One'},
            {'@id': 'http://orcid.org/9999-9999-9999-9999', '@type': 'Person',
             'email': 'another.contributor@example.com',
             'familyName': 'Contributor', 'givenName': 'Another'}
        ]
    }
    metadata.compute_names()
    # 'name' field doesn't exist
    assert metadata.data['author'][0]['name'] == 'One Author'
    assert metadata.data['contributor'][1]['name'] == 'Another Contributor'
    # 'name' field already exists and shouldn't be overwritten
    assert metadata.data['contributor'][0]['name'] == 'O Contributor'


def test_remove_doubles():
    metadata = CodemetaMetadata()
    metadata.data = {
        'author': [
            # Entries with same 'name' are considered duplicates
            {'@type': 'Person', 'name': 'One Author', 'email': 'oa@kit.edu'},
            {'@type': 'Person', 'name': 'One Author', 'email': 'oauthor@kit.edu'},
            {'@type': 'Person', 'familyName': 'Author', 'givenName': 'One', 'email': 'oa@kit.edu'}
        ],
        'contributor': [
            # Entries with same '@id' are considered duplicates
            {'@type': 'Person', 'familyName': 'Author', 'givenName': 'One', '@id': 'http://orcid.org/9999-9999-9999-9999'},
            {'@type': 'Person', 'familyName': 'Author', 'givenName': 'O', '@id': 'http://orcid.org/9999-9999-9999-9999'},
        ]
    }
    metadata.remove_doubles()
    expected_result = {
        'author': [
            {'@type': 'Person', 'name': 'One Author', 'email': 'oa@kit.edu'},
            {'@type': 'Person', 'familyName': 'Author', 'givenName': 'One', 'email': 'oa@kit.edu'}
        ],
        'contributor': [
            {'@type': 'Person', 'familyName': 'Author', 'givenName': 'One', '@id': 'http://orcid.org/9999-9999-9999-9999'}
        ]
    }
    assert metadata.data == expected_result


def test_sort_persons():
    metadata = CodemetaMetadata()
    for key in ['author', 'contributor']:
        metadata.data[key] = [
                {'@type': 'Person', 'name': 'Firstname Lastname'},
                {'@type': 'Person', 'familyName': 'Author', 'givenName': 'One', 'email': 'oa@kit.edu'},
                {'@type': 'Organization', 'name': 'First organization', 'additionalType': 'anotherType'},
                {'@type': 'Organization', 'name': 'Zyx organization'},
                {'@type': 'Organization', 'name': 'Another organization'}
            ]
    metadata.sort_persons()
    expected_result = {}
    for key in ['author', 'contributor']:
        expected_result[key] = [
                # Organizations first...
                {'@type': 'Organization', 'name': 'Another organization'},
                {'@type': 'Organization', 'name': 'Zyx organization'},
                {'@type': 'Person', 'familyName': 'Author', 'givenName': 'One', 'email': 'oa@kit.edu'},
                {'@type': 'Person', 'name': 'Firstname Lastname'},
                # ... Unless they have an additionalType
                {'@type': 'Organization', 'name': 'First organization', 'additionalType': 'anotherType'},
            ]
    assert expected_result == metadata.data


def test_update_identifier_new():
    # Test adding a new DOI and archive ID when no previous identifiers exist
    metadata = CodemetaMetadata()
    metadata.data = {
        'name': 'openCARP',
        'version': '0.0.1'
    }
    metadata.update_identifier(new_doi='10.1234/new.doi', new_archive_id='zenodo123', archive_type='Zenodo',
                               keep_previous_doi=False)
    expected_result = {
        'name': 'openCARP',
        'version': '0.0.1',
        '@id': 'https://doi.org/10.1234/new.doi',
        'identifier': [
            {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': '10.1234/new.doi',
                'description': 'The DOI for version 0.0.1 of this work'
            },
            {'@type': 'PropertyValue', 'propertyID': 'Zenodo', 'value': 'zenodo123'}
        ]
    }
    assert metadata.data == expected_result

def test_update_identifier_existing_overwrite():
    # Test adding a new DOI and archive ID when previous identifiers exist, without keeping the previous DOI
    metadata = CodemetaMetadata()
    metadata.data = {
        'name': 'openCARP',
        'version': '0.0.2',
        '@id': 'https://doi.org/10.1234/old.doi',
        'identifier': [
            {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': '10.1234/additional.doi',
                'description': 'The concept DOI of this work'
            },
            {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': '10.1234/old.doi',
                'description': 'The DOI for version 0.0.1 of this work'
            },
            {'@type': 'PropertyValue', 'propertyID': 'RADAR', 'value': 'radarold'}
        ]
    }
    metadata.update_identifier(new_doi='10.5678/new.doi', new_archive_id='radarnew', archive_type='RADAR',
                               keep_previous_doi=False)
    expected_result = {
        'name': 'openCARP',
        'version': '0.0.2',
        '@id': 'https://doi.org/10.5678/new.doi',
        'identifier': [
            {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': '10.1234/additional.doi',
                'description': 'The concept DOI of this work'
            },
            {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': '10.5678/new.doi',
                'description': 'The DOI for version 0.0.2 of this work'
            },
            {'@type': 'PropertyValue', 'propertyID': 'RADAR', 'value': 'radarnew'}
        ]
    }
    assert metadata.data == expected_result

def test_update_identifier_existing_keepdois():
    # Test adding a new DOI, keeping previous DOIs
    metadata = CodemetaMetadata()
    metadata.data = {
        'name': 'openCARP',
        'version': '1.0.0',
        '@id': 'https://doi.org/10.1234/old.doi',
        'identifier': [
            {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': '10.1234/additional.doi',
                'description': 'The concept DOI of this work'
            },
            {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': '10.1234/old.doi',
                'description': 'The DOI for version 0.0.1 of this work'
            },
            {'@type': 'PropertyValue', 'propertyID': 'RADAR', 'value': 'radarold'}
        ]
    }
    metadata.update_identifier(new_doi='10.5678/new.doi', keep_previous_doi=True)
    expected_result = {
        'name': 'openCARP',
        'version': '1.0.0',
        '@id': 'https://doi.org/10.5678/new.doi',
        'identifier': [
            {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': '10.1234/additional.doi',
                'description': 'The concept DOI of this work'
            },
            {
                '@type': 'PropertyValue',
                'propertyID': 'DOI',
                'value': '10.5678/new.doi',
                'description': 'The DOI for version 1.0.0 of this work'
            },
            {'@type': 'PropertyValue', 'propertyID': 'RADAR', 'value': 'radarold'}
        ],
        'isBasedOn': [
            {
                '@type': 'CreativeWork',
                'identifier': {
                    '@type': 'PropertyValue',
                    'propertyID': 'DOI',
                    'value': '10.1234/old.doi',
                    'description': 'The DOI for version 0.0.1 of this work'
                }
            }
        ]
    }
    assert metadata.data == expected_result
