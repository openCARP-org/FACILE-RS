import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__file__)


class RadarMetadata:

    doi_prefix = 'https://doi.org/'
    orcid_prefix = 'https://orcid.org/'
    ror_prefix = 'https://ror.org/'

    # map SPDX to Radar licenses
    radar_licenses = {
        "": "PUBLIC_DOMAIN_MARK_1_0",  # SPDX doesn't consider it a license https://github.com/spdx/license-list-XML/issues/988
        "PDDL-1.0": "PUBLIC_DOMAIN_DEDICATION_AND_LICENSE_PDDL",
        "ODC-By-1.0": "ATTRIBUTION_LICENSE_ODC_BY",
        "ODbL-1.0": "OPEN_DATABASE_LICENSE_ODC_O_DB_L",
        "Apache-2.0": "APACHE_LICENSE_2_0",
        "CDDL-1.0": "COMMON_DEVELOPMENT_AND_DISTRIBUTION_LICENSE_1_0",
        "EPL-1.0": "ECLIPSE_PUBLIC_LICENSE_1_0",
        "EPL-2.0": "ECLIPSE_PUBLIC_LICENSE_2_0",
        "GPL-3.0-only": "GNU_GENERAL_PUBLIC_LICENSE_V_3_0_ONLY",
        "LGPL-3.0": "GNU_LESSER_GENERAL_PUBLIC_LICENSE_V_3_0_ONLY",
        "BSD-2-Clause": "BSD_2_CLAUSE_SIMPLIFIED_LICENSE",
        "BSD-3-Clause": "BSD_3_CLAUSE_NEW_OR_REVISED_LICENSE",
        "MIT": "MIT_LICENSE"
    }

    def __init__(self, data, responsible_email, publication_backlink):
        """
        Initialize the RadarMetadata object from CodeMeta metadata.

        :param data: CodeMeta metadata, typically the data attribute of a CodemetaMetadata instance.
        :type data: dict
        :param responsible_email: email address of the contact person
        :type responsible_email: str
        :param publication_backlink: URL to the publication
        :type publication_backlink: str
        """
        self.data = data
        self.responsible_email = responsible_email
        self.publication_backlink = publication_backlink
        logger.debug('data = %s', self.data)

    def radar_value(self, string):
        """converts CamelCase to all caps and underscores, e.g. HostingInstitution -> HOSTING_INSTITUTION
        """
        return '_'.join([s.upper() for s in re.findall('([A-Z][a-z]+)', string)])

    def as_dict(self):
        """
        Prepare RADAR payload to be passed to the RADAR API.

        :return: RADAR metadata dictionary
        """
        archive_date = datetime.utcnow()

        radar_dict = {
            'technicalMetadata': {
                "retentionPeriod": 10,
                "archiveDate": int(archive_date.timestamp()),
                "responsibleEmail": self.responsible_email,
                "publicationBacklink": self.publication_backlink,
                "schema": {
                    "key": "RDDM",
                    "version": "9.1"
                }
            },
            'descriptiveMetadata': {
                'language': 'ENG',
                'resource': {}
            }
        }

        if 'identifier' in self.data and isinstance(self.data['identifier'], list):
            for identifier in self.data['identifier']:
                if identifier.get('propertyID') == 'RADAR':
                    radar_dict['id'] = identifier['value']

        if 'name' in self.data:
            radar_dict['descriptiveMetadata']['title'] = self.data['name']

        if 'dateModified' in self.data:
            production_year = datetime.strptime(self.data.get('dateModified'), '%Y-%m-%d')
            publish_date = datetime.strptime(self.data['dateModified'], '%Y-%m-%d')

            radar_dict['technicalMetadata']['publishDate'] = int(publish_date.timestamp())
            radar_dict['descriptiveMetadata']['productionYear'] = production_year.year
            radar_dict['descriptiveMetadata']['publicationYear'] = publish_date.year

        if 'sameAs' in self.data:
            radar_dict['descriptiveMetadata']['alternateIdentifiers'] = {
                'alternateIdentifier': []
            }
            radar_dict['descriptiveMetadata']['alternateIdentifiers']['alternateIdentifier'].append({
                'value': self.data['sameAs'],
                'alternateIdentifierType': 'URL'
            })

        if 'downloadUrl' in self.data:
            radar_dict['descriptiveMetadata']['alternateIdentifiers'] = {
                'alternateIdentifier': []
            }
            radar_dict['descriptiveMetadata']['alternateIdentifiers']['alternateIdentifier'].append({
                'value': self.data['downloadUrl'],
                'alternateIdentifierType': 'URL'
            })

        if any(key in self.data for key in ['referencePublication', 'codeRepository']):
            radar_dict['descriptiveMetadata']['relatedIdentifiers'] = {
                'relatedIdentifier': []
            }
            if 'referencePublication' in self.data and \
                    self.data['referencePublication'].get('@id', '').startswith(self.doi_prefix):
                radar_dict['descriptiveMetadata']['relatedIdentifiers']['relatedIdentifier'].append({
                    'value': self.data['referencePublication']['@id'].replace(self.doi_prefix, ''),
                    'relatedIdentifierType': 'DOI',
                    'relationType': self.radar_value('IsDocumentedBy')
                })
            if 'codeRepository' in self.data:
                radar_dict['descriptiveMetadata']['relatedIdentifiers']['relatedIdentifier'].append({
                    'value': self.data['codeRepository'],
                    'relatedIdentifierType': 'URL',
                    'relationType': self.radar_value('IsSupplementTo')  # like zenodo does it
                })

        if 'author' in self.data:
            radar_dict['descriptiveMetadata']['creators'] = {
                'creator': []
            }

            for author in self.data['author']:
                if 'name' in author:
                    radar_creator = {
                        'creatorName': author['name']
                    }

                    if 'givenName' in author:
                        radar_creator['givenName'] = author['givenName']

                    if 'familyName' in author:
                        radar_creator['familyName'] = author['familyName']

                    if '@id' in author:
                        if author['@id'].startswith(self.orcid_prefix):
                            radar_creator['nameIdentifier'] = [{
                                'value': author['@id'].replace(self.orcid_prefix, ''),
                                'schemeURI': 'http://orcid.org',
                                'nameIdentifierScheme': 'ORCID',
                            }]

                    for affiliation in author.get('affiliation', []):
                        if 'name' in affiliation:
                            radar_creator['creatorAffiliation'] = {
                                'value': affiliation['name']
                            }
                            if '@id' in affiliation and affiliation['@id'].startswith(self.ror_prefix):
                                radar_creator['creatorAffiliation'].update({
                                    'schemeURI': 'https://ror.org',
                                    'affiliationIdentifier': affiliation['@id'],
                                    'affiliationIdentifierScheme': 'ROR'
                                })

                    radar_dict['descriptiveMetadata']['creators']['creator'].append(radar_creator)

        if 'contributors' in self.data:
            radar_dict['descriptiveMetadata']['contributors'] = {
                'contributor': []
            }

            for contributor in self.data['contributors']:
                if 'name' in contributor:
                    radar_contributor = {
                        'contributorName': author['name'],
                        'contributorType': self.radar_value(contributor['additionalType'])
                    }

                    if contributor.get('@type') == 'Person':
                        radar_contributor['givenName'] = contributor['givenName']
                        radar_contributor['familyName'] = contributor['familyName']

                        if '@id' in contributor:
                            if contributor['@id'].startswith(self.orcid_prefix):
                                radar_contributor['nameIdentifier'] = [{
                                    'value': contributor['@id'].replace(self.orcid_prefix, ''),
                                    'schemeURI': 'http://orcid.org',
                                    'nameIdentifierScheme': 'ORCID',
                                }]

                        for affiliation in contributor.get('affiliation', []):
                            if 'name' in affiliation:
                                radar_creator['contributorAffiliation'] = {
                                    'value': affiliation['name']
                                }
                                if '@id' in affiliation and affiliation['@id'].startswith(self.ror_prefix):
                                    radar_creator['contributorAffiliation'].update({
                                        'schemeURI': 'https://ror.org',
                                        'affiliationIdentifier': affiliation['@id'],
                                        'affiliationIdentifierScheme': 'ROR'
                                    })

                radar_dict['descriptiveMetadata']['contributors']['contributor'].append(radar_contributor)

        if 'alternateName' in self.data:
            radar_dict['descriptiveMetadata']['additionalTitles'] = {
                'additionalTitle': []
            }
            radar_dict['descriptiveMetadata']['additionalTitles']['additionalTitle'].append({
                'value': self.data['alternateName'],
                'additionalTitleType': self.radar_value('AlternativeTitle')
            })

        if 'description' in self.data:
            radar_dict['descriptiveMetadata']['descriptions'] = {
                'description': []
            }
            radar_dict['descriptiveMetadata']['descriptions']['description'].append({
                'value': self.data['description'],
                'descriptionType': self.radar_value('Abstract')
            })

        if 'keywords' in self.data:
            keywords = []
            subjects = []
            for keyword in self.data['keywords']:
                if isinstance(keyword, str):
                    keywords.append(keyword)

                else:
                    if 'name' in keyword and \
                            keyword.get('@type') == 'DefinedTerm' and \
                            keyword.get('inDefinedTermSet', '').startswith('https://www.radar-service.eu/schemas/'):
                        subjects.append(keyword['name'])

            if keywords:
                radar_dict['descriptiveMetadata']['keywords'] = {
                    'keyword': []
                }
                for keyword in keywords:
                    radar_dict['descriptiveMetadata']['keywords']['keyword'].append({
                        'value': keyword
                    })

            if subjects:
                radar_dict['descriptiveMetadata']['subjectAreas'] = {
                    'subjectArea': []
                }
                for subject in subjects:
                    radar_dict['descriptiveMetadata']['subjectAreas']['subjectArea'].append({
                        'controlledSubjectAreaName': self.radar_value(subject)
                    })

        if 'publisher' in self.data and 'name' in self.data['publisher']:
            radar_dict['descriptiveMetadata']['publishers'] = {
                'publisher': []
            }
            radar_publisher = {
                'value': self.data['publisher']['name']
            }

            if '@id' in self.data['publisher'] and self.data['publisher']['@id'].startswith(self.ror_prefix):
                radar_publisher.update({
                    'schemeURI': 'https://ror.org',
                    'nameIdentifier': self.data['publisher']['@id'],
                    'nameIdentifierScheme': 'ROR'
                })

            radar_dict['descriptiveMetadata']['publishers']['publisher'].append(radar_publisher)

        if 'applicationCategory' in self.data:
            radar_dict['descriptiveMetadata']['resource'] = {
                'value': self.data['applicationCategory']
            }

        if self.data.get('@type') == 'SoftwareSourceCode':
                radar_dict['descriptiveMetadata']['resource']['resourceType'] = self.radar_value('Software')

        if 'license' in self.data:
            licenseName = ""
            if isinstance(self.data['license'], str):
                licenseName = self.data['license']
            elif isinstance(self.data['license'], dict) and 'name' in self.data['license']:
                licenseName = self.data['license']['name']

            # CodeMeta wants the license to be a URL or a creative work, RADAR is only interested in the name
            if licenseName.startswith("https://spdx.org/licenses/"):
                licenseName = licenseName.replace("https://spdx.org/licenses/", "")

            for spdx_name, radar_name in self.radar_licenses.items():
                if spdx_name:
                    licenseName = licenseName.replace(spdx_name, radar_name)

            if licenseName in list(self.radar_licenses.values()):
                radar_dict['descriptiveMetadata']['rights'] = {
                    'controlledRights': licenseName
                }
            else:
                radar_dict['descriptiveMetadata']['rights'] = {
                    'controlledRights': 'OTHER',
                    'additionalRights': licenseName
                }

        if 'copyrightHolder' in self.data:
            radar_dict['descriptiveMetadata']['rightsHolders'] = {
                'rightsHolder': []
            }
            for copyright_holder in self.data['copyrightHolder']:
                if 'name' in copyright_holder:
                    radar_rights_holder = {
                        'value': copyright_holder['name']
                    }

                    if '@id' in copyright_holder and copyright_holder['@id'].startswith(self.ror_prefix):
                        radar_rights_holder.update({
                            'schemeURI': 'https://ror.org',
                            'nameIdentifier': copyright_holder['@id'],
                            'nameIdentifierScheme': 'ROR'
                        })

                radar_dict['descriptiveMetadata']['rightsHolders']['rightsHolder'].append(radar_rights_holder)

        if 'funding' in self.data:
            radar_dict['descriptiveMetadata']['fundingReferences'] = {
                'fundingReference': []
            }
            for funding in self.data['funding']:
                radar_funding_reference = {}

                if 'funder' in funding:
                    if 'name' in funding['funder']:
                        radar_funding_reference['funderName'] = funding['funder']['name']

                    if '@id' in funding['funder'] and funding['funder']['@id'].startswith(self.ror_prefix):
                        radar_funding_reference['funderIdentifier'] = {
                            'value': funding['funder']['@id'],
                            'schemeURI': 'https://ror.org',
                            'type': 'ROR'
                        }

                if 'identifier' in funding:
                    radar_funding_reference['awardNumber'] = funding['identifier']
                if 'url' in funding:
                    radar_funding_reference['awardURI'] = funding['url']
                if 'name' in funding:
                    radar_funding_reference['awardTitle'] = funding['name']

                radar_dict['descriptiveMetadata']['fundingReferences']['fundingReference'].append(radar_funding_reference)

        logger.debug('radar_dict = %s', json.dumps(radar_dict, indent=2))
        return radar_dict
