from pydantic import BaseModel


class Track(BaseModel):
    save_url: str
    name: str
    artist: str
    image: str
    path: str
