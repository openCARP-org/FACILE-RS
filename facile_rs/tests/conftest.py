import pytest


@pytest.fixture(autouse=True)
def unset_facilers_env(monkeypatch):
    """
    Ensure not to use variables defined in external environment when running tests.
    """
    env_vars = [
        'ASSETS',
        'BAG_INFO_LOCATION',
        'BAG_PATH',
        'CFF_PATH',
        'CODEMETA_LOCATION',
        'CONTRIBUTORS_LOCATIONS',
        'CREATORS_LOCATIONS',
        'DATE',
        'DATACITE_PATH',
        'GRAV_PATH',
        'LOG_FILE',
        'LOG_LEVEL',
        'NOTIFICATION_EMAIL',
        'PIPELINE',
        'PIPELINE_CSL',
        'PIPELINE_FOOTER',
        'PIPELINE_HEADER',
        'PIPELINE_IMAGES',
        'PIPELINE_REFS',
        'PIPELINE_SOURCE',
        'PRIVATE_TOKEN',
        'RADAR_BACKLINK',
        'RADAR_CLIENT_ID',
        'RADAR_CLIENT_SECRET',
        'RADAR_EMAIL',
        'RADAR_PASSWORD',
        'RADAR_PATH',
        'RADAR_REDIRECT_URL',
        'RADAR_URL',
        'RADAR_USERNAME',
        'RADAR_WORKSPACE_ID',
        'RELEASE_API_URL',
        'RELEASE_DESCRIPTION',
        'RELEASE_TAG',
        'SMTP_SERVER',
        'VERSION',
        'ZENODO_PATH',
        'ZENODO_TOKEN',
        'ZENODO_URL',
    ]
    for env_var in env_vars:
        monkeypatch.delenv(env_var, raising=False)
    yield
