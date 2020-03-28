from hashlib import md5

from constants import PHOTOS_REF_NAME
from provider import FirebaseAPIProvider, UnsplashAPIProvider


class DataService:

    def __init__(self):
        self.firebase_provider = FirebaseAPIProvider()
        self.photo_provider = UnsplashAPIProvider()

    def upload_photos(self):
        for photo in self.photo_provider.get_photos(per_page=10, order_by='popular'):
            if photo.location.position.longitude is None or photo.location.position.latitude is None:
                continue
            document_id = md5(photo.id.encode()).hexdigest()
            self.firebase_provider.add_document(
                collection_id=PHOTOS_REF_NAME, document_id=document_id, data=photo.dict()
            )


data_service = DataService()
data_service.upload_photos()

