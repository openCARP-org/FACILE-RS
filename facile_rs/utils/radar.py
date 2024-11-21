import logging

import requests

logger = logging.getLogger(__file__)


def fetch_radar_token(radar_url, client_id, client_secret, redirect_url, username, password):
    """
    Fetch RADAR token using the RADAR API.

    :param radar_url: URL to the RADAR repository
    :param client_id: RADAR client ID
    :param client_secret: RADAR client secret
    :param redirect_url: RADAR redirect URL
    :param username: RADAR username
    :param password: RADAR password
    :return: RADAR token for the given user
    """
    url = radar_url + '/radar/api/tokens'
    try:
        response = requests.post(url, json={
            'clientId': client_id,
            'clientSecret': client_secret,
            'redirectUrl': redirect_url,
            'userName': username,
            'userPassword': password
        })
        response.raise_for_status()
        logger.debug('response = %s', response.json())
    except requests.exceptions.HTTPError as e:
        print(response.text)
        raise e

    tokens = response.json()
    return {
        'Authorization': 'Bearer {}'.format(tokens['access_token'])
    }


def create_radar_dataset(radar_url, workspace_id, headers, radar_dict):
    """
    Create a dataset in the given RADAR workspace, using the token provided in headers.

    :param radar_url: URL to the RADAR repository
    :param workspace_id: RADAR workspace ID
    :param headers: request headers. Typically the RADAR token, as returned by fetch_radar_token
    :param radar_dict: RADAR metadata dictionary, as returned by RadarMetadata.as_dict()
    :return: RADAR dataset ID
    """
    url = radar_url + f'/radar/api/workspaces/{workspace_id}/datasets'
    try:
        response = requests.post(url, headers=headers, json=radar_dict)
        response.raise_for_status()
        logger.debug('response = %s', response.json())
        return response.json()['id']
    except requests.exceptions.HTTPError as e:
        print(response.text)
        raise e


def prepare_radar_dataset(radar_url, dataset_id, headers):
    """"
    Prepare a dataset for review in RADAR.

    :param radar_url: URL to the RADAR repository
    :param dataset_id: RADAR dataset ID
    :param headers: request headers. Typically the RADAR token, as returned by fetch_radar_token
    :return: RADAR response to the request
    """

    review_url = radar_url + f'/radar/api/datasets/{dataset_id}/startreview'
    try:
        response = requests.post(review_url, headers=headers)
        if response.status_code == 422:
            dataset_url = radar_url + f'/radar/api/datasets/{dataset_id}/'
            response = requests.get(dataset_url, headers=headers)
            response.raise_for_status()
            logger.debug('response = %s', response.json())
            return response.json()
        else:
            logger.debug('response = %s', response.json())
            raise RuntimeError('startreview did not return 422')
    except requests.exceptions.HTTPError as e:
        print(response.text)
        raise e


def update_radar_dataset(radar_url, dataset_id, headers, radar_dict):
    """
    Update a dataset's metadata in the given RADAR workspace.

    :param radar_url: URL to the RADAR repository
    :param dataset_id: RADAR dataset ID
    :param headers: request headers. Typically the RADAR token, as returned by fetch_radar_token
    :param radar_dict: RADAR metadata dictionary, as returned by RadarMetadata.as_dict()
    :return: RADAR dataset ID
    """
    url = radar_url + f'/radar/api/datasets/{dataset_id}'
    try:
        response = requests.put(url, headers=headers, json=radar_dict)
        response.raise_for_status()
        logger.debug('response = %s', response.json())
        return response.json()['id']
    except requests.exceptions.HTTPError as e:
        print(response.text)
        raise e


def upload_radar_assets(radar_url, dataset_id, headers, assets, path):
    """
    Upload assets to a RADAR dataset.

    :param radar_url: URL to the RADAR repository
    :param dataset_id: RADAR dataset ID
    :param headers: request headers. Typically the RADAR token, as returned by fetch_radar_token
    :param assets: locations of assets to upload
    :type assets: list
    :param path: location where the assets are collected before upload
    """
    url = radar_url + f'/radar-ingest/upload/{dataset_id}/file'
    for location in assets:
        target = path / location.split('/')[-1]
        files = {'upload_file': open(target, 'rb')}

        try:
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
            logger.debug('response = %s', response.text)
        except requests.exceptions.HTTPError as e:
            print(response.text)
            raise e
