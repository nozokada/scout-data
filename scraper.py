from dateutil.parser import parse
from hashlib import md5

from provider import FirebaseAPIProvider, UnsplashAPIProvider

firebase_provider = FirebaseAPIProvider()
photo_provider = UnsplashAPIProvider()

photos = photo_provider.get_photos(per_page=1, order_by='popular')
for photo in photos:
    document_id = md5(photo.id.encode()).hexdigest()
    firebase_provider.add_document(collection_id='photos', document_id=document_id, data=photo.dict())
