import json
import random
import time
from datetime import datetime
from hashlib import md5

from dateutil.parser import parse
from google.cloud.firestore_v1 import GeoPoint
from unsplash import UnsplashError

from constants import TP_PHOTOS_REF_NAME
from provider import FirebaseAPIProvider, UnsplashAPIProvider


class DataService:

    def __init__(self):
        self.firebase_provider = FirebaseAPIProvider()
        self.photo_provider = UnsplashAPIProvider()

    def _scrape_photos(self, page_number):
        photos = []
        print(f'Scraping photos at page {page_number}...')
        for photo in self.photo_provider.get_photos(order_by='popular', per_page=15, page=page_number):
            if photo.location.position.longitude is None or photo.location.position.latitude is None:
                continue
            photos.append(photo)
        return photos

    def execute_photo_scraping_cycle(self, page_number):
        while True:
            try:
                for photo in self._scrape_photos(page_number):
                    hash_id = md5(photo.raw_id.encode()).hexdigest()
                    print(f'Adding document for photo {hash_id}...')
                    self.firebase_provider.add_document(
                        collection_id=TP_PHOTOS_REF_NAME, document_id=hash_id, data=photo.dict()
                    )
            except UnsplashError as e:
                print(f'Handling Unsplash error: {e}')
                self.wait_for_random_seconds(min=3600)
                continue

            page_number += 1
            self.wait_for_random_seconds()

    def download_scout_doc_to_json(self, collection_id):
        data = {}
        for doc in self.firebase_provider.get_documents(collection_id):
            doc_id, doc_data = doc['id'], doc['data']
            data[doc_id] = doc_data
        with open(f'{collection_id}.json', 'w') as file:
            json.dump(data, file, indent=4, sort_keys=True, default=self.dump_scout_data_types)

    def upload_scout_docs_from_json(self, collection_id):
        with open(f'{collection_id}.json', 'r') as file:
            data = json.load(file, object_hook=self.load_scout_data_types)
        for key, value in data.items():
            self.firebase_provider.add_document(collection_id=collection_id, document_id=key, data=value)

    @staticmethod
    def wait_for_random_seconds(min=0, max=3600):
        wait_seconds = random.randint(min, max)
        print(f'Waiting for {wait_seconds} seconds to avoid rate limiting...')
        time.sleep(wait_seconds)

    @staticmethod
    def dump_scout_data_types(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(repr(o) + ' is not JSON serializable')

    @staticmethod
    def load_scout_data_types(json_dict):
        for key, value in json_dict.items():
            if key == 'created':
                json_dict[key] = parse(value)
            elif key == 'position':
                json_dict[key] = GeoPoint(value['latitude'], value['longitude'])
        return json_dict


data_service = DataService()

data_service.execute_photo_scraping_cycle(page_number=125)
# data_service.download_scout_photos_to_json(collection_id=TP_PHOTOS_REF_NAME)
# data_service.upload_scout_docs_from_json(collection_id=TP_PHOTOS_REF_NAME)
