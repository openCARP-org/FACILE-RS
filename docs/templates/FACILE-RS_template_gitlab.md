# FACILE-RS template for GitLab CI/CD

The [FACILE-RS template](https://git.opencarp.org/openCARP/facile-rs-template) allows you to integrate automated FACILE-RS workflows to a GitLab repository.

## Description of the workflow

### Default workflow

On simple commits, this pipeline will by default:
- generate a DataCite metadata file in XML format and export it as an artifact.
- generate a CFF (Citation File Format) file and export it as an artifact. See `.gitlab/ci/facile-rs/cff.gitlab-ci.yml` if you also want to push the file to the repository.

### Release workflow

You can trigger a release by creating a pre-release tag on GitLab: this tag must start with `pre-v`.

The pre-release pipeline will then:
- update the CodeMeta file with the version identifier (what is after "pre-" in the tag name) and the current date
- create or update the CFF file
- create the release tag starting with `v`, which will trigger the release pipeline

The release pipeline triggered by the creation of this tag will then:
- create a GitLab release integrating the DataCite metadata file
- create a BagPack bag and upload it to the GitLab registry

### Optional workflows

You can optionally trigger releases on RADAR or Zenodo by turning `ENABLE_ZENODO` or `ENABLE_RADAR` to "true" in `.gitlab/ci/facile-rs/.gitlab-ci.yml`.
See the [dedicated section](#optional-release-workflows) for more information about the configuration of these workflows.

## Get started

In this section, you will modify the content of your GitLab repository. We advise you to create a new branch before proceeding further, so that you don't modify the content of your default branch:
```
git checkout -b facile-rs-integration
```

### Merge the template into your repository

To get started, merge the files in this repository into your own project.
You can do it manually, or using git:
```
git remote add facile-rs-template https://git.opencarp.org/openCARP/facile-rs-template.git
git fetch facile-rs-template --tags
# This merges the current main branch of the FACILE-RS template.
# You can also merge a tag corresponding to a specific FACILE-RS version.
git merge --allow-unrelated-histories facile-rs-template/main
git remote remove facile-rs-template
```

If you already have a `.gitlab-ci.yml` file in your repository, you will get conflicts when trying to merge the repository:
```
Auto-merging .gitlab-ci.yml
CONFLICT (add/add): Merge conflict in .gitlab-ci.yml
Automatic merge failed; fix conflicts and then commit the result.
```
To fix this, open `.gitlab-ci.yml` and fix the conflict manually by removing the conflict markers (`<<<<<<< HEAD ...`, `=======` and `>>>>>>>`), keeping both your version of the file and the content added from the FACILE-RS template.

### Configure the template

Open `.gitlab/ci/facile-rs/.gitlab-ci.yml` and configure at least:
- PROJECT_NAME: the name of your project
- CODEMETA_LOCATION: the location of your CodeMeta metadata file (`codemeta.json` by default)
- CFF_PATH: the location of the CFF file to create or update (`CITATION.cff` by default)
- RELEASE_BRANCH: the branch from which you will create releases (`$CI_DEFAULT_BRANCH` by default, the default branch of your repository)

### Run your first pipeline

Ensure you have Docker runners available on your GitLab instance, and push the changes.
A GitLab CI/CD pipeline should have been triggered and can be seen from your GitLab project in Build > Pipelines.

### Configure your GitLab project for the release workflow

If you want your pipeline to be able to update your repository metadata and trigger releases, you should additionally:
- Create a Project Access Token. Go to your project on GitLab and then in Settings -> Access Tokens, choose the name of your token, expiration date (can be removed), role as a Maintainer and Scopes as `api` and `write_repository`. After the token has been created, copy its value and keep it for later.
- Go to Settings -> CI/CD -> Variables and choose Add Variable. As a key write `PRIVATE_TOKEN` and as value paste the copied token. This variable should be made "masked" (so that it is not displayed) and "protected" (which means that it is only usable on protected branches and tags).
- Make release tags protected (otherwise, `PRIVATE_TOKEN` can not be used when creating releases): go to Settings > Repository > Protected tags. Click on Add tag and protect the tags matching wildcard `pre-v*`. Then add a new tag and protect the tags matching `v*`.
- If you will create releases from another branch than your default branch, you also need to protect this branch: go to Settings > Repository > Protected branches and protect the branch from which you will create the releases.

**Note:** protecting the PRIVATE_TOKEN variable, branches and tags is important in order to avoid that any developer can use the token which has write permissions on the whole repository. It also avoids that releases are triggered from a feature branch.

### Trigger a software release

To trigger a software release, go to your project on GitLab, then to Code > Tags. Create a new tag with a name starting with `pre-v`, for example `pre-v0.0.1`. Create it from the protected branch in which you've integrated the FACILE-RS template.

The pre-release workflow should then be triggered, followed by the release workflow. GitLab CI/CD Pipelines can be checked in Build > Pipelines.

### Troubleshooting

#### “This job is stuck because you don’t have any active runners online with any of these tags assigned to them: docker”

By default, if this is not overwritten, the tag `docker` is assigned to all FACILE-RS jobs. If this tag is not available in your instance, you can remove or replace the following lines in `.gitlab/ci/facile-rs/.gitlab-ci.yml`:
```
default:
  tags:
    - docker
```

### Optional release workflows

You can optionally trigger releases on RADAR or Zenodo by turning `ENABLE_ZENODO` or `ENABLE_RADAR` to "true" in `.gitlab/ci/facile-rs/.gitlab-ci.yml`.

#### Enable releases on Zenodo

When the Zenodo workflow is enabled, the software releases created by the release workflows will also be uploaded to Zenodo.
Once a release has been uploaded, you can log in to Zenodo and review it before it is published.

In order to upload releases on Zenodo when triggering the release workflow, you have to enable the Zenodo workflow in the template and to register a Zenodo Personal access token in GitLab:
- Set the variable `ENABLE_ZENODO` to "true" in `.gitlab/ci/facile-rs/.gitlab-ci.yml`.
- Set the `ZENODO_URL` to https://sandbox.zenodo.org for uploading releases on the Zenodo test environment, or to https://zenodo.org to upload releases on Zenodo.
- Create a Personal access token on Zenodo: open the `ZENODO_URL` in a web browser, log in, go to the Applications settings and create a new personal access token with scope "deposit:write". Copy the token and save it for the next step.
- In your GitLab project, go to Settings -> CI/CD -> Variables, and add a new variable. Set the key as `ZENODO_TOKEN` and as a value paste the token created in the previous step. Make it "Masked" and check the box "Protect variable".

You can now trigger a new release in your release branch by pushing a pre-release tag:
```
git tag pre-v0.0.2
git push origin pre-v0.0.2
```

A GitLab release of your software will be created, and in addition, the release will be associated with a DOI and uploaded to Zenodo.
Once the workflow has run, you can log in to Zenodo to review and publish your software release.

#### Enable releases on RADAR

In order to use the RADAR workflow, you have to possess publication credentials on a [RADAR](https://www.radar-service.eu/) instance.
When the RADAR workflow is enabled, the software releases created by the release workflows will also be uploaded to RADAR.
Once a release has been uploaded, you can log in to RADAR and review it before it is published.

In order to use the RADAR release workflow, you have to enable the workflow and to register some RADAR secrets in GitLab:
- Set the variable `ENABLE_RADAR` to "true" in `.gitlab/ci/facile-rs/.gitlab-ci.yml`.
- In your GitLab project, go to Settings -> CI/CD -> Variables, and add the following variables (ensure to check the box "Protect variable" and to make them "Masked"):
  * `RADAR_REDIRECT_URL` with the value being a link to a web page of your project or repository
  * `RADAR_EMAIL` with the value being the email address of the data steward for this dataset
  * `RADAR_WORKSPACE_ID` with the value being the ID of your RADAR workspace (see the URL to your workspace with the . followed by the name of your workspace)
  * `RADAR_URL` with the value being the URL to your RADAR instance (talk to your RADAR admin)
  * `RADAR_CLIENT_ID` with the value being your RADAR API client ID (talk to your RADAR admin)
  * `RADAR_CLIENT_SECRET` with the value being your RADAR API secret (talk to your RADAR admin)
  * `RADAR_USERNAME` with the value being your RADAR API user name (talk to your RADAR admin)
  * `RADAR_PASSWORD` with the value being your RADAR API password (talk to your RADAR admin)

You can now trigger a new release in your release branch by pushing a pre-release tag:
```
git tag pre-v0.0.2
git push origin pre-v0.0.2
```

A GitLab release of your software will be created, and in addition, the release will be associated with a DOI and uploaded to RADAR.
Once the workflow has run, you can log in to your RADAR instance to review and publish your software release.

