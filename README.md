# FACILE-RS

This package (previously known as openCARP-CI) contains a set of Python scripts which can be used to perform tasks around the archival and long term preservation of software repositories. In particular, it can be used to:

* create a release in GitLab using the GitLab API,
* create a DataCite record based on CodeMeta files present in repositories,
* create a CFF (Citation File Format) file from CodeMeta files,
* create archive packages in the [BagIt](https://tools.ietf.org/html/rfc8493) or [BagPack](https://www.rd-alliance.org/system/files/Research%20Data%20Repository%20Interoperability%20WG%20-%20Final%20Recommendations_reviewed_0.pdf) formats.
* archive the software using the [RADAR service](https://www.radar-service.eu),
* archive the software on [Zenodo](https://zenodo.org),
* use content from markdown files, bibtex files, or python docstrings to create web pages in a [Grav CMS](https://getgrav.org/).

The scripts were created for the [openCARP](https://opencarp.org) simulation software, but can be adopted for arbitrary projects. While they can be used on the command line, the scripts are mainly used within the GitLab CI to run automatically on each push to a repository, or when a tag is created.

An example of integration in a CI environment is provided in the [tutorials](https://facile-rs.readthedocs.io/en/latest/tutorials/). An example of a more complex setup are the [openCARP CI file](https://git.opencarp.org/openCARP/openCARP/-/blob/master/.gitlab-ci.yml) and the [included subscripts](https://git.opencarp.org/openCARP/openCARP/-/tree/master/.gitlab/ci).


## Setup

### Prerequisites

In order to generate metadata or publish software releases using FACILE-RS, it is necessary to create a CodeMeta metadata file for the software (for example using the [CodeMeta generator](https://codemeta.github.io/codemeta-generator/)).

In addition, if you want to use our preconfigured automated pipelines, your software repository needs to be hosted on a GitLab instance with [Docker runners](https://docs.gitlab.com/runner/) available.

It is technically possible to automate the FACILE-RS workflows on other platforms (for example using GitHub actions), but such examples have not been implemented yet.

### Installation

FACILE-RS can be installed using pip:
```
pip install FACILE-RS
```

In order to use FACILE-RS from the command-line, we recommend to install the package in a [virtual environment](https://docs.python.org/3/library/venv.html):

```bash
python -m venv env
source env/bin/activate
pip install FACILE-RS
```

### Use FACILE-RS within GitLab CI/CD

In order to integrate automated FACILE-RS workflows into your GitLab project, you can use the FACILE-RS template ([source](https://git.opencarp.org/openCARP/facile-rs-template), [documentation](https://facile-rs.readthedocs.io/en/latest/facile-rs_template.html)), which provides a sample GitLab CI/CD configuration for generating metadata and creating software releases with FACILE-RS.

## Documentation

[![Documentation Status](https://readthedocs.org/projects/facile-rs/badge/?version=latest)](https://facile-rs.readthedocs.io/en/latest/?badge=latest)

FACILE-RS documentation is available at [https://facile-rs.readthedocs.io/](https://facile-rs.readthedocs.io/).

It can also be generated using Sphinx from [docs/sphinxdocs](https://git.opencarp.org/openCARP/FACILE-RS/-/tree/master/docs/sphinxdocs?ref_type=heads) by running:
```
pip install -r requirements.txt
make html
```
The Python packages in [docs/sphinxdocs/requirements.txt](https://git.opencarp.org/openCARP/FACILE-RS/-/blob/master/docs/sphinxdocs/requirements.txt?ref_type=heads) as well as FACILE-RS itself must be installed in order to generate the documentation.

## Usage

The FACILE-RS tools are available via the command `facile-rs`.
More details about its usage are available in the [documentation](https://facile-rs.readthedocs.io/en/latest/apidocs/facile_rs/facile_rs.facile_rs.html) or by running `facile-rs --help`.

`facile-rs` expects a number of command line arguments. Default values can be set using environment variables (using upper case and underscores), i.e. the following lines do the same:

```bash
facile-rs bag create --bag-path=/path/to/bag
BAG_PATH=/path/to/bag facile-rs bag create
```

Environments variables can be set in the usual way, e.g. the `.gitlab-ci.yml` file, but also in a `.env` file in the directory where the script is invoked.

FACILE-RS comprises the following tools:

### `facile-rs cff create`

Creates a [Citation File Format](https://citation-file-format.github.io) (CFF) file from a CodeMeta file.
An example output can be found [here](https://git.opencarp.org/openCARP/openCARP/-/blob/master/CITATION.cff).

Deprecated alias: `create_cff`

### `facile-rs datacite create`

Creates a DataCite XML file following the [DataCite Metadata Schema 4.3](https://schema.datacite.org/meta/kernel-4.3/). The information needed for this can be taken from (a list) of locations given as URL or local file path. `CODEMETA_LOCATION` must point to a [codemeta.json](https://codemeta.github.io) file. `CREATORS_LOCATIONS` and `CONTRIBUTORS_LOCATIONS` point to similar files which contain a list of `creators` or `contributors`, respectively.

For an example, see [here](https://git.opencarp.org/openCARP/openCARP/blob/master/codemeta.json).

Deprecated alias: `create_datacite`

### `facile-rs bag create`

Creates a bag [BagIt](https://tools.ietf.org/html/rfc8493) using the [bagit-python](https://github.com/LibraryOfCongress/bagit-python) package. The assets to be included in the bag are given as positional arguments.

Deprecated alias: `create_bag`

### `facile-rs bagpack create`

Creates a bag [BagIt](https://tools.ietf.org/html/rfc8493) similar to `create_bag.py`, but also includes a DataCite XML file as recommended by the [RDA Research Data Repository Interoperability WG](https://www.rd-alliance.org/system/files/Research%20Data%20Repository%20Interoperability%20WG%20-%20Final%20Recommendations_reviewed_0.pdf).

Deprecated alias: `create_bagpack`

### `facile-rs release prepare`

Updates the CodeMeta file for the given `VERSION` and `DATE` (as `dateModified`, current date if omitted). Useful to automatically get the version from a git tag and inject it into the repo's metadata file.

Deprecated alias: `prepare_release`

### `facile-rs gitlab publish`

Creates a release in GitLab using the GitLab API. A tag for the release needs to be created before and provided to the script.
An example output can be found [here](https://git.opencarp.org/openCARP/openCARP/-/releases).

Deprecated alias: `create_release`

### `facile-rs radar prepare`

Creates an empty archive in the [RADAR service](https://www.radar-service.eu) in order to "reserve" a DOI and an ID in RADAR. Both are stored in the CodeMeta file and can be used by the `create_radar` command below to include the DOI for this release in the deposited CodeMeta file. A detailed HowTo for releasing datasets on RADAR is provided in the file [`HOWTO_release_radar.md`](https://git.opencarp.org/openCARP/FACILE-RS/-/blob/master/HOWTO_release_radar.md) in this directory.

Deprecated alias: `prepare_radar`

### `facile-rs radar upload`

Creates an archive in the [RADAR service](https://www.radar-service.eu) and uploads the assets provided as positional arguments. The metadata is created similar to `create_datacite`. If the RADAR ID is already in the CodeMeta file, the existing archive is updated instead. A detailed HowTo for releasing datasets on RADAR is provided in the file `HOWTO_release_radar.md` in this directory.

Deprecated alias: `create_radar`

### `facile-rs zenodo prepare`

Creates an empty archive on [Zenodo](https://zenodo.org) in order to "reserve" a DOI and an ID in Zenodo. Both are stored in the CodeMeta file and can be used by the `create_zenodo` command below to include the DOI for this release in the deposited CodeMeta file. A detailed HowTo for releasing datasets on Zenodo is provided in the tutorial [`04_release_zenodo.md`](./docs/tutorials/04_release_zenodo.md).

Deprecated alias: `prepare_zenodo`

### `facile-rs zenodo upload`

Creates an archive on [Zenodo](https://zenodo.org) and uploads the assets provided as positional arguments. The metadata is created similar to `create_datacite`. If the Zenodo ID is already in the CodeMeta file, the existing archive is updated instead. A detailed HowTo for releasing datasets on Zenodo is provided in the tutorial [`04_release_zenodo.md`](./docs/tutorials/04_release_zenodo.md).

Deprecated alias: `create_zenodo`

### `facile-rs grav bibtex`

Compiles and copies the content of bibtex files in a similar way to `run_markdown_pipeline`. A [CSL](https://citationstyles.org/) can be provided.

Please refer to https://git.opencarp.org/openCARP/publications for an example setup.

Deprecated alias: `run_bibtex_pipeline`

### `facile-rs grav docstring`

Extracts and copies the content of [reStructuredText](https://docutils.sourceforge.io/) docstrings of Python scripts. Contrary to the other pipelines, this script does not copy one file to one page in GRAV, but creates a tree of pages below one page (given by the `pipeline` header). it processes all `run.py` and `__init__.py` files.

The `PIPELINE` and `PIPELINE_SOURCE` options are used in the same way as in `rum_markdown_pipeline`. In addition, `PIPELINE_IMAGES` specifies a directory where the images from the docstrings are located and `PIPELINE_HEADER` and `PIPELINE_FOOTER` options point to templates which are prepended and appended to each page. With the `PIPELINE_REFS` YML file, you can specifie replacements for the references in the rst code.

Please refer to https://git.opencarp.org/openCARP/experiments for an example setup.

Deprecated alias: `run_docstring_pipeline`

### `facile-rs grav markdown`

Copies the content of markdown files in the `PIPELINE_SOURCE` to a Grav CMS repository given by `GRAV_PATH`. The Grav repository is created by the [Git-Sync Plugin](https://getgrav.org/blog/git-sync-plugin).

The pages need to be already existing in Grav and contain a `pipeline` and a `source` field in their frontmatter. The script will find all pages which match the provided `PIPELINE` and will overwrite content part of the page with the markdown file given by `source`. If source is `codemeta.json`, the content will be added to the frontmatter entry `codemeta` rather than overwriting the page content. Twig templates digesting the metadata can be found in the file `Twig_templates.md` in this directory.

After running the script, the changes to the Grav CMS repository can be committed and pushed and the Git-Sync Plugin will update the public pages.

See [openCARP citation info](https://opencarp.org/download/citation) or [code of conduct](https://opencarp.org/community/code-of-conduct) for examples.

Deprecated alias: `run_markdown_pipeline`
