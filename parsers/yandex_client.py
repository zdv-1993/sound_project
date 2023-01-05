import requests
import hashlib
import uuid
import os
import time

from yandex_music import Client
from interfaces import IMusicParserClient
from schemas import Track
from typing import List


class YandexClient(IMusicParserClient):
    client_type = "yandex"
    def __init__(self):
        self._file_name = uuid.uuid4().hex + ".mp3"
        self._file_dir = "/tmp"
        self._file_path = os.path.join(self._file_dir, self._file_name)
        self._yandex = Client(os.environ["YANDEX_TOKEN"])

    def __del__(self):
        try:
            os.remove(self._file_path)
        except FileNotFoundError:
            pass

    
    def get_track_file_data(self, track_id: int) -> bytes:
        download_info = self._yandex.tracks_download_info(track_id)[0]
        # track_data = self.get_track(track_id)
        minimal_downloaded_time = time.time()
        download_info.download(self._file_path)

        is_loaded = os.path.getmtime(self._file_path) > minimal_downloaded_time
        if not is_loaded:
            raise Exception('Ошибка загрузки Yandex')
        with open(self._file_path, "rb") as f:
            return f.read()

    def search(self, q: str) -> List[Track]:
        from app import app
        yandex_res =  self._yandex.search(q, type_="track")
        res = []
        for item_yandex in yandex_res["tracks"]["results"]:
            cover_url = f"https://{item_yandex.cover_uri[:-2]}/400x400"
            res.append(
                Track(
                    name=item_yandex.title,
                    artist=item_yandex.artists[0].name,
                    image=cover_url,
                    path=os.environ["DEEZER_PROJECT_HOST"] + app.url_path_for("play_track", parser_name=self.client_type, track_id=item_yandex.id),
                    save_url=os.environ["DEEZER_PROJECT_HOST"] + app.url_path_for("save_track", parser_name=self.client_type, track_id=item_yandex.id),
                )
            )
        return res
    def save_track(self, track_id: int, file_app_client):
        track_data = self._yandex.tracks([track_id])[0]
        track_file_data = self.get_track_file_data(track_id)
        track_hash = hashlib.sha256(track_file_data).hexdigest()
        track_params_from_db = file_app_client.get_file_params(track_hash)
        if track_params_from_db and "error" not in track_params_from_db:
            return JSONResponse(status_code=400, content={"error": "file already exist!"})
        # Сохраняем картинку песни
        track_album_image_hash = f"https://{track_data.cover_uri[:-2]}/400x400"
        cover_data = requests.get(track_album_image_hash).content
        cover_hash = hashlib.sha256(cover_data).hexdigest()
        is_uploaded = file_app_client.upload_cover(
            file_bytes=cover_data,
            source_name=self.client_type,
            source_id=track_id,
        )
        # Загружаем трек
        return file_app_client.upload_music(
            file_bytes=track_file_data, 
            source_name=self.client_type,
            source_id=track_id,
            source_data=track_data.to_dict(),
            image=cover_hash,
        )