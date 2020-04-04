import json
import random
import time
from datetime import datetime
from hashlib import md5

from dateutil.parser import parse
from unsplash import UnsplashError

from constants import PHOTOS_REF_NAME
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
                    self.firebase_provider.add_document(
                        collection_id=PHOTOS_REF_NAME,
                        document_id=f'photo_{md5(photo.id.encode()).hexdigest()}',
                        data=photo.dict()
                    )
            except UnsplashError as e:
                print(f'Handling Unsplash error: {e}')
                time.sleep(3600)
                continue

            page_number += 1
            wait_seconds = random.randint(0, 3600)
            print(f'Waiting for {wait_seconds} seconds to avoid rate limiting...')
            time.sleep(wait_seconds)

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
            self.firebase_provider.add_document(collection_id=collection_id, document_id=f'photo_{key}', data=value)

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
        return json_dict


data_service = DataService()

# data_service.execute_scraping_cycle(page_number=126)

# data_service.download_scout_photos_to_json(collection_id=PHOTOS_REF_NAME)

# data_service.upload_scout_docs_from_json(collection_id=PHOTOS_REF_NAME)

# results = data_service.firebase_provider.search_documents(
#     collection_id='photos_test',
#     wheres=[('location.position.latitude', '==', 52.47552833), ('location.position.longitude', '==', -1.88157833)]
# )
# print(list(results))
