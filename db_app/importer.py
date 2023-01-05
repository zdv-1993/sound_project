import hashlib
import typing
from shared.file_app_client import FileAppClient
from orm import get_track_by_hash, create_track, create_track_file, get_track_file
from database import SessionLocal
from schemas import CreateTrack, CreateTrackFile, TrackData


class TrackImporter:
    def __init__(self, file_params):
        self._file_params = file_params

    def _get_track_deezer(self) -> CreateTrack:
        deezer_data = self._file_params["source_data"]
        track_title = deezer_data["DATA"].get("SNG_TITLE")
        album_title = deezer_data["DATA"].get("ALB_TITLE")
        artist_name = deezer_data["DATA"].get("ART_NAME")

        artists = [i["ART_NAME"] for i in deezer_data["DATA"].get("ARTISTS")]
        try:
            year = deezer_data["ISRC"]["data"][0]["DIGITAL_RELEASE_DATE"][:4]
        except:
            year = 1900
        # coздаем песню
        track_data = TrackData(
            album=album_title,
            artists=artists,
            year=year,
            
        )
        return CreateTrack(
            title=track_title,
            artist_name=artist_name,
            data=track_data,
        )
    def _get_track_yandex(self) -> CreateTrack:
        from pudb import remote
        remote.set_trace(term_size=(180, 39), host='0.0.0.0', port=6930)
        yandex_data = self._file_params["source_data"]
        track_title = yandex_data["title"]
        artist_name = yandex_data["artists"][0]["name"]
        album_title = yandex_data["albums"][0]["title"]
        artists = [i["name"] for i in yandex_data["artists"]]
        try:
            # TODO: Поправить получение года
            year = yandex_data["year"]
        except:
            year = 1900
        track_data = TrackData(
            album=album_title,
            artists=artists,
            year=year,
        )
        return CreateTrack(
            title=track_title,
            artist_name=artist_name,
            data=track_data,
        )



    def _get_track_file(self, track_id: str) -> CreateTrackFile:
        deezer_data = self._file_params["source_data"]
        return CreateTrackFile(
            id=self._file_params["hash"],
            info={
                "len": self._file_params["file_len"]
            },
            track_id=track_id,
        )

    def get_track(self):
        source = self._file_params["source_name"]
        get_track_func = getattr(self, f"_get_track_{source}")
        return get_track_func()

    def get_track_file(self, track_id: str):
        source = self._file_params["source_name"]
        get_track_file_func = getattr(self, f"_get_track_file")
        return get_track_file_func(track_id)


def run_import():
    db = SessionLocal()
    file_app_client = FileAppClient()
    for file_hash in file_app_client.get_files_list():
        file_params = file_app_client.get_file_params(file_hash)
        if not file_params:
            continue
        if file_params.get("type") != "music":
            continue
        track_importer = TrackImporter(file_params)
        if get_track_file(db, file_hash):
            continue
        track = track_importer.get_track()

        track_from_local_db = get_track_by_hash(db, track.hashed)

        if not track_from_local_db:
            # Если в базе есть, то просто пропускаем
            track_from_local_db = create_track(db, track)

        track_file = track_importer.get_track_file(track_from_local_db.id)
        create_track_file(db, track_file)
        

if __name__ == "__main__":
    run_import()
        