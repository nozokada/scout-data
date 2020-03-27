from datetime import datetime

from pydantic import BaseModel


class Exif(BaseModel):
    aperture: str
    exposure_time: str
    focal_length: str
    iso: int
    make: str
    model: str


class Location(BaseModel):
    city: str = None
    country: str = None
    position: str = None


class PhotoUrls(BaseModel):
    full: str
    raw: str
    regular: str
    small: str
    thumb: str


class User(BaseModel):
    name: str


class Photo(BaseModel):
    id: str
    provider: str
    likes: int
    location: Location
    exif: Exif
    tags: dict
    created: datetime
    urls: PhotoUrls
    user: User
