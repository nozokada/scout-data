from abc import ABC, abstractmethod
import firebase_admin
from firebase_admin import credentials, firestore
import json
from unsplash.api import Api
from unsplash.auth import Auth

from constants import UNSPLASH_CREDENTIALS_FILE_PATH, FIREBASE_CREDENTIALS_FILE_PATH


class APIProvider(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def authenticate(self):
        pass


class PhotoAPIProvider(APIProvider, ABC):

    def __init__(self):
        APIProvider.__init__(self)

    @abstractmethod
    def get_photos(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_photo(self, *args, **kwargs):
        pass


class FirebaseAPIProvider(APIProvider):

    def __init__(self):
        APIProvider.__init__(self)
        self._client = self.authenticate()

    def authenticate(self):
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_FILE_PATH)
        firebase_admin.initialize_app(cred)
        return firestore.client()
    
    def add_document(self, collection_id, document_id, data):
        collection_ref = self._client.collection(collection_id)
        document_ref = collection_ref.document(document_id)
        document_ref.set(data)


class UnsplashAPIProvider(PhotoAPIProvider):

    def __init__(self):
        PhotoAPIProvider.__init__(self)
        self._client = self.authenticate()

    def authenticate(self):
        with open(UNSPLASH_CREDENTIALS_FILE_PATH) as file:
            cred = json.load(file)
        return Api(Auth(**cred))

    def get_photos(self, *args, **kwargs):
        return self._client.photo.all(*args, **kwargs)
    
    def get_photo(self, *args, **kwargs):
        return self._client.photo.get(*args, **kwargs)