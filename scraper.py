from hashlib import md5

from constants import PHOTOS_REF_NAME
from provider import FirebaseAPIProvider, UnsplashAPIProvider

firebase_provider = FirebaseAPIProvider()
photo_provider = UnsplashAPIProvider()

for photo in photo_provider.get_photos(per_page=10, order_by='popular'):
    if photo.location.position.longitude and photo.location.position.latitude:
        document_id = md5(photo.id.encode()).hexdigest()
        firebase_provider.add_document(collection_id=PHOTOS_REF_NAME, document_id=document_id, data=photo.dict())
