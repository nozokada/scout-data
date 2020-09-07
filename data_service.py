import json
import logging
import random
import time
from datetime import datetime
from hashlib import md5

from dateutil.parser import parse
from google.cloud.firestore_v1 import GeoPoint

from constants import TP_PHOTOS_REF_NAME
from provider import FirebaseAPIProvider, UnsplashAPIProvider, APIProviderError


def load_scout_data_types(json_dict):
    for key, value in json_dict.items():
        if key == 'created':
            json_dict[key] = parse(value)
        elif key == 'position':
            json_dict[key] = GeoPoint(value['latitude'], value['longitude'])
    return json_dict


def dump_scout_data_types(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(repr(o) + ' is not JSON serializable')


def wait_for_random_seconds(min=0, max=3600):
    wait_seconds = random.randint(min, max)
    logging.info(f'Waiting for {wait_seconds} seconds to avoid rate limiting...')
    time.sleep(wait_seconds)


class DataService:

    def __init__(self):
        self.firebase_provider = FirebaseAPIProvider()
        self.photo_provider = UnsplashAPIProvider()

    def _get_photo_data(self, page_number):
        photos = []
        logging.info(f'Retrieving photos at page {page_number}...')
        for photo in self.photo_provider.get_photos(order_by='popular', per_page=15, page=page_number):
            if photo.location.position.longitude is None or photo.location.position.latitude is None:
                continue
            photos.append(photo)
        return photos

    def execute_scout_data_generation_cycle(self, page_number):
        while True:
            try:
                for photo in self._get_photo_data(page_number):
                    hash_id = md5(photo.raw_id.encode()).hexdigest()
                    logging.info(f'Adding document for photo {hash_id}...')
                    self.firebase_provider.add_document(
                        collection_id=TP_PHOTOS_REF_NAME, document_id=hash_id, data=photo.dict()
                    )
            except APIProviderError as e:
                logging.info(f'Handling API Provider error: {e}')
                wait_for_random_seconds(min=3600)
                continue

            page_number += 1
            wait_for_random_seconds(min=600, max=1800)

    def download_scout_data(self, collection_id):
        data = {}
        for doc in self.firebase_provider.get_documents(collection_id):
            doc_id, doc_data = doc['id'], doc['data']
            data[doc_id] = doc_data
        with open(f'{collection_id}.json', 'w') as file:
            json.dump(data, file, indent=4, sort_keys=True, default=dump_scout_data_types)

    def upload_scout_data(self, collection_id):
        with open(f'{collection_id}.json', 'r') as file:
            data = json.load(file, object_hook=load_scout_data_types)
        for key, value in data.items():
            self.firebase_provider.add_document(collection_id=collection_id, document_id=key, data=value)
