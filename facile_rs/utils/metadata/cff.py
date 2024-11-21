import logging
from datetime import datetime

import yaml

logger = logging.getLogger(__file__)


class CffMetadata:

    """A class for creating CFF citation files from CodeMeta metadata"""

    doi_prefix = 'https://doi.org/'
    orcid_prefix = 'https://orcid.org/'
    ror_prefix = 'https://ror.org/'

    name_types = {
        'Person': 'Personal',
        'Organization': 'Organizational'
    }

    def __init__(self, data):
        """Initialization from a CodeMeta metadata dictionary.

        :param data: data attribute of a class:CodemetaMetadata instance
        :type data: dict
        """
        self.data = data
        logger.debug('data = %s', self.data)

    def to_yaml(self):
        """Convert metadata to CFF format.

        :return: Content of the CFF file
        :rtype: str
        """
        cff_json = {
            'cff-version': '1.2.0',
            'message': 'If you use this software, please cite the paper describing it as below. '
                       'Specific versions of the software can additionally be referenced using individual DOIs.',
            'type': 'software'
        }

        if 'name' in self.data:
            cff_json['title'] = self.data['name']

        if 'description' in self.data:
            cff_json['abstract'] = self.data['description']

        # Check if a DOI is provided
        id_keys = ['@id', 'identifier', 'id']
        for id_key in id_keys:
            if id_key in self.data and isinstance(self.data[id_key], str):
                if self.data[id_key].startswith(self.doi_prefix):
                    cff_json['doi'] = self.data[id_key].replace(self.doi_prefix, '')
                    break

        if 'sameAs' in self.data:
            cff_json['url'] = self.data['sameAs']

        if 'version' in self.data:
            cff_json['version'] = self.data['version']

        if 'dateModified' in self.data:
            cff_json['date-released'] = datetime.strptime(self.data['dateModified'], '%Y-%m-%d').date()

        if 'author' in self.data:
            cff_json['authors'] = []
            for author in self.data['author']:
                cff_author = {}

                if 'name' in author:
                    cff_author['name'] = author['name']

                if 'givenName' in author:
                    cff_author['given-names'] = author['givenName']

                if 'familyName' in author:
                    cff_author['family-names'] = author['familyName']

                if '@id' in author and author['@id'].startswith(self.orcid_prefix):
                    cff_author['orcid'] = author['@id']

                if cff_author:
                    cff_json['authors'].append(cff_author)

        if 'license' in self.data:
            if isinstance(self.data['license'], str):
                cff_json['license'] = self.data['license']
                # CodeMeta wants the license to be a URL or a creative work, CFF is only interested in the name
                if cff_json['license'].startswith("https://spdx.org/licenses/"):
                    cff_json['license'] = cff_json['license'].replace("https://spdx.org/licenses/", "")
            elif isinstance(self.data['license'], dict):
                self.data['license']['name']
                if 'name' in self.data['license']:
                    cff_json['license'] = self.data['license']['name']
                if 'url' in self.data['license']:
                    cff_json['license-url'] = self.data['license']['url']

        if 'codeRepository' in self.data:
            cff_json['repository-code'] = self.data['codeRepository']

        if 'referencePublication' in self.data:
            cff_json['preferred-citation'] = {}

            if '@type' in self.data['referencePublication']:
                if self.data['referencePublication']['@type'] == 'ScholarlyArticle':
                    cff_json['preferred-citation']['type'] = 'article'

            if '@id' in self.data['referencePublication'] and \
                    self.data['referencePublication']['@id'].startswith(self.doi_prefix):
                cff_json['preferred-citation']['doi'] = \
                    self.data['referencePublication']['@id'].replace(self.doi_prefix, '')

            if 'name' in self.data['referencePublication']:
                cff_json['preferred-citation']['title'] = self.data['referencePublication']['name']

            if 'isPartOf' in self.data['referencePublication']:
                if 'isPartOf' in self.data['referencePublication']['isPartOf']:
                    if 'name' in self.data['referencePublication']['isPartOf']['isPartOf']:
                        cff_json['preferred-citation']['journal'] = \
                            self.data['referencePublication']['isPartOf']['isPartOf']['name']

                if 'volumeNumber' in self.data['referencePublication']['isPartOf']:
                    cff_json['preferred-citation']['volume'] = \
                        int(self.data['referencePublication']['isPartOf']['volumeNumber'])

                if 'datePublished' in self.data['referencePublication']['isPartOf']:
                    cff_json['preferred-citation']['year'] = \
                        int(self.data['referencePublication']['isPartOf']['datePublished'])

            if 'pageStart' in self.data['referencePublication']:
                cff_json['preferred-citation']['pages'] = self.data['referencePublication']['pageStart']

            if 'pageEnd' in self.data['referencePublication']:
                cff_json['preferred-citation']['pages'] += "-" + self.data['referencePublication']['pageEnd']

            if 'author' in self.data['referencePublication']:
                cff_json['preferred-citation']['authors'] = []
                for author in self.data['referencePublication']['author']:
                    cff_citation_author = {}

                    if 'familyName' in author:
                        cff_citation_author['family-names'] = author['familyName']

                    if 'givenName' in author:
                        cff_citation_author['given-names'] = author['givenName']

                    if '@id' in author and author['@id'].startswith(self.orcid_prefix):
                        cff_citation_author['orcid'] = author['@id']

                    cff_json['preferred-citation']['authors'].append(cff_citation_author)

        # Case when identifier follows https://schema.org/identifier schema
        if 'identifier' in self.data and isinstance(self.data['identifier'], dict):
            cff_json['identifiers'] = [schema_org_identifier_to_cff(self.data['identifier'], cff_json)]
        elif 'identifier' in self.data and isinstance(self.data['identifier'], list):
            cff_json['identifiers'] = []
            for identifier in self.data['identifier']:
                cff_identifier = schema_org_identifier_to_cff(identifier, cff_json)
                if cff_identifier:
                    cff_json['identifiers'].append(cff_identifier)

        return yaml.dump(cff_json, allow_unicode=True, sort_keys=False, default_flow_style=False)


def schema_org_identifier_to_cff(identifier, cff_json=None):
    """ Converts schema.org identifier to CFF identifier.
    Supports only DOI identifiers for now. Returns an empty dict if identifier is not a schema.org-compliant
    DOI identifier.

    :param identifier: schema.org compliant DOI identifier
    :type identifier: dict
    :param cff_json: dictionary containing CFF-formatted metadata
    :type cff_json: dict, optional
    :return: CFF-formatted DOI identifier or empty dict if identifier was not compliant.
    :rtype: dict
    """
    cff_identifier = {}
    if cff_json is None:
        cff_json = {}
    if 'propertyID' in identifier and identifier['propertyID'] == "DOI":
        if 'title' in cff_json and 'version' in cff_json:
            cff_identifier['description'] = "This is the archived snapshot of version {} of {}".format(
                cff_json['version'], cff_json['title']
            )
        cff_identifier['type'] = 'doi'
        if 'value' in identifier:
            cff_identifier['value'] = identifier['value']
    return cff_identifier
