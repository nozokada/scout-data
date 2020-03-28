from datetime import datetime

from pydantic import BaseModel


class Exif(BaseModel):
    aperture: str = None
    exposure_time: str = None
    focal_length: str = None
    iso: int = None
    make: str = None
    model: str = None


class Position(BaseModel):
    latitude: float = None
    longitude: float = None


class Location(BaseModel):
    city: str = None
    country: str = None
    position: Position


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
