import logging
import os
import tempfile
import xml.etree.ElementTree as ET

import boto3
import requests
from boto3.s3.transfer import TransferConfig

log = logging.getLogger('its_live_monitoring')
log.setLevel(logging.INFO)

s3 = boto3.client('s3')


def download_file(url, download_path):
    session = requests.Session()
    with session.get(url, stream=True) as s:
        s.raise_for_status()
        with open(download_path, 'wb') as f:
            for chunk in s.iter_content(chunk_size=8*1024*1024):
                if chunk:
                    f.write(chunk)
    session.close()


def get_s2_safe_url(scene_name):
    root_url = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles'
    tile = f'{scene_name[39:41]}/{scene_name[41:42]}/{scene_name[42:44]}'
    return f'{root_url}/{tile}/{scene_name}.SAFE'


def get_s2_manifest(safe_url: str):
    manifest_url = f'{safe_url}/manifest.safe'
    response = requests.get(manifest_url)
    response.raise_for_status()
    return response.text


def get_s2_path(scene_name: str) -> str:
    safe_url = get_s2_safe_url(scene_name)

    manifest_text = get_s2_manifest(safe_url)
    root = ET.fromstring(manifest_text)
    elements = root.findall(".//fileLocation[@locatorType='URL'][@href]")
    hrefs = [element.attrib['href'] for element in elements if
             element.attrib['href'].endswith('_B08.jp2') and '/IMG_DATA/' in element.attrib['href']]
    if len(hrefs) == 1:
        # post-2016-12-06 scene; only one tile
        file_path = hrefs[0]
    else:
        # pre-2016-12-06 scene; choose the requested tile
        tile_token = scene_name.split('_')[5]
        file_path = [href for href in hrefs if href.endswith(f'_{tile_token}_B08.jp2')][0]

    return f'{safe_url}/{file_path}'


def fetch_scene(scene_name, bucket_name, bucket_prefix):
    google_cloud_url = get_s2_path(scene_name)
    with tempfile.NamedTemporaryFile() as foo:
        download_file(google_cloud_url, foo.name)

        key = f'{bucket_prefix}{scene_name}_B08.jp2'
        transfer_config = TransferConfig(multipart_threshold=150*1024*1024, multipart_chunksize=100*1024*1024)
        s3.upload_file(foo.name, bucket_name, key, Config=transfer_config)


def lambda_handler(event: dict, context: object) -> dict:
    bucket_name = os.getenv('BUCKET_NAME')
    bucket_prefix = os.getenv('BUCKET_PREFIX')

    batch_item_failures = []
    for record in event['Records']:
        try:
            scene = record['body']
            print(f'Processing {scene}')
            fetch_scene(scene, bucket_name, bucket_prefix)
        except Exception:
            log.exception(f'Could not process message {record["messageId"]}')
            batch_item_failures.append({'itemIdentifier': record['messageId']})
    return {'batchItemFailures': batch_item_failures}
