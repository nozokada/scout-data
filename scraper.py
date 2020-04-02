import json
import random
import time
from datetime import datetime
from hashlib import md5

from dateutil.parser import parse
from google.cloud.firestore_v1 import GeoPoint
from unsplash import UnsplashError

from constants import PHOTOS_REF_NAME
from provider import FirebaseAPIProvider, UnsplashAPIProvider


class DataService:

    def __init__(self):
        self.firebase_provider = FirebaseAPIProvider()
        self.photo_provider = UnsplashAPIProvider()

    def scrape_photos(self, page_number):
        photos = []
        print(f'Scraping photos at page {page_number}...')
        for photo in self.photo_provider.get_photos(order_by='popular', per_page=15, page=page_number):
            if photo.location.position.longitude is None or photo.location.position.latitude is None:
                continue
            photos.append(photo)
        return photos

    def upload_scout_photo(self, photo):
        document_id = md5(photo.id.encode()).hexdigest()
        print(f'Uploading {photo.id}...')
        self.firebase_provider.add_document(
            collection_id=PHOTOS_REF_NAME, document_id=document_id, data=photo.dict()
        )

    def write_scout_photos_to_json(self):
        data = {}
        for doc in self.firebase_provider.get_documents(PHOTOS_REF_NAME):
            doc_id, doc_data = doc[0], doc[1]
            print(f'Downloaded {doc_id}')
            data[doc_id] = doc_data
            with open('photos.json', 'w') as file:
                json.dump(data, file, indent=4, sort_keys=True, default=self.support_scout_data_types)

    def read_scout_photos_from_json(self):
        with open('photos.json', 'r') as file:
            data = json.load(file, object_hook=self.parse_scout_data_types)

        for key, value in data.items():
            data_service.firebase_provider.add_document(
                collection_id="photos_test", document_id=key, data=value
            )

    @staticmethod
    def parse_scout_data_types(json_dict):
        for key, value in json_dict.items():
            if key == 'created':
                json_dict[key] = parse(value)
        return json_dict

    @staticmethod
    def support_scout_data_types(o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, GeoPoint):
            latitude, longitude = float(o.latitude), float(o.longitude)
            return {
                'latitude': latitude,
                'longitude': longitude
            }
        raise TypeError(repr(o) + ' is not JSON serializable')

    def execute_scraping_cycle(self, page_number):
        while True:
            try:
                for photo in self.scrape_photos(page_number):
                    self.upload_scout_photo(photo)
            except UnsplashError as e:
                print(f'Handling Unsplash error: {e}')
                time.sleep(3600)
                continue

            page_number += 1
            wait_seconds = random.randint(0, 3600)
            print(f'Waiting for {wait_seconds} seconds to avoid rate limiting...')
            time.sleep(wait_seconds)


data_service = DataService()

# data_service.execute_scraping_cycle(page_number=126)

# data_service.write_scout_photos_to_json()

data_service.read_scout_photos_from_json()
