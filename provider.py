import json
from abc import ABC, abstractmethod

import firebase_admin
from dateutil.parser import parse
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import GeoPoint
from unsplash.api import Api
from unsplash.auth import Auth

from constants import UNSPLASH_CREDENTIALS_FILE_PATH, FIREBASE_CREDENTIALS_FILE_PATH
from models import Photo, Location, Exif, PhotoUrls, User


class APIProvider(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def _authenticate(self):
        pass


class PhotoAPIProvider(APIProvider, ABC):

    def __init__(self):
        APIProvider.__init__(self)

    @abstractmethod
    def get_photos(self, *args, **kwargs):
        pass


class FirebaseAPIProvider(APIProvider):

    def __init__(self):
        APIProvider.__init__(self)
        self._client = self._authenticate()

    def _authenticate(self):
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_FILE_PATH)
        firebase_admin.initialize_app(cred)
        return firestore.client()

    def add_document(self, collection_id, document_id, data):
        collection_ref = self._client.collection(collection_id)
        if document_id:
            document_ref = collection_ref.document(document_id)
            document_ref.set(data)
        else:
            collection_ref.add(data)

    def get_documents(self, collection_id):
        collection_ref = self._client.collection(collection_id)
        for doc in collection_ref.stream():
            yield {'id': doc.id, 'data': doc.to_dict()}

    def search_documents(self, collection_id, wheres):
        collection_ref = self._client.collection(collection_id)
        for where in wheres:
            collection_ref = collection_ref.where(*where)
        for doc in collection_ref.stream():
            yield {'id': doc.id, 'data': doc.to_dict()}


class UnsplashAPIProvider(PhotoAPIProvider):

    def __init__(self):
        PhotoAPIProvider.__init__(self)
        self._client = self._authenticate()

    def _authenticate(self):
        with open(UNSPLASH_CREDENTIALS_FILE_PATH) as file:
            cred = json.load(file)
        return Api(Auth(**cred))

    def get_photos(self, *args, **kwargs):
        photos = (self.get_photo(listed_photo.id) for listed_photo in self._client.photo.all(*args, **kwargs))
        for photo in photos:
            yield self.convert(photo)

    def get_photo(self, *args, **kwargs):
        return self._client.photo.get(*args, **kwargs)

    @staticmethod
    def convert(photo):
        location = Location(
            city=photo.location.city,
            country=photo.location.country,
            position=GeoPoint(
                latitude=photo.location.position['latitude'],
                longitude=photo.location.position['longitude']
            ),
        )

        exif = Exif(
            aperture=photo.exif.aperture,
            exposure_time=photo.exif.exposure_time,
            focal_length=photo.exif.focal_length,
            iso=photo.exif.iso,
            make=photo.exif.make,
            model=photo.exif.model,
        )

        urls = PhotoUrls(
            full=photo.urls.full,
            raw=photo.urls.raw,
            regular=photo.urls.regular,
            small=photo.urls.small,
            thumb=photo.urls.thumb,
        )

        return Photo(
            raw_id=photo.id,
            provider='unsplash',
            likes=photo.likes,
            location=location,
            exif=exif,
            tags={tag: True for tag in (tag['title'] for tag in photo.tags)},
            created=parse(photo.created_at),
            urls=urls,
            user=User(name=photo.user.name),
        )
