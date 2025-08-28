# Metadata crosswalk in FACILE-RS

| Codemeta field               | Type / pattern                          | CFF field                  | CFF value (if different)                                              |
| ---------------------------- | --------------------------------------- | -------------------------- | --------------------------------------------------------------------- |
| name                         | str                                     | title                      |                                                                       |
| description                  | str                                     | abstract                   |                                                                       |
| @id, id, identifier          | str                                     | doi                        | original value without prefix 'https://doi.org/'                      |
| sameAs                       | str                                     | url                        |                                                                       |
| version                      | str                                     | version                    |                                                                       |
| dateModified                 | str                                     | date-released              | original value in format '%Y-%m-%d'                                   |
| author                       | list[dict]                              | authors                    |                                                                       |
| &emsp;[i].name               | str                                     | &emsp;[i].name             |                                                                       |
| &emsp;[i].givenName          | str                                     | &emsp;[i].given-names      |                                                                       |
| &emsp;[i].familyName         | str                                     | &emsp;[i].family-names     |                                                                       |
| &emsp;[i].@id                | str, starting with 'https://orcid.org/' | &emsp;[i].orcid            |                                                                       |
| license                      | str                                     | license                    | original value, without prefix 'https://spdx.org/licenses/' if present|
| license                      | dict                                    | license and/or license-url | details below                                                         |
| &emsp;.name                  | str                                     | license                    |                                                                       |
| &emsp;.url                   | str                                     | license-url                |                                                                       |
| codeRepository               | str                                     | repository-code            |                                                                       |
| referencePublication         | dict                                    | preferred-citation         |                                                                       |
| &emsp;.@type                 | str == 'ScholarlyArticle'               | &emsp;.type                | article                                                               |
| &emsp;.@id                   | str, starting with 'https://orcid.org/' | &emsp;.doi                 | original value without prefix 'https://doi.org/'                      |
| &emsp;.name                  | str                                     | &emsp;.title               |                                                                       |
| &emsp;.isPartOf.isPartOf.name| str                                     | &emsp;.journal             |                                                                       |
| &emsp;.isPartOf.volumeNumber | str                                     | &emsp;.volume              |                                                                       |
| &emsp;.isPartOf.datePublished| str                                     | &emsp;.year                |                                                                       |
| &emsp;.pageStart             | str                                     | &emsp;.pages               |                                                                       |
| &emsp;.pageEnd               | str                                     | &emsp;.pages               | value above + '-' + this value                                        |
| &emsp;.author                | list[dict]                              | &emsp;.authors             | built on the same model as field "author"                             |
| identifier                   | dict (schema.org DOI identifier)        | identifiers                | List of identifiers containing a single element                       |
| &emsp;.propertyID            | str == 'DOI'                            | &emsp;[0].type             | 'doi'                                                                 |
| &emsp;.value                 | str                                     | &emsp;[0].value            |                                                                       |
| &emsp;.description           | str                                     | &emsp;[0].description      |                                                                       |
| identifier                   | list[dict] (schema.org DOI identifiers) | identifiers                | List of identifiers, each element built as above                      |
