from dateutil.parser import parse
from hashlib import md5

from provider import FirebaseAPIProvider, UnsplashAPIProvider

firebase_provider = FirebaseAPIProvider()
photo_provider = UnsplashAPIProvider()

photos = (photo_provider.get_photo(photo.id) for photo in photo_provider.get_photos(per_page=1, order_by='popular'))
for photo in photos:
    document_id = md5(photo.id.encode()).hexdigest()
    tags = {tag: True for tag in (tag['title'] for tag in photo.tags)}
    data = {
        'id': photo.id,
        'provider': 'unsplash',
        'likes': photo.likes,
        'location': {
            'city': photo.location.city,
            'country': photo.location.country,
            'position': photo.location.position,
        },
        'exif': {
            'aperture': photo.exif.aperture,
            'exposure_time': photo.exif.exposure_time,
            'focal_length': photo.exif.focal_length,
            'iso': photo.exif.iso,
            'make': photo.exif.make,
            'model': photo.exif.model,
        },
        'tags': tags,
        'created': parse(photo.created_at),
        'urls': {
            'full': photo.urls.full,
            'raw': photo.urls.raw,
            'regular': photo.urls.regular,
            'small': photo.urls.small,
            'thumb': photo.urls.thumb,
        },
        'user': {
            'name': photo.user.name,
        },
    }
    firebase_provider.add_document(collection_id='photos', document_id=document_id, data=data)
