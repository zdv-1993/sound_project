from pydantic import BaseModel

import typing


class TrackData(BaseModel):
    album: str
    artists: typing.List[str]
    year: int


class CreateTrack(BaseModel):
    title: str
    artist_name: str
    data: TrackData

    @property
    def hashed(self):
        return hash(tuple(self.title, ) + tuple(self.data.artists))


class CreateTrackFile(BaseModel):
    id: str
    info: dict
    track_id: int
