import hashlib
import typing
from shared.file_app_client import FileAppClient
from orm import get_track_by_hash, create_track, create_track_file
from database import SessionLocal
from schemas import CreateTrack, CreateTrackFile, TrackData


class TrackImporter:
    def __init__(self, file_params):
        self._file_params = file_params

    def _get_track_deezer(self) -> CreateTrack:
        deezer_data = self._file_params["source_data"]
        # coздаем песню
        track_data = TrackData(
            album=deezer_data["album"],
            artists=[],
            year=deezer_data["year"]
        )
        return CreateTrack(
            title=deezer_data["title"],
            artist_name=deezer_data["artist_name"],
            data=track_data,
        )

    def get_track(self):
        source = self._file_params["source"]
        get_track_func = getattr(self, f"_get_track_{source}")
        return get_track_func()
        

def run_import():
    import pdb; pdb.set_trace()
    db = SessionLocal()
    file_app_client = FileAppClient()
    for file_hash in file_app_client.get_files_list():
        file_params = file_app_client.get_file_params(file_hash)
        if not file_params:
            continue
        track = TrackImporter(file_params).get_track()
        track_from_local_db = get_track_by_hash(db, track.hashed)
        if not track_from_local_db:
            # Если в базе есть, то просто пропускаем
            track_from_local_db = create_track(db, track)
        
        track_file = CreateTrackFile(
            id=file_hash,
            info={},
            track_id=track_from_local_db.id,
        )
        create_track_file(track_file)
        

        

        