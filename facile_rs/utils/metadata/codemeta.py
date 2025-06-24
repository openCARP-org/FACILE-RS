import json
import logging

from ..http import fetch_dict

logger = logging.getLogger(__file__)


class CodemetaMetadata:

    """A class for storing and manipulating metadata in the CodeMeta format"""

    def __init__(self):
        """Initialize metadata set as an empty dictionary."""
        self.data = {}

    def fetch(self, location):
        """Update metadata set with data fetched from a CodeMeta file

        :param location: URL or path to the CodeMeta JSON file
        :type location: str
        """
        if location:
            self.data.update(fetch_dict(location))

    def fetch_authors(self, locations):
        """Fetch authors from CodeMeta files and update metadata set

        :param locations: list of URL or paths to CodeMeta files
        :param locations: list
        """
        if locations:
            if 'author' not in self.data:
                self.data['author'] = []
            # Case when there is a unique author not contained in a list
            elif isinstance(self.data['author'], dict):
                self.data['author'] = [self.data['author']]
            for location in locations:
                self.data['author'] += fetch_dict(location).get('author', [])

    def fetch_contributors(self, locations):
        """Fetch contributors from CodeMeta files and update metadata set

        :param locations: list of URL or paths to CodeMeta files
        :param locations: list
        """
        if locations:
            if 'contributor' not in self.data:
                self.data['contributor'] = []
            # Case when there is a unique contributor not contained in a list
            elif isinstance(self.data['contributor'], dict):
                self.data['contributor'] = [self.data['contributor']]
            for location in locations:
                self.data['contributor'] += fetch_dict(location).get('contributor', [])

    def compute_names(self):
        """Add full name of authors and contributors in metadata set from given name and family name,
        under the dictionary key 'name'.
        """
        for key in ['author', 'contributor']:
            if key in self.data:
                for thing in self.data[key]:
                    if 'name' not in thing and ('givenName' in thing and 'familyName' in thing):
                        thing['name'] = '{} {}'.format(thing['givenName'], thing['familyName'])

    def remove_doubles(self):
        """Remove duplicates in authors and contributors lists, comparing names (key: name), concatenation of keys
        givenName and familyName, and ids (key: @id).
        """
        for key in ['author', 'contributor']:
            if key in self.data:
                ids = set()
                names = set()
                givenAndFamilyNames = set()
                things = []
                if not isinstance(self.data[key], list):
                    data_list = [self.data[key]]
                else:
                    data_list = self.data[key]
                for thing in data_list:
                    thing_id = thing.get('@id')
                    thing_name = thing.get('name')
                    thing_givenAndFamilyName = None
                    if 'givenName' in thing and 'familyName' in thing:
                        thing_givenAndFamilyName = '{} {}'.format(thing['givenName'], thing['familyName'])
                    if thing_id in ids or thing_name in names or thing_givenAndFamilyName in givenAndFamilyNames:
                        pass
                    else:
                        things.append(thing)
                        if thing_id is not None:
                            ids.add(thing_id)
                        if thing_name is not None:
                            names.add(thing_name)
                        if thing_givenAndFamilyName is not None:
                            givenAndFamilyNames.add(thing_givenAndFamilyName)
                self.data[key] = things

    def sort_persons(self):
        """Sort authors and contributors alphabetically based on family name."""
        def get_key(item):
            key = item.get('familyName', item.get('name', ''))

            if item.get('@type') == 'Organization':
                # put organzations first unless they have an additionalType
                if item.get('additionalType') is None:
                    key = '!' + key
                else:
                    key = '~' + key

            return key

        if 'author' in self.data:
            self.data['author'] = sorted(self.data['author'], key=get_key)
        if 'contributor' in self.data:
            self.data['contributor'] = sorted(self.data['contributor'], key=get_key)

    def to_json(self):
        """Dump metadata set as JSON-formatted string.

        :return: metadata set as JSON-formatted string
        :rtype: str
        """
        return json.dumps(self.data, indent=2, ensure_ascii=False)
