from abc import abstractmethod
from schemas import Track

from typing import List


class IMusicParserClient:
    
    @abstractmethod
    def get_track_file_data(self, track_id: int) -> bytes:
        "Get track file data from id"
    
    @abstractmethod
    def search(self, q: str) -> List[Track]:
        "Search tracks by query string"

    def save_track(self, track_id, file_app_client) -> bool:
        "Save track to local file server"
