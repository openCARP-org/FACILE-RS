from os import path

from facile_rs.utils.metadata import ZenodoMetadata

# Get current script location
SCRIPT_DIR = path.dirname(path.realpath(__file__))


def test_get_license_id_from_spdx():
    metadata = ZenodoMetadata()
    assert metadata.get_license_id_from_spdx("LGPL-3.0") == "lgpl-3.0-only"
    assert metadata.get_license_id_from_spdx("MIT") == "mit"
    assert metadata.get_license_id_from_spdx("Apache-2.0") == "apache-2.0"
    assert metadata.get_license_id_from_spdx("not-a-license") is None


def test_to_person_or_org():
    metadata = ZenodoMetadata()
    codemeta_person = {
        "@type": "Person",
        "@id": "https://orcid.org/0000-0000-0000-0000",
        "givenName": "John",
        "familyName": "Smith",
        "affiliation": [
            {
                "@type": "Organization",
                "@id": "https://ror.org/04t3en479",
                "name": "Karlsruhe Institute of Technology (KIT)"
            },
            {
                "@type": "Organization",
                "@id": "https://ror.org/0245cg223",
                "name": "University of Freiburg"
            }
        ]
    }
    zenodo_person = {
        "person_or_org": {
            "type": "personal",
            "given_name": "John",
            "family_name": "Smith",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0000-0000-0000"
                }
            ]
        },
        "affiliations": [
            {
                "name": "Karlsruhe Institute of Technology (KIT)",
                "id": "04t3en479"
            },
            {
                "name": "University of Freiburg",
                "id": "0245cg223"
            }
        ]
    }
    codemeta_organization = {
        "@type": "Organization",
        "@id": "https://ror.org/02n0bts35",
        "name": "Medical University of Graz"
        }
    zenodo_organization = {
        "person_or_org": {
            "type": "organizational",
            "name": "Medical University of Graz",
            "identifiers": [
                {
                    "scheme": "ror",
                    "identifier": "02n0bts35"
                }
        ]
        }
    }
    codemeta_person_single_affiliation = {
        "id": "https://orcid.org/0000-0002-6584-0233",
        "type": "Person",
        "affiliation": {
            "type": "Organization",
            "name": "Karlsruhe Institute of Technology"
        },
        "email": "marie.houillon@kit.edu",
        "familyName": "Houillon",
        "givenName": "Marie"
    }
    zenodo_person_single_affiliation = {
        "person_or_org": {
            "type": "personal",
            "given_name": "Marie",
            "family_name": "Houillon",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-6584-0233"
                }
            ]
        },
        "affiliations": [
            {
                "name": "Karlsruhe Institute of Technology"
            }
        ]
    }

    zenodo_contributor = zenodo_person.copy()
    zenodo_contributor["role"] = {"id": "datacurator"}
    zenodo_unknown_contributortype = zenodo_person.copy()
    zenodo_unknown_contributortype["role"] = {"id": "other"}

    assert metadata.to_person_or_org(codemeta_person) == zenodo_person
    assert metadata.to_person_or_org(codemeta_person_single_affiliation) == zenodo_person_single_affiliation
    assert metadata.to_person_or_org(codemeta_organization) == zenodo_organization
    assert metadata.to_person_or_org(codemeta_person, "datacurator") == zenodo_contributor
    assert metadata.to_person_or_org(codemeta_person, "InvalidType") == zenodo_unknown_contributortype


def test_to_funding():
    metadata = ZenodoMetadata()
    codemeta_invalid_funding = {
      "@type": "Grant",
      "name": "Rolling out the openCARP simulator as a sustainable e-research infrastructure: CARPe-diem",
      "identifier": 507828355,
      "url": "https://gepris.dfg.de/gepris/projekt/507828355?language=en",
      "funder": {
        "@type": "Organization",
        "@id": "https://ror.org/018mejw64",
        "name": "Deutsche Forschungsgemeinschaft"
      }
    }
    codemeta_valid_funding = {
      "@type": "Grant",
      "name": "Numerical modeling of cardiac electrophysiology at the cellular scale",
      "identifier": 955495,
      "url": "https://eurohpc-ju.europa.eu/actions#ecl-inpage-259",
      "funder": {
        "@type": "Organization",
        "@id": "https://ror.org/00k4n6c32",
        "name": "European High-Performance Computing Joint Undertaking EuroHPC (JU)"
      }
    }
    zenodo_invalid_grant = {
        "funder": {
          "id": "018mejw64"
        },
        "award": {
          "title": {
            "en": "Rolling out the openCARP simulator as a sustainable e-research infrastructure: CARPe-diem"
          },
          "number": 507828355,
          "identifiers": [
            {
              "scheme": "url",
              "identifier": "https://gepris.dfg.de/gepris/projekt/507828355?language=en"
            }
          ]
        }
      }
    zenodo_valid_grant = {
        "award": {
          "id": "00k4n6c32::955495"
        },
        "funder": {
          "id": "00k4n6c32"
        }
      }
    assert metadata.to_funding(codemeta_valid_funding) == zenodo_valid_grant
    assert metadata.to_funding(codemeta_invalid_funding) == zenodo_invalid_grant
    metadata.data = {"funder": "The grant funder", "funding": "The grant name"}
    zenodo_funding = {
        "award": {
            "title": {"en": "The grant name"}
        },
        "funder": {
            "name": "The grant funder"
        }
    }
    assert metadata.to_funding("The grant name") == zenodo_funding

