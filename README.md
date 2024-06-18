# FACILE-RS

This package (previously known as openCARP-CI) contains a set of Python scripts which can be used to perform tasks around the archival and long term preservation of software repositories. In particular, it can be used to:

* create a release in GitLab using the GitLab API,
* create a DataCite record based on codemeta files present in repositories,
* create archive packages in the [BagIt](https://tools.ietf.org/html/rfc8493) or [BagPack](https://www.rd-alliance.org/system/files/Research%20Data%20Repository%20Interoperability%20WG%20-%20Final%20Recommendations_reviewed_0.pdf) formats.
* archive the software using the [RADAR service](https://www.radar-service.eu),
* use content from markdown files, bibtex files, or python docstrings to create web pages in a [Grav CMS](https://getgrav.org/).

The scripts were created for the [openCARP](https://opencarp.org) simulation software, but can be adopted for arbitray projects. While they can be used on the command line, the scripts are mainly used within the GitLab CI to run automatically on each push to a repository, or when a tag is created.

An example of integration in a CI environment can be found in the [KIT project template](https://gitlab.kit.edu/kit/fair-rs/public/template-instance). An example of a more complex setup are the [openCARP CI file](https://git.opencarp.org/openCARP/openCARP/-/blob/master/.gitlab-ci.yml) and the [included subscripts](https://git.opencarp.org/openCARP/openCARP/-/tree/master/.gitlab/ci).


## Setup

To use the scripts whithin the GitLab CI, add the following to your job:

```yaml
  before_script:
  - pip install git+https://git.opencarp.org/openCARP/FACILE-RS
```

In order to run the scripts on the command line, we recommend to use a [virtual environment](https://docs.python.org/3/library/venv.html):

```bash
python -m venv env
source env/bin/activate
pip install git+https://git.opencarp.org/openCARP/FACILE-RS
```

### Adapting CI from FACILE-RS

You can adapt the automated pipelines from this repository by copying `.gitlab-ci.yml` and `.gitlab/` to your project.

For the publication in releases you need to add an access token. Go to your repository and then in Settings -> Access Tokens, choose the name of your token, Expiration date (can be removed), role as a Maintainer and Scopes as `api` and `write_repository`. After the token has been created, copy its value and go to your repository, Settings -> CI/CD -> Variables and choose Add Variable. As a key write `PUSH_TOKEN` and as value paste the copied token. Then create a variable with key `PRIVATE_TOKEN` and as value enter `$PUSH_TOKEN` (which will be expanded to the value defined previously).

If you don't want to trigger releases on RADAR, you can deactivate the RADAR jobs by setting `ENABLE_RADAR` to "false" in [`.gitlab-ci.yml`](https://git.opencarp.org/openCARP/FACILE-RS/-/blob/master/.gitlab-ci.yml#L35).


## Documentation

[![Documentation Status](https://readthedocs.org/projects/facile-rs/badge/?version=latest)](https://facile-rs.readthedocs.io/en/latest/?badge=latest)

The API documentation is available at https://facile-rs.readthedocs.io/.

It can also be generated using Sphinx from [docs/sphinxdocs](./docs/sphinxdocs) by running:
```
make html
```
The Python packages in [docs/sphinxdocs/requirements.txt](./docs/sphinxdocs/requirements.txt) as well as FACILE-RS itself must be installed to generate the documentation.

## Usage

Each of the scripts expects a number of command line arguments. Default values can be set using environment variables (using upper case and underscores), i.e. the following lines do the same:

```bash
create_bag --bag-path=/path/to/bag
BAG_PATH=/path/to/bag create_bag
```

Environments variables can be set in the usual way, e.g. the `.gitlab-ci.yml` file, but also in a `.env` file in the directory where the script is invoked.

The following scripts are included:

### create_cff

Creates a [Citation File Format](https://citation-file-format.github.io) (CFF) file from your CodeMeta file.
An example output can be found [here](https://git.opencarp.org/openCARP/openCARP/-/blob/master/CITATION.cff).

```
usage: create_cff     [-h] [--codemeta-location CODEMETA_LOCATION]
                      [--creators-location CREATORS_LOCATION]
                      [--contributors-location CONTRIBUTORS_LOCATION]
                      [--cff-path CFF_PATH]
                      [--log-level LOG_LEVEL] [--log-file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --codemeta-location CODEMETA_LOCATION
                        Location of the main codemeta.json JSON file
  --creators-location CREATORS_LOCATIONS
                        Locations of codemeta JSON files for additional creators
  --contributors-location CONTRIBUTORS_LOCATIONS
                        Locations of codemeta JSON files for additional contributors
  --cff-path CFF_PATH
                        Path to the cff output file
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### prepare_release

Updates the CodeMeta file for the given `VERSION` and `DATE` (as `dateModified`, current date if omitted). Useful to automatically get the version from a git tag and inject it into the repo's metadata file.

```
usage: prepare_release [-h] [--codemeta-location CODEMETA_LOCATION] [--version VERSION]
                       [--date DATE] [--log-level LOG_LEVEL] [--log-file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --codemeta-location CODEMETA_LOCATION
                        Location of the main codemeta.json JSON file
  --version VERSION     Version of the resource
  --date DATE           Date for dateModified (format: '%Y-%m-%d')
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### create_release

Creates a release in GitLab using the GitLab API. A tag for the release needs to be created before and provided to the script.
An example output can be found [here](https://git.opencarp.org/openCARP/openCARP/-/releases).

```
usage: create_release [-h] [--release-tag RELEASE_TAG]
                      [--release-description RELEASE_DESCRIPTION]
                      [--release-api-url RELEASE_API_URL] [--private-token PRIVATE_TOKEN]
                      [--dry] [--log-level LOG_LEVEL] [--log-file LOG_FILE]
                      [assets [assets ...]]

positional arguments:
  assets                Assets to be included in the release.

optional arguments:
  -h, --help            show this help message and exit
  --release-tag RELEASE_TAG
                        Tag for the release.
  --release-description RELEASE_DESCRIPTION
                        Description for the release.
  --release-api-url RELEASE_API_URL
                        API URL to create the release.
  --private-token PRIVATE_TOKEN
                        The PRIVATE_TOKEN to be used with the GitLab API.
  --dry                 Perform a dry run, do not perfrom the final request.
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### create_datacite

Creates a DataCite XML file following the [DataCite Metadata Schema 4.3](https://schema.datacite.org/meta/kernel-4.3/). The information needed for this can be taken from (a list) of locations given as URL or local file path. `CODEMETA_LOCATION` must point to a [codemeta.json](https://codemeta.github.io) file. `CREATORS_LOCATIONS` and `CONTRIBUTORS_LOCATIONS` point to similar files which contain a list of `creators` or `contributors`, repectively.

For an example, see [here](https://git.opencarp.org/openCARP/openCARP/blob/master/codemeta.json).

```
usage: create_datacite [-h] [--codemeta-location CODEMETA_LOCATION]
                       [--creators-location CREATORS_LOCATIONS]
                       [--contributors-location CONTRIBUTORS_LOCATIONS] [--version VERSION]
                       [--issued ISSUED] [--datacite-path DATACITE_PATH]
                       [--log-level LOG_LEVEL] [--log-file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --codemeta-location CODEMETA_LOCATION
                        Location of the maim codemeta.json file
  --creators-location CREATORS_LOCATIONS
                        Locations of codemeta JSON files for additional creators
  --contributors-location CONTRIBUTORS_LOCATIONS
                        Locations of codemeta JSON files for additional contributors
  --version VERSION     Version of the resource
  --issued ISSUED       Date for the Issued field and publication year (format: '%Y-%m-%d')
  --datacite-path DATACITE_PATH
                        Path to the DataCite XML output file
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### create_bag

Creates a bag [BagIt](https://tools.ietf.org/html/rfc8493) using the [bagit-python](https://github.com/LibraryOfCongress/bagit-python) package. The assets to be included in the bag are given as positional arguments.

```
usage: create_bag [-h] [--bag-path BAG_PATH] [--bag-info-location BAG_INFO_LOCATIONS]
                  [--log-level LOG_LEVEL] [--log-file LOG_FILE]
                  [assets [assets ...]]

positional arguments:
  assets                Assets to be added to the bag.

optional arguments:
  -h, --help            show this help message and exit
  --bag-path BAG_PATH   Path to the Bag directory
  --bag-info-location BAG_INFO_LOCATIONS
                        Locations of the bog-info YAML files
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### create_bagpack

Creates a bag [BagIt](https://tools.ietf.org/html/rfc8493) similar to `create_bag.py`, but also includes a DataCite XML file as recomended by the [RDA Research Data Repository Interoperability WG](https://www.rd-alliance.org/system/files/Research%20Data%20Repository%20Interoperability%20WG%20-%20Final%20Recommendations_reviewed_0.pdf).

```
usage: create_bagpack [-h] [--bag-path BAG_PATH] [--bag-info-location BAG_INFO_LOCATIONS]
                      [--datacite-path DATACITE_PATH] [--log-level LOG_LEVEL]
                      [--log-file LOG_FILE]
                      [assets [assets ...]]

positional arguments:
  assets                Assets to be added to the bag.

optional arguments:
  -h, --help            show this help message and exit
  --bag-path BAG_PATH   Path to the Bag directory
  --bag-info-location BAG_INFO_LOCATIONS
                        Locations of the bog-info YAML files
  --datacite-path DATACITE_PATH
                        Path to the DataCite XML file
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### prepare_radar

Creates an empty archive in the [RADAR service](https://www.radar-service.eu) in order to "reserve" a DOI and an ID in RADAR. Both are stored in the CodeMeta file and can be used by the `create_radar` command below to include the DOI for this release in the deposited CodeMeta file. A detailed HowTo for releasing datasets on RADAR is provided in the file [`HOWTO_release_radar.md`](https://git.opencarp.org/openCARP/FACILE-RS/-/blob/master/HOWTO_release_radar.md) in this directory.

```
usage: prepare_radar [-h] [--codemeta-location CODEMETA_LOCATION] [--radar-url RADAR_URL]
                     [--radar-username RADAR_USERNAME] [--radar-password RADAR_PASSWORD]
                     [--radar-client-id RADAR_CLIENT_ID]
                     [--radar-client-secret RADAR_CLIENT_SECRET]
                     [--radar-workspace-id RADAR_WORKSPACE_ID]
                     [--radar-redirect-url RADAR_REDIRECT_URL] [--radar-email RADAR_EMAIL]
                     [--radar-backlink RADAR_BACKLINK] [--dry] [--log-level LOG_LEVEL]
                     [--log-file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --codemeta-location CODEMETA_LOCATION
                        Location of the main codemeta.json JSON file
  --radar-url RADAR_URL
                        URL of the RADAR service.
  --radar-username RADAR_USERNAME
                        Username for the RADAR service.
  --radar-password RADAR_PASSWORD
                        Password for the RADAR service.
  --radar-client-id RADAR_CLIENT_ID
                        Client ID for the RADAR service.
  --radar-client-secret RADAR_CLIENT_SECRET
                        Client secret for the RADAR service.
  --radar-workspace-id RADAR_WORKSPACE_ID
                        Workspace ID for the RADAR service.
  --radar-redirect-url RADAR_REDIRECT_URL
                        Redirect URL for the OAuth workflow of the RADAR service.
  --radar-email RADAR_EMAIL
                        Email for the RADAR metadata.
  --radar-backlink RADAR_BACKLINK
                        Backlink for the RADAR metadata.
  --dry                 Perform a dry run, do not upload anything.
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### create_radar

Creates an archive in the [RADAR service](https://www.radar-service.eu) and uploads the assets provided as positional arguments. The metadata is created similar to `create_datacite`. If the RADAR ID is already in the CodeMeta file, the existing archive is updated instead. A detailed HowTo for releasing datasets on RADAR is provided in the file `HOWTO_release_radar.md` in this directory.

```
usage: create_radar [-h] [--codemeta-location CODEMETA_LOCATION]
                    [--creators-location CREATORS_LOCATIONS]
                    [--contributors-location CONTRIBUTORS_LOCATIONS] [--version VERSION]
                    [--issued ISSUED] [--radar-path RADAR_PATH] [--radar-url RADAR_URL]
                    [--radar-username RADAR_USERNAME] [--radar-password RADAR_PASSWORD]
                    [--radar-client-id RADAR_CLIENT_ID]
                    [--radar-client-secret RADAR_CLIENT_SECRET]
                    [--radar-contract-id RADAR_CONTRACT_ID]
                    [--radar-workspace-id RADAR_WORKSPACE_ID]
                    [--radar-redirect-url RADAR_REDIRECT_URL] [--radar-email RADAR_EMAIL]
                    [--radar-backlink RADAR_BACKLINK] [--dry] [--log-level LOG_LEVEL]
                    [--log-file LOG_FILE]
                    [assets [assets ...]]

positional arguments:
  assets                Assets to be added to the repository.

optional arguments:
  -h, --help            show this help message and exit
  --codemeta-location CODEMETA_LOCATION
                        Location of the main codemeta.json file
  --creators-location CREATORS_LOCATIONS
                        Locations of codemeta JSON files for additional creators
  --contributors-location CONTRIBUTORS_LOCATIONS
                        Locations of codemeta JSON files for additional contributors
  --version VERSION     Version of the resource
  --issued ISSUED       Date for the Issued field and publication year (format: '%Y-%m-%d')
  --radar-path RADAR_PATH
                        Path to the Radar directory, where the assets are collected before
                        upload.
  --radar-url RADAR_URL
                        URL of the RADAR service.
  --radar-username RADAR_USERNAME
                        Username for the RADAR service.
  --radar-password RADAR_PASSWORD
                        Password for the RADAR service.
  --radar-client-id RADAR_CLIENT_ID
                        Client ID for the RADAR service.
  --radar-client-secret RADAR_CLIENT_SECRET
                        Client secret for the RADAR service.
  --radar-contract-id RADAR_CONTRACT_ID
                        Contract ID for the RADAR service.
  --radar-workspace-id RADAR_WORKSPACE_ID
                        Workspace ID for the RADAR service.
  --radar-redirect-url RADAR_REDIRECT_URL
                        Redirect URL for the OAuth workflow of the RADAR service.
  --radar-email RADAR_EMAIL
                        Email for the RADAR metadata.
  --radar-backlink RADAR_BACKLINK
                        Backlink for the RADAR metadata.
  --dry                 Perform a dry run, do not upload anything.
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### run_markdown_pipeline

Copies the content of markdown files in the `PIPELINE_SOURCE` to a Grav CMS repository given by `GRAV_PATH`. The Grav repository is created by the [Git-Sync Plugin](https://getgrav.org/blog/git-sync-plugin).

The pages need to be already existing in Grav and contain a `pipeline` and a `source` field in their frontmatter. The script will find all pages which match the provided `PIPELINE` and will overwrite content part of the page with the markdown file given by `source`. If source is `codemeta.json`, the content will be added to the frontmatter entry `codemeta` rather than overwriting the page content. Twig templates digesting the metadata can be found in the file `Twig_templates.md` in this directory.

After running the script, the changes to the Grav CMS repository can be committed and pushed and the Git-Sync Plugin will update the public pages.

See [openCARP citation info](https://opencarp.org/download/citation) or [code of conduct](https://opencarp.org/community/code-of-conduct) for examples.


```
usage: run_markdown_pipeline [-h] [--grav-path GRAV_PATH] [--pipeline PIPELINE]
                             [--pipeline-source PIPELINE_SOURCE] [--log-level LOG_LEVEL]
                             [--log-file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --grav-path GRAV_PATH
                        Path to the grav repository directory.
  --pipeline PIPELINE   Name of the pipeline as specified in the GRAV metadata.
  --pipeline-source PIPELINE_SOURCE
                        Path to the source directory for the pipeline.
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### run_bibtex_pipeline

Compiles and copies the content of bibtex files in a similar way to `run_markdown_pipeline`. A [CSL](https://citationstyles.org/) can be provided.

Please refer to https://git.opencarp.org/openCARP/publications for an example setup.

```
usage: run_bibtex_pipeline [-h] [--grav-path GRAV_PATH] [--pipeline PIPELINE]
                           [--pipeline-source PIPELINE_SOURCE]
                           [--pipeline-csl PIPELINE_CSL]
                           [--log-level LOG_LEVEL] [--log-file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --grav-path GRAV_PATH
                        Path to the grav repository directory.
  --pipeline PIPELINE   Name of the pipeline as specified in the GRAV
                        metadata.
  --pipeline-source PIPELINE_SOURCE
                        Path to the source directory for the pipeline.
  --pipeline-csl PIPELINE_CSL
                        Path to the source directory for the pipeline.
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```

### run_docstring_pipeline

Extracts and copies the content of [reStructuredText](https://docutils.sourceforge.io/) docstrings of Python scripts. Contrary to the other pipelines, this script does not copy one file to one page in GRAV, but creates a tree of pages below one page (given by the `pipeline` header). it processes all `run.py` and `__init__.py` files.

The `PIPELINE` and `PIPELINE_SOURCE` optiones are used in the same way as in `rum_markdown_pipeline`. In addition, `PIPELINE_IMAGES` specifies a directory where the images from the docstrings are located and `PIPELINE_HEADER` and `PIPELINE_FOOTER` options point to templates which are prepended and appended to each page. With the `PIPELINE_REFS` YML file, you can specifie replacements for the references in the rst code.

Please refer to https://git.opencarp.org/openCARP/experiments for an example setup.

```
usage: run_docstring_pipeline [-h] [--grav-path GRAV_PATH]
                              [--pipeline PIPELINE]
                              [--pipeline-source PIPELINE_SOURCE]
                              [--pipeline-images PIPELINE_IMAGES]
                              [--pipeline-header PIPELINE_HEADER]
                              [--pipeline-footer PIPELINE_FOOTER]
                              [--pipeline-refs PIPELINE_REFS]
                              [--log-level LOG_LEVEL] [--log-file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --grav-path GRAV_PATH
                        Path to the grav repository directory.
  --pipeline PIPELINE   Name of the pipeline as specified in the GRAV
                        metadata.
  --pipeline-source PIPELINE_SOURCE
                        Path to the source directory for the pipeline.
  --pipeline-images PIPELINE_IMAGES
                        Path to the images directory for the pipeline.
  --pipeline-header PIPELINE_HEADER
                        Path to the header template.
  --pipeline-footer PIPELINE_FOOTER
                        Path to the footer template.
  --pipeline-refs PIPELINE_REFS
                        Path to the refs yaml file.
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
```
