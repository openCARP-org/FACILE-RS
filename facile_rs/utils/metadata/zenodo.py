import json
import logging

import requests

logger = logging.getLogger(__file__)


class ZenodoMetadata:

    prefixes = {
        'doi': 'https://doi.org/',
        'orcid': 'https://orcid.org/',
        'ror': 'https://ror.org/'
    }

    ZENODO_CONTRIBUTORTYPES = [
        "contactperson",
        "datacollector",
        "datacurator",
        "datamanager",
        "distributor",
        "editor",
        "hostinginstitution",
        "other",
        "producer",
        "projectleader",
        "projectmanager",
        "projectmember",
        "registrationagency",
        "registrationauthority",
        "relatedperson",
        "researcher",
        "researchgroup",
        "rightsholder",
        "sponsor",
        "supervisor",
        "workpackageleader"
    ]

    ZENODO_RELATIONSHIPS = [
        "iscitedby",
        "cites",
        "issupplementto",
        "issupplementedby",
        "iscontinuedby",
        "continues",
        "isdescribedby",
        "describes",
        "hasmetadata",
        "ismetadatafor",
        "isnewversionof",
        "ispreviousversionof",
        "ispartof",
        "haspart",
        "isreferencedby",
        "references",
        "isdocumentedby",
        "documents",
        "iscompiledby",
        "compiles",
        "isvariantformof",
        "isoriginalformof",
        "isidenticalto",
        "isalternateidentifier",
        "isreviewedby",
        "reviews",
        "isderivedfrom",
        "issourceof",
        "requires",
        "isrequiredby",
        "isobsoletedby",
        "obsoletes"
    ]

    def __init__(self, data={}):
        """
        Initialize the ZenodoMetadata object from CodeMeta metadata.

        :param data: CodeMeta metadata, typically the data attribute of a CodemetaMetadata instance.
        :type data: dict
        """
        self.data = data
        logger.debug('data = %s', self.data)

    def get_license_id_from_spdx(self, spdx_id):
        """
        Get Zenodo license ID from SPDX identifier. Return None if the id could not be validated.

        :param spdx_id: SPDX license identifier
        :return: Zenodo identifier for the license or None if not found
        """
        # Default mapping
        zenodo_id = spdx_id.lower()

        # Handle exceptions
        if zenodo_id == "lgpl-3.0":
            return "lgpl-3.0-only"

        # Validate license id, use 'notspecified' if license cannot be validated
        r = requests.get(f"https://zenodo.org/api/vocabularies/licenses/{zenodo_id}")
        if r.status_code != 200:
            logger.info(f'Zenodo license ID {zenodo_id} could not be validated...')
            zenodo_id = None

        return zenodo_id

    def to_rights(self, license):
        """
        Convert a CodeMeta license to a Zenodo rights object.

        :param license: CodeMeta license, URL or Schema.org CreativeWork object
        :type license: str or dict
        :return: Zenodo rights object
        :rtype: dict
        """
        zenodo_right = {}
        # Attempt to find license SPDX identifier
        licenseName = "unknown"
        if isinstance(license, str):
            licenseName = license
        elif isinstance(license, dict):
            if 'url' in license:
                licenseName = license['url']
            elif 'name' in license:
                licenseName = license['name']
        if licenseName.startswith("https://spdx.org/licenses/"):
            licenseName = licenseName.replace("https://spdx.org/licenses/", "")
        zenodo_id = self.get_license_id_from_spdx(licenseName)

        if zenodo_id:
            zenodo_right['id'] = zenodo_id
        else:
            if 'name' in license:
                zenodo_right['title'] = {'en': license['name']}
            if 'url' in license:
                zenodo_right['link'] = license['url']
            if 'description' in license:
                zenodo_right['description'] = {'en': license['description']}
        return zenodo_right

    def to_person_or_org(self, value, contributorType=None):
        """
        Converts a Person or Organization object to a Zenodo "person_or_org".
        If contributorType is not None, it will be converted to a Zenodo "contributor_person_or_org".

        :param value: CodeMeta Person or Organization object
        :type value: dict
        :param contributorType: None or type of contributor, taken from the Zenodo controlled vocabulary
            defined in self.ZENODO_CONTRIBUTORTYPES
        :type contributorType: None or str
        :return: Zenodo person_or_org or contributor_person_or_org object
        :rtype: dict
        """
        # Provide default value
        out_entry = {}

        if contributorType:
            if contributorType in self.ZENODO_CONTRIBUTORTYPES:
                out_entry['role'] = {
                    'id': contributorType
                }
            else:
                logger.info(f'Contributor type {contributorType} is not in the Zenodo controlled vocabulary,'\
                    'replacing with \'other\'...')
                out_entry['role'] = {
                    'id': 'other'
                }

        # Define is entry is a person or an organization
        person_or_org = {}
        if 'type' in value and value['type'] == 'Organization':
            person_or_org['type'] = 'organizational'
            person_or_org['name'] = value.get('name', '')
        elif ('type' in value and value['type'] == 'Person') or 'familyName' in value:
            person_or_org['type'] = 'personal'
            person_or_org['family_name'] = value.get('familyName', '')
            person_or_org['given_name'] = value.get('givenName', '')
        else:
            person_or_org['type'] = 'organizational'
            person_or_org['name'] = value.get('name', '')

        for id in ['id', '@id']:
            if id in value:
                person_or_org['identifiers'] = []
                for scheme, prefix in self.prefixes.items():
                    if value[id].startswith(prefix):
                        person_or_org['identifiers'].append(
                            {
                                'scheme': scheme,
                                'identifier': value[id].replace(prefix, '')
                            }
                        )
        out_entry['person_or_org'] = person_or_org

        # Add affiliations if type is person
        if person_or_org['type'] == 'personal':
            if isinstance(value.get('affiliation', {}), dict):
                value['affiliation'] = [value.get('affiliation', {})]
            for affiliation in value.get('affiliation', []):
                if 'affiliations' not in out_entry:
                    out_entry['affiliations'] = []
                id_found = False
                for id in ['id', '@id']:
                    if id in affiliation:
                        if affiliation[id].startswith(self.prefixes['ror']):
                            out_entry['affiliations'].append({
                                                            'id': affiliation[id].replace(self.prefixes['ror'], ''),
                                                            'name': affiliation.get('name', '')})
                            id_found = True
                # If ROR not found, add affiliation name only
                if not id_found:
                    out_entry['affiliations'].append({'name': affiliation.get('name', '')})
        return out_entry

    def validate_funding_identifier(self, funding_identifier):
        """
        Validate a funding identifier against the Zenodo API. If funding could be validated,
        return the funding object, otherwise return an empty dictionary.

        :param funding_identifier: funding identifier to validate
        :type funding_identifier: str
        :return: Zenodo funding object or empty dictionary
        :rtype: dict
        """
        r = requests.get('https://zenodo.org/api/awards',
            params={'q': f'number:{funding_identifier}'}
            )
        r_json = r.json()
        if r.status_code == 200 and r_json['hits']['total'] == 1:
            return r_json['hits']['hits'][0]
        logger.info(f'Funding identifier {funding_identifier} could not be validated...')
        return {}

    def to_funding(self, funding):
        """
        Convert a CodeMeta funding object to a Zenodo funding object.

        :param funding: CodeMeta funding object
        :type funding: dict or str
        :return: Zenodo funding object
        """
        # Case when funding is a string
        if isinstance(funding, str):
            zenodo_funding = {
                'award': {'title': {"en": funding}},
                'funder': {'name': 'Unknown funder'}
            }
            # Case when funder is provided as a single element (typically with CodeMeta generator)
            if 'funder' in self.data and not isinstance(self.data['funder'], list):
                zenodo_funding['funder'] = self.to_funder(self.data['funder'])
            return zenodo_funding

        # Case when funding is a dictionary
        zenodo_funding = {}
        # Attempt to validate funding identifier
        if 'identifier' in funding:
            validated_funding = self.validate_funding_identifier(funding['identifier'])
            if validated_funding:
                zenodo_funding['award'] = {
                    'id': validated_funding['id']
                }
                zenodo_funding['funder'] = {
                    'id': validated_funding['funder']['id']
                }
        # Fallback to custom funding object
        if not zenodo_funding:
            if 'funder' in funding:
                zenodo_funding['funder'] = self.to_funder(funding['funder'])
            else:
                zenodo_funding['funder'] = {'name': 'Unknown funder'}

            zenodo_funding['award'] = {'title': {"en": funding.get('name', '')}}
            if 'identifier' in funding:
                zenodo_funding['award']['number'] = funding['identifier']
            if 'url' in funding:
                zenodo_funding['award']['identifiers'] = [{
                        'scheme': 'url',
                        'identifier': funding['url']
                    }]
        return zenodo_funding

    def validate_funder_identifier(self, funder_identifier):
        """
        Validate a funder identifier against the Zenodo API. If funder could be validated,
        return the funder identifier, otherwise return None.
        Supports plain identifier or full ROR URL.
        """
        funder_identifier = funder_identifier.replace(self.prefixes['ror'], '')
        r = requests.get('https://zenodo.org/api/funders',
            params={'q': f'id:{funder_identifier}'}
            )
        r_json = r.json()
        if r.status_code == 200 and r_json['hits']['total'] == 1:
            return r_json['hits']['hits'][0]['id']
        logger.info(f'Funder identifier {funder_identifier} could not be validated...')
        return None

    def to_funder(self, funder):
        """
        Convert a CodeMeta funder to a Zenodo funder object.
        """
        zenodo_funder = {}
        if isinstance(funder, str):
            funderid = self.validate_funder_identifier(funder)
        elif isinstance(funder, dict) and 'id' in funder:
            funderid = self.validate_funder_identifier(funder['id'])
        elif isinstance(funder, dict) and '@id' in funder:
            funderid = self.validate_funder_identifier(funder['@id'])
        else:
            funderid = None
        if funderid:
            zenodo_funder['id'] = funderid
        else:
            if isinstance(funder, str):
                zenodo_funder['name'] = funder
            else:
                if 'name' in funder:
                    zenodo_funder['name'] = funder['name']
                elif 'url' in funder:
                    zenodo_funder['name'] = funder['url']
        return zenodo_funder

    def to_related_identifier(self, identifier, relation):
        """
        Convert an identifier to a Zenodo related identifier object.

        :param identifier: Persistent identifier of related publication or dataset.
            Supported identifier schemes:
            ARK, arXiv, Bibcode, DOI, EAN13, EISSN, Handle, IGSN, ISBN, ISSN, ISTC, LISSN, LSID,
            PubMed ID, PURL, UPC, URL, URN, W3ID.
        :type identifier: str
        :param relation: relationship described with controlled vocabulary defined in self.ZENODO_RELATIONSHIPS
        :type relation: str
        :return: Zenodo related identifier object
        :rtype: dict or None
        """
        if relation in self.ZENODO_RELATIONSHIPS:
            zenodo_related_identifier = {
                'relation_type': {'id': relation},
                'identifier': identifier
            }
        else:
            logger.info(f'Relation {relation} is not in the Zenodo controlled vocabulary, skipping...')
            zenodo_related_identifier = None
        return zenodo_related_identifier

    def to_subjects(self, keywords):
        """
        Convert CodeMeta keywords to Zenodo subjects.
        """
        zenodo_subjects = []
        for keyword in keywords:
            if isinstance(keyword, str):
                zenodo_subjects.append({'subject': keyword})
            else:
                if 'name' in keyword:
                    if keyword.get('@type') == 'DefinedTerm' and 'url' in keyword:
                        zenodo_subjects.append({
                            # Should be:
                            # 'id': keyword['url']
                            # but caused an error 500 in Zenodo, to be investigated...
                            'subject': keyword['url']
                        })
                    else:
                        zenodo_subjects.append({'subject': keyword['name']})
        return zenodo_subjects

    def add_to_array_field(self, zenodo_dict, key, value):
        """
        Add an object to a field of type "array" in a Zenodo metadata dictionary.
        Add the field if it doesn't exist yet, append the value to the field otherwise.
        Does nothing if value is None.

        :param zenodo_dict: Zenodo metadata dictionary; will be modified in place
        :param key: key to be added or updated
        :param value: value to be added. If None, the function does nothing.
        """
        if value:
            if key not in zenodo_dict['metadata']:
                zenodo_dict['metadata'][key] = []
            zenodo_dict['metadata'][key].append(value)

    def as_dict(self):
        """
        Prepare Zenodo payload to be passed to the Zenodo API.

        :return: Zenodo metadata dictionary
        """

        zenodo_dict = {
            'metadata': {
                'language': 'eng'
            }
        }

        if 'name' in self.data:
            zenodo_dict['metadata']['title'] = self.data['name']

        if 'alternateName' in self.data:
            self.add_to_array_field(zenodo_dict,
                'additional_titles',
                {
                    'title': self.data['alternateName'],
                    'type': {'id': 'alternative-title'}
                })

        if 'version' in self.data:
            zenodo_dict['metadata']['version'] = self.data['version']

        if 'dateModified' in self.data:
            zenodo_dict['metadata']['publication_date'] = self.data['dateModified']

        if 'sameAs' in self.data:
            related_id = self.to_related_identifier(self.data['sameAs'], 'isidenticalto')
            self.add_to_array_field(zenodo_dict, 'related_identifiers', related_id)

        if 'downloadUrl' in self.data:
            related_id = self.to_related_identifier(self.data['downloadUrl'], 'issourceof')
            self.add_to_array_field(zenodo_dict, 'related_identifiers', related_id)

        if 'referencePublication' in self.data \
            and self.data['referencePublication'].get('@id', '').startswith(self.prefixes['doi']):
            related_id = self.to_related_identifier(self.data['referencePublication']['@id'], 'isdocumentedby')
            self.add_to_array_field(zenodo_dict, 'related_identifiers', related_id)

        if 'codeRepository' in self.data:
            related_id = self.to_related_identifier(self.data['codeRepository'], 'issupplementto')
            self.add_to_array_field(zenodo_dict, 'related_identifiers', related_id)

        if 'author' in self.data:
            for author in self.data['author']:
                zenodo_creator = self.to_person_or_org(author)
                self.add_to_array_field(zenodo_dict, 'creators', zenodo_creator)

        if 'contributor' in self.data:
            for contributor in self.data['contributor']:
                if 'additionalType' in contributor and contributor['additionalType'] in self.ZENODO_CONTRIBUTORTYPES:
                    contributor_type = contributor['additionalType']
                else:
                    contributor_type = 'other'
                zenodo_contributor = self.to_person_or_org(contributor, contributor_type)
                self.add_to_array_field(zenodo_dict, 'contributors', zenodo_contributor)

        if 'description' in self.data:
            zenodo_dict['metadata']['description'] = self.data['description']

        if 'keywords' in self.data:
            zenodo_dict['metadata']['subjects'] = self.to_subjects(self.data['keywords'])

        if 'publisher' in self.data:
            zenodo_publisher = self.to_person_or_org(self.data['publisher'], 'distributor')
            self.add_to_array_field(zenodo_dict, 'contributors', zenodo_publisher)

        # Put it in "keywords" as no field seems to correspond
        if 'applicationCategory' in self.data:
            self.add_to_array_field(zenodo_dict,
                                    'subjects',
                                    {'subject': self.data['applicationCategory']}
                                    )

        if self.data.get('@type') == 'SoftwareSourceCode':
                zenodo_dict['metadata']['resource_type'] = {'id': 'software'}

        if 'license' in self.data:
            if not isinstance(self.data['license'], list):
                licenses = [self.data['license']]
            else:
                licenses = self.data['license']
            for license in licenses:
                self.add_to_array_field(zenodo_dict, 'rights', self.to_rights(license))

        if 'copyrightHolder' in self.data:
            for copyright_holder in self.data['copyrightHolder']:
                zenodo_rights_holder = self.to_person_or_org(copyright_holder, 'rightsholder')
                self.add_to_array_field(zenodo_dict, 'contributors', zenodo_rights_holder)

        if 'funding' in self.data:
            if not isinstance(self.data['funding'], list):
                fundings = [self.data['funding']]
            else:
                fundings = self.data['funding']
            for funding in fundings:
                zenodo_funding = self.to_funding(funding)
                if zenodo_funding:
                    self.add_to_array_field(zenodo_dict, 'funding', zenodo_funding)

        logger.debug('zenodo_dict = %s', json.dumps(zenodo_dict, indent=2))
        return zenodo_dict