def test_to_rights():
    metadata = ZenodoMetadata()
    codemeta_license = "https://spdx.org/licenses/MIT"
    zenodo_right = {"id": "mit"}
    assert metadata.to_rights(codemeta_license) == zenodo_right
    codemeta_license = "MIT"
    assert metadata.to_rights(codemeta_license) == zenodo_right
    codemeta_license = "not-a-license"
    assert metadata.to_rights(codemeta_license) == {}
    codemeta_license = {
        "@type": "CreativeWork",
        "name": "ACADEMIC PUBLIC LICENSE (openCARP, v1.1)",
        "url": "https://openCARP.org/download/license"
    }
    zenodo_right = {
        "title": {
            "en": "ACADEMIC PUBLIC LICENSE (openCARP, v1.1)"
        },
        "link": "https://openCARP.org/download/license"
    }
    assert metadata.to_rights(codemeta_license) == zenodo_right
    codemeta_license = {
        "@type": "CreativeWork",
        "name": "Apache License, Version 2.0",
        "url": "https://spdx.org/licenses/Apache-2.0"
    }
    zenodo_right = {
        "id": "apache-2.0"
    }
    assert metadata.to_rights(codemeta_license) == zenodo_right

def test_validate_funding_identifier():
    metadata = ZenodoMetadata()
    assert metadata.validate_funding_identifier("955495")['id'] == "00k4n6c32::955495"
    assert metadata.validate_funding_identifier(955495)['id'] == "00k4n6c32::955495"
    assert metadata.validate_funding_identifier("nonvalid1234") == {}

def test_validate_funder_identifier():
    metadata = ZenodoMetadata()
    assert metadata.validate_funder_identifier("https://ror.org/00k4n6c32") == "00k4n6c32"
    assert metadata.validate_funder_identifier("00k4n6c32") == "00k4n6c32"
    assert metadata.validate_funder_identifier("nonvalid1234") is None

def test_to_funder():
    metadata = ZenodoMetadata()
    codemeta_funder = {
        "@type": "Organization",
        "@id": "https://ror.org/00k4n6c32",
        "name": "European High-Performance Computing Joint Undertaking EuroHPC (JU)"
    }
    zenodo_funder = {
        "id": "00k4n6c32"
    }
    assert metadata.to_funder(codemeta_funder) == zenodo_funder
    codemeta_funder = {
        "type": "Organization",
        "name": "The funding organization",
        "url": "https://thefundingorganization.org"
    }
    zenodo_funder = {
        "name": "The funding organization"
    }
    assert metadata.to_funder(codemeta_funder) == zenodo_funder

def test_to_related_identifier():
    metadata = ZenodoMetadata()
    identifier = "https://git.opencarp.org/openCARP/openCARP"
    relation = "issupplementto"
    zenodo_related_identifier = {
        "relation_type": {"id": relation},
        "identifier": identifier
    }
    assert metadata.to_related_identifier(identifier, relation) == zenodo_related_identifier
    relation = "notincontrolledvocabulary"
    assert metadata.to_related_identifier(identifier, relation) is None

def test_to_subjects():
    metadata = ZenodoMetadata()
    codemeta_keywords = ["cardiac electrophysiology"]
    zenodo_subjects = [{"subject": "cardiac electrophysiology"}]
    assert metadata.to_subjects(codemeta_keywords) == zenodo_subjects
    codemeta_keywords = [{"@type": "DefinedTerm",
      "name": "Mathematical models",
      "url": "http://id.loc.gov/authorities/subjects/sh85082124",
      "inDefinedTermSet": "http://id.loc.gov/authorities/subjects"
    }]
    zenodo_subjects = [{"subject": "http://id.loc.gov/authorities/subjects/sh85082124"}]
    assert metadata.to_subjects(codemeta_keywords) == zenodo_subjects

def test_add_to_array_field():
    metadata = ZenodoMetadata()
    zenodo_dict = {'metadata': {}}
    field = 'contributors'
    value1 = {'name': 'John Smith'}
    metadata.add_to_array_field(zenodo_dict, field, value1)
    assert zenodo_dict['metadata'][field] == [value1]
    value2 = {'name': 'Jane Doe'}
    metadata.add_to_array_field(zenodo_dict, field, value2)
    assert isinstance(zenodo_dict['metadata'][field], list)
    assert len(zenodo_dict['metadata'][field]) == 2
    assert value1 in zenodo_dict['metadata'][field]
    assert value2 in zenodo_dict['metadata'][field]
