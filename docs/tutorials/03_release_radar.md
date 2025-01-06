# How to set up FACILE-RS for a two-step release process and archival on RADAR

## Overview
This HowTo will guide you through
 * setting up the GitLab CI environment for your project
 * establishing a release process based on pre-release tags
 * archiving your release on a RADAR repository

## Prepare your codemeta file
You'll need your metadata prepared in a [codemeta.json](https://codemeta.github.io/create/) file. If you used [KIT's cookiecutter template](https://git.scc.kit.edu/ak-open-source-software/cookiecutter-kittemplate), you should be good to go already.


## GitLab Continuous Integration environment
1. You need access to a GitLab Runner that can run Docker containers. If your project is hosted on [the Helmholtz Codebase GitLab instance](https://codebase.helmholtz.cloud/), you will have access to a suitable shared runner. If your project is hosted on GitLab.com, you have access to free runners for a certain amount of minutes per month. If not, see [the GitLab docs](https://docs.gitlab.com/runner/install/) for general information on how to set up your own GitLab runner.
In general, FACILE-RS should also be compatible with GitHub Actions. We did not test this yet. If you got it running, a merge request extending this documentation would be highly appreciated.

2. In your GitLab project, go to `Settings` -> `Access Tokens` and create a token with name `release`, role `Maintainer`, scopes `api` and `write_repository`. Copy this token to a safe place, we'll need it in the next step.
3. In your GitLab project, go to `Settings` -> `CI/CD`. Create the following variables which you can all [protect and mask](https://docs.gitlab.com/ee/ci/variables/#add-a-cicd-variable-to-a-project) to keep them safe:
  * `PRIVATE_TOKEN` with the value being the token created in step 2: this variable name will be recognized and used in the script `create_release`, and the token will be used to push changes to the repository.
  * `RADAR_BACKLINK` with the value being a link to a web page of your project's releases, e.g. `https://git.opencarp.org/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}/-/releases`
  * `RADAR_REDIRECT_URL` with the value being a link to a web page of your project or repository, e.g. `https://git.opencarp.org/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}/`
  * `RADAR_EMAIL` with the value being the mail address of the data steward for this dataset
  * `RADAR_WORKSPACE_ID` with the value being the ID of your RADAR workspace (see the URL to your workspace with the . followed by the name of your workspace)
  * `RADAR_URL` with the value being the URL to your RADAR instance (talk to your RADAR admin)
  * `RADAR_CLIENT_ID` with the value being your RADAR API client ID (talk to your RADAR admin)
  * `RADAR_CLIENT_SECRET` with the value being your RADAR API secret (talk to your RADAR admin)
  * `RADAR_USERNAME` with the value being your RADAR API user name (talk to your RADAR admin)
  * `RADAR_PASSWORD` with the value being your RADAR API password (talk to your RADAR admin)
  * If your project is private, you should in addition set the (masked and protected) variable `ASSETS_TOKEN` with the same value as `PRIVATE_TOKEN`: this token will be used by `facile-rs radar upload` to fetch the source code from the repository.

4. Protect the tags triggering the release process so that they can access the protected variables.
Go to `Settings` -> `Repository` -> `Protected tags` and add the following entries:
  * Tag: `pre-v*`, Allowed to create: `Maintainers`
  * Tag: `v*`, Allowed to create: `Maintainers`

5. Create the CI configuration in the `.gitlab-ci.yml` file in your repository.
You can find a minimum template for a two-stage release process below. There are a number of variables that should/can be adapted:
  * `PROJECT_NAME` where you replace `openCARP` with for example the name of your software
  * `RELEASE_DESCRIPTION` where you adapt the search term and can add as many additional release info as desired, see for example [here](https://git.opencarp.org/openCARP/openCARP/-/releases)
  * `CREATORS_LOCATIONS` and `CONTRIBUTORS_LOCATIONS` (the latter being data curators) with paths or links to raw codemeta.json files. They can also be lists of those links (starting with `|` and then one link per line) or empty.
  * If you want to inform the data steward about the new release ready to be published, set the following variables:
    * `NOTIFICATION_EMAIL: abc@host.com` address of the data steward (can be the same as `RADAR_EMAIL`)
    * `SMTP_SERVER: your.smtpserver.com` (a SMTP server not requiring authentication, e.g. `smarthost.kit.edu`)
  * Commented content in the code below can be uncommented in order to include all submodules in the archived release. If your repository doesn't include submodules, this content can be removed.
  * You can add further artifacts to be included in the archive by simply adding additional arguments to the `create_release` call in the the `release-create` pipeline.

```
stages:
- build
- release
- archive

variables:
  PROJECT_NAME: openCARP
  RADAR_PATH: ${PROJECT_NAME}-${CI_COMMIT_TAG}
  RADAR_BACKLINK: ${CI_PROJECT_URL}/-/releases
  SMTP_SERVER: smarthost.kit.edu
  NOTIFICATION_EMAIL: info@openCARP.org
  RELEASE_TAG: ${CI_COMMIT_TAG}
  RELEASE_API_URL: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/releases
  RELEASE_ARCHIVE_URL: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/repository/archive.tar.gz?sha=${CI_COMMIT_TAG}
  RELEASE_DESCRIPTION: |
    Find the archived version of the release in the [RADAR4KIT repository](https://radar.kit.edu/radar/en/search?query=${PROJECT_NAME}+%28${CI_COMMIT_TAG}%29&searchBy=metadata).
  CREATORS_LOCATIONS: ${CI_PROJECT_URL}/raw/master/codemeta.json
  CONTRIBUTORS_LOCATIONS: https://git.opencarp.org/openCARP/openCARP-CDE/raw/master/codemeta.json
  CODEMETA_LOCATION: codemeta.json
  CFF_PATH: CITATION.cff
  DATACITE_PATH: ${PROJECT_NAME}.xml
  DATACITE_RELEASE: ${PROJECT_NAME}-${CI_COMMIT_TAG}.xml
  DATACITE_REGISTRY_URL: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/generic/${PROJECT_NAME}-datacite/${CI_COMMIT_TAG}
  GIT_SUBMODULE_STRATEGY: recursive
  DOCKER_DRIVER: overlay
  GIT_STRATEGY: clone
  GIT_DEPTH: 1
  # # Optional: for source code including submodules
  # INCLSUBMODULES_REGISTRY_URL: ${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/generic/${PROJECT_NAME}-inclSubmodules/${CI_COMMIT_TAG}
  # INCLSUBMODULES_RELEASE: ${PROJECT_NAME}-${CI_COMMIT_TAG}-inclSubmodules.zip

build-datacite:
  stage: build
  image: python:3.9
  before_script:
  - pip install FACILE-RS
  script:
  - facile-rs datacite create
  artifacts:
    paths:
    - $DATACITE_PATH
    expire_in: 2 hrs

release-datacite:
  variables:
    GIT_STRATEGY: none
  stage: release
  image: curlimages/curl:7.77.0
  needs:
  - build-datacite
  rules:
  - if: $CI_COMMIT_TAG =~ /^v/
  script:
  - mv $DATACITE_PATH $DATACITE_RELEASE
  - |
    curl --header "JOB-TOKEN: ${CI_JOB_TOKEN}" --upload-file ${DATACITE_RELEASE} ${DATACITE_REGISTRY_URL}/${DATACITE_RELEASE}

# # Optional job, for releasing source code including submodules
# release-submodule:
#  variables:
#    GIT_STRATEGY: none
#  stage: release
#  image: mrnonz/alpine-git-curl:alpine3.12
#  rules:
#  - if: $CI_COMMIT_TAG =~ /^v/
#  script:
#  - git clone --branch ${CI_COMMIT_TAG} --depth 1 --recurse-submodules ${CI_PROJECT_URL}.git
#  - rm -rf ${CI_PROJECT_NAME}/.git/
#  - tar czf ${INCLSUBMODULES_RELEASE} ${CI_PROJECT_NAME}
#  - |
#    curl --header "JOB-TOKEN: ${CI_JOB_TOKEN}" --upload-file ${INCLSUBMODULES_RELEASE} ${INCLSUBMODULES_REGISTRY_URL}/${INCLSUBMODULES_RELEASE}

release-create:
  stage: release
  image: python:3.9
  rules:
  - if: $CI_COMMIT_TAG =~ /^v/
  before_script:
  - git config --global user.name "${GITLAB_USER_NAME}"
  - git config --global user.email "${GITLAB_USER_EMAIL}"
  - pip install FACILE-RS
  script:
  - >
    facile-rs gitlab publish
    ${DATACITE_REGISTRY_URL}/${DATACITE_RELEASE}
  #  ${INCLSUBMODULES_REGISTRY_URL}/${INCLSUBMODULES_RELEASE}

prepare-release:
  image: python:3.9
  stage: release
  rules:
  - if: $CI_COMMIT_TAG =~ /^pre/
  before_script:
  - pip install FACILE-RS
  - git config --global user.name "${GITLAB_USER_NAME}"
  - git config --global user.email "${GITLAB_USER_EMAIL}"
  script:
  - VERSION=`echo $CI_COMMIT_TAG | grep -oP '^pre-\K.*$'`
  - echo "Preparing release of $VERSION"
  - facile-rs release prepare
  - facile-rs radar prepare
  - facile-rs cff create
  - git add ${CODEMETA_LOCATION} ${CFF_PATH}
  - git commit -m "Release ${VERSION}"
  - git push "https://PUSH_TOKEN:${PRIVATE_TOKEN}@${CI_REPOSITORY_URL#*@}" "HEAD:${CI_DEFAULT_BRANCH}"
  - git tag $VERSION
  - git push "https://PUSH_TOKEN:${PRIVATE_TOKEN}@${CI_REPOSITORY_URL#*@}" --tags

archive-radar:
  stage: archive
  image: python:3.9
  rules:
  - if: $CI_COMMIT_TAG =~ /^v/
  before_script:
  - pip install FACILE-RS
  script:
  - >
    facile-rs radar upload --no-sort-authors
    $RELEASE_ARCHIVE_URL
  #  ${INCLSUBMODULES_REGISTRY_URL}/${INCLSUBMODULES_RELEASE}
```

## Test your pipeline
Just make a change to the repository with GitLab's WebIDE or push a local commit to the server.

## Tag a release

To initiate the two-stage release process, add a tag `pre-vX.Y` where `X.Y` is  your desired version number. This can either be done in GitLab via `Repository` -> `Tags` or on the commandline:
```
git tag -a pre-vX.Y
git push origin pre-vX.Y
```

Then, the prepare-release pipeline will run and
* reserve a DOI for your release
* update your `codemeta.json` with the new version, its date and DOI
* create the tag `vX.Y`
* not delete the tag `pre-vX.Y` as protected tags can only be deleted from the web interface
* upload your dataset to RADAR
* notify the data steward by email that the release is ready to be published on RADAR
