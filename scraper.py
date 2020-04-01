import random
import time
from hashlib import md5

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

    def upload_photo(self, photo):
        document_id = md5(photo.id.encode()).hexdigest()
        print(f'Uploading {photo.id}...')
        self.firebase_provider.add_document(
            collection_id=PHOTOS_REF_NAME, document_id=document_id, data=photo.dict()
        )

    def execute_scraping_cycle(self, page_number):
        while True:
            try:
                for photo in self.scrape_photos(page_number):
                    self.upload_photo(photo)
            except UnsplashError as e:
                print(f'Handling Unsplash error: {e}')
                time.sleep(3600)
                continue

            page_number += 1
            wait_seconds = random.randint(0, 3600)
            print(f'Waiting for {wait_seconds} seconds to avoid rate limiting...')
            time.sleep(wait_seconds)


data_service = DataService()
data_service.execute_scraping_cycle(page_number=126)
