# FACILE-RS template for GitHub Actions
The [FACILE-RS GitHub template](https://github.com/openCARP-org/FACILE-RS-template) allows you to integrate automated FACILE-RS workflows to a repository hosted on GitHub.

## Description of the workflow

### Default workflow

On simple commits, this pipeline will by default:
- generate a DataCite metadata file in XML format and export it as an artifact.
- generate a CFF (Citation File Format) file and export it as an artifact. See `.github/github.env` if you also want to push the file to the repository.

### Release workflow

You can trigger a release by creating a pre-release tag on GitHub: this tag must start with `pre-v`.

The pre-release pipeline will then:
- update the CodeMeta file with the version identifier (what is after "pre-" in the tag name) and the current date
- create or update the CFF file in the repository
- create the release tag starting with `v`, which will trigger the release pipeline

The release pipeline triggered by the creation of this tag will then:
- create a GitHub release integrating the DataCite metadata file

### Optional workflows

You can optionally trigger releases on RADAR or Zenodo by turning `ENABLE_ZENODO` or `ENABLE_RADAR` to `true` in `.github/github.env`.
See the section [Optional release workflows](#optional-release-workflows) for more information about the configuration of these workflows.

## Get started

In this section, you will modify the content of your GitHub repository. We advise you to create a new branch before proceeding further, so that you don't modify the content of your default branch directly:
```
git checkout -b facile-rs-integration
```

### Merge the template into your repository

To get started, merge the files from the [template repository](https://github.com/openCARP-org/FACILE-RS-template) into your own project.
You can copy the files from the template in your project manually, or use the following git commands inside your local git repository:
```
git remote add facile-rs-template https://github.com/openCARP-org/FACILE-RS-template.git
git fetch facile-rs-template --tags
# This merges the current main branch of the FACILE-RS template.
# You can also merge a tag corresponding to a specific FACILE-RS version.
git merge --allow-unrelated-histories facile-rs-template/main
git remote remove facile-rs-template
```

### Add a CodeMeta file to your repository

In order to use FACILE-RS, you have to add a CodeMeta metadata file to your repository.

You can for example generate a file `codemeta.json` using the [CodeMeta generator](https://codemeta.github.io/codemeta-generator/) and include in the root directory of your repository.

### Configure the template

Open `.github/github.env` and configure at least:
- PROJECT_NAME: the name of your project
- CODEMETA_LOCATION: the location of your CodeMeta metadata file (`codemeta.json` by default)
- CFF_PATH: the location of the CFF file to create or update (`CITATION.cff` by default)
- RELEASE_BRANCH: the branch from which you will create releases (By default, it will be the default branch of your repository)

*Note :* In particular, if you have switched to a new branch `facile-rs-integration` as advised in the [Get started](#get-started) section, and want to test the release workflow from this branch, you should set `RELEASE_BRANCH` accordingly.

### Run your first pipeline

Push the changes to GitHub: a workflow should have been triggered on GitHub, and can be seen from your GitHub repository in the `Actions` section.

### Configure your GitHub project for the release workflow

If you want your pipeline to be able to update your repository metadata and trigger releases, some additional configuration has to be done on GitHub.

In the next sections, we present two different configuration options: the first option sets up a configuration where only maintainers and/or owners will be able to push to the release branch and create release tags.

The second option introduces a simpler setup that doesn't implement any protection against write permissions, which means that any collaborator will be able to push to any branch and to trigger releases. This option is typically only suitable for a repo where all collaborators have full permissions.

#### Option 1: protect release branch and tags (recommended)

With this configuration, we will restrict the creation and modification of release branch and tags, as well as the access to the secrets used in FACILE-RS workflows to the repository maintainers.

- Allow GitHub Actions to write to your repository: from your GitHub project, go to Settings > Actions > General, and in the section "Workflow permissions", select "Read and write permissions".
- Protect your release branch with a ruleset: go to Settings > Rules > Rulesets > New Ruleset > New branch ruleset.
  - Choose a name, for example "Release branch".
  - Set enforcement status to "Active".
  - In the Bypass list, add "Deploy keys", "Repository admin" and "Maintain".
  - In Target branches, add the branch you use for release (typically the default branch of your repository, or the value of `RELEASE_BRANCH`).
  - Mark the following branch rules: Restrict creations, Restrict update, Restrict deletions, Block force pushes.
- Protect your release tags with a ruleset: go to Settings > Rules > Rulesets > New Ruleset > New tag ruleset.
  - Choose a name, for example "Release tags".
  - Set enforcement status to "Active".
  - In the Bypass list, add "Deploy keys", "Repository admin" and "Maintain".
  - In Target tags, click on Add target > Include by pattern and add the pattern `v*`. Then do the same for the pattern `pre-v*`.
  - Mark the following tag rules: Restrict creations, Restrict update, Restrict deletions, Block force pushes.
- Create an environment for FACILE-RS secrets:
  - go to Settings > Environments > New environment, and create an environment named `facile-rs`. 
  - In "Deployment branch and tags", select "Selected branches and tags" and click on "Add deployment branch or tag rule" to add your release branch (for example `main`) and the release tags patterns (`pre-v*` and `v*`)
  - Note: you can add secrets needed by FACILE-RS inside this environment to make them only accessible via the release branch and tags (for example: ZENODO_TOKEN, RADAR_PASSWORD, ...).
- Create a Deploy key, which will allow GitHub Actions to trigger release workflows:
  - Generate a SSH key pair, for example using the command `ssh-keygen -t ed25519 -f id_ed25519 -N "" -q -C ""` in a Unix shell. This command will generate two files in the current directory: a private key named `id_ed25519` and a public key `id_ed25519.pub`. Be sure never to expose the private key publicly!
  - Register the private key as a new secret in your `facile-rs` environment: go to Settings > Environments > facile-rs and click on "Add environment secret". Give it the name `PRIVATE_KEY` and as the value, paste the content of the file `ed_25519`.
  - Register the public key as a Deploy key in your GitHub repository: go to Settings > Deploy keys and click on "Add deploy key". Choose a title for your deploy key and as a value, paste the content of the file `ed_25519.pub`. Check the box "Allow write access".
  - You can now delete the files `ed_25519` and `ed_25519.pub`.

#### Option 2: define permissions at the repository level

This option should be used cautiously, as it doesn't implement any protection mechanisms about who can trigger releases and from which branch.

- Allow GitHub Actions to write to your repository: from your GitHub project, go to Settings > Actions > General, and in the section "Workflow permissions", select "Read and write permissions".
- Create a Deploy key, which will allow GitHub Actions to trigger release workflows:
  - Generate a SSH key pair, for example using the command `ssh-keygen -t ed25519 -f id_ed25519 -N "" -q -C ""` in a Unix shell. This command will generate two files in the current directory: a private key named `id_ed25519` and a public key `id_ed25519.pub`. Be sure never to expose the private key publicly!
  - Register the private key as a new secret in your repository: go to Settings > Secrets and variables > Actions and click on "New repository secret". Give it the name `PRIVATE_KEY` and as the value, paste the content of the file `ed_25519`.
  - Register the public key as a Deploy key in your GitHub repository: go to Settings > Deploy keys and click on "Add deploy key". Choose a title for your deploy key and as a value, paste the content of the file `ed_25519.pub`. Check the box "Allow write access".
  - You can now delete the files `ed_25519` and `ed_25519.pub`.

### Trigger a software release

After having configured your deploy key, you can trigger a software release: create and push a new pre-release tag on GitHub, starting with `pre-v`, for example `pre-v0.0.1`.

To do so from a terminal, go to your git repository, ensure your are on the branch you have defined as the release branch, and run the following commands:
```
git tag pre-v0.0.1
git push origin pre-v0.0.1
```

The pre-release workflow should then be triggered, followed by the release workflow, which will create a GitHub release of your software. Workflows can be checked in the "Actions" tab. Releases are available in the "Code" tab, on the right side.

### Optional release workflows

#### Enable releases on Zenodo

When the Zenodo workflow is enabled, the software releases created by the release workflows will also be uploaded to Zenodo.
Once a release has been uploaded, you can log in to Zenodo and review it before it is published.

In order to upload releases on Zenodo when triggering the release workflow, you have to enable the Zenodo workflow in the template and to register a Zenodo Personal access token in GitHub:
- Set the variable `ENABLE_ZENODO` to `true` in `.github/github.env`.
- Set the `ZENODO_URL` to https://sandbox.zenodo.org for uploading releases on the Zenodo test environment, or to https://zenodo.org to upload releases on Zenodo.
- Create a Personal access token on Zenodo: open the `ZENODO_URL` in a web browser, log in, go to the Applications settings and create a new personal access token with scope "deposit:write". Copy the token and save it for the next step.
- In your GitHub project, create a new secret at the same place as you created the `PRIVATE_KEY` secret, name it `ZENODO_TOKEN` and as a value paste the token created in the previous step.

You can now trigger a new release in your release branch by pushing a pre-release tag:
```
git tag pre-v0.0.2
git push origin pre-v0.0.2
```

A GitHub release of your software will be created, and in addition, the release will be associated with a DOI and uploaded to Zenodo.
Once the workflow has run, you can log in to Zenodo to review and publish your software release.

#### Enable releases on RADAR

In order to use the RADAR workflow, you have to possess publication credentials on a [RADAR](https://www.radar-service.eu/) instance.
When the RADAR workflow is enabled, the software releases created by the release workflows will also be uploaded to RADAR.
Once a release has been uploaded, you can log in to RADAR and review it before it is published.

In order to use the RADAR release workflow, you have to enable the workflow and to register some RADAR secrets in GitHub:
- Set the variable `ENABLE_RADAR` to `true` in `.github/github.env`.
- In your GitHub project, create the following secrets at the same place as you created the `PRIVATE_KEY` secret:
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

A GitHub release of your software will be created, and in addition, the release will be associated with a DOI and uploaded to RADAR.
Once the workflow has run, you can log in to your RADAR instance to review and publish your software release.
