import hashlib
import uuid
import os
import time

from pydeezer import Downloader
from pydeezer.constants import track_formats
from pydeezer import Deezer


class DeezerUploadError(Exception):
    name = "Ощибка загрузки файла из deezer"


class DeezerClient:
    def __init__(self):
        self._file_name = uuid.uuid4().hex + ".mp3"
        self._file_dir = "/tmp"
        self._file_path = os.path.join(self._file_dir, self._file_name)
        self._deezer = Deezer(arl=os.environ["DEEZER_ARL"])

    def __del__(self):
        try:
            os.remove(self._file_path)
        except FileNotFoundError:
            pass

    def get_track(self, track_id: str):
        return self._deezer.get_track(track_id)
    
    def get_track_file_data(self, track_id: int):
        track_data = self.get_track(track_id)
        minimal_downloaded_time = time.time()
        track_data["download"](self._file_dir, quality=track_formats.FLAC, filename=self._file_name)
        is_loaded = os.path.getmtime(self._file_path) > minimal_downloaded_time
        if not is_loaded:
            raise DeezerUploadError()
        with open(self._file_path, "rb") as f:
            return f.read()

    def search(self, q: str):
        return self._deezer.search_tracks(q)

# ARL_WORKED = "c8ebe1da6c4d92bc70c106eda6323057cd17c59351ba493a40e35eda82f583a5ba30b9a733caa3af586ec6923b4506adc95ad353f11ca16846df7c5251ed5ffcf0b9f4c82404934dd551b6492d54be598f17a01fdfd5fd775c7e508ce148ae0d"

# ARL_MY = "ac8ce781eff5cb6aa3e7af7fdf21fee948c61c116a8027413da3aa0e7aaad6b2b4f686c0df9ce05af99291d23b275fe0575d48ae5fa544f27ba6192a9fe53565f064165578726e3f7e362e2f77ba693f05a780523a4c95fa20cb7eeaf95df32c"

# ARL_TEST = "1b322915e79453e6ef2e615fad5175c2b55de098b3406fad3f56dfcdbb386d121ab989c75fd3927b9eb7cfc82ec764dca677123f61969a6c0b11e11d1a5fd6aa3f6abd6cf011918a49fb52b5abe65635d2b7b0e93321cc25af7140da8ce903fe"
# arl = ARL_MY

# TMP_FILE_NAME = "tmp_file.mp3"
# FILE_DIR = "deezer_files"
# TMP_FILE_PATH = os.path.join(FILE_DIR, TMP_FILE_NAME)

# deezer = Deezer(arl=arl)


# download_dir = "deezer_files"

# track_id = "547653622"
# track = deezer.get_track(track_id)
# # track is now a dict with a key of info, download, tags, and get_tag
# # info and tags are dict
# track_info = track["info"]
# tags_separated_by_comma = track["tags"]
# # download and get_tag are partial functions
# #track["download"](download_dir, quality=track_formats.MP3_320) # this will download the file, default file name is Filename.[mp3 or flac]


# from pudb import remote
# remote.set_trace(term_size=(180, 39), host='0.0.0.0', port=6930)
# minimal_downloaded_time = time.time()
# ff = track["download"](download_dir, quality=track_formats.FLAC, filename=TMP_FILE_NAME) # this will download the file, default file name is Filename.[mp3 or flac]

# is_loaded = os.path.getmtime(TMP_FILE_PATH) > minimal_downloaded_time
# if not is_loaded:
#     raise Exception("Ошибка загрузки")
# tags_separated_by_semicolon = track["get_tag"](separator="; ") # this will return a dictionary similar to track["tags"] but this will override the default separator
# print(1)
# # artist_id = "53859305"
# # artist = deezer.get_artist(artist_id)

# # album_id = "39949511"
# # album = deezer.get_album(album_id) # returns a dict containing data about the album

# # playlist_id = "1370794195"
# # playlist = deezer.get_playlist(playlist_id) # returns a dict containing data about the playlist

# # # Multithreaded Downloader

# # list_of_id = ["572537082",
# #               "921278352",
# #               "927432162",
# #               "547653622"]

# # downloader = Downloader(deezer, list_of_ids, download_dir,
# #                         quality=track_formats.MP3_320, concurrent_downloads=2)
# # downloader.start()
