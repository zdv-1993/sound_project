
from shared.file_app_client import FileAppClient

from deezer_client import DeezerClient
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import hashlib
from fastapi.middleware.cors import CORSMiddleware
import requests


from typing import List
from os import environ


SOURCE_NAME = "deezer"

class Track(BaseModel):
    save_url: str
    name: str
    artist: str
    image: str
    path: str



deezer_client = DeezerClient()

file_app_client = FileAppClient()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="/app/static"), name="static")


templates = Jinja2Templates(directory="/app/templates")


@app.get("/", response_class=HTMLResponse)
async def search_view(request: Request):
    return templates.TemplateResponse("player.html", {"request": request})


@app.get("/api/search")
async def search_track(request: Request, q: str) -> List[Track]:
    res = list()

    # from pudb import remote
    # remote.set_trace(term_size=(180, 39), host='0.0.0.0', port=6930)
    for deezer_track in deezer_client.search(q):
        res.append(
            Track(
                name=deezer_track["title"],
                artist=deezer_track["artist"]["name"],
                image=deezer_track["album"]["cover"],
                path=environ['DEEZER_PROJECT_HOST'] + app.url_path_for("play_track", track_id=deezer_track["id"]),
                save_url=environ['DEEZER_PROJECT_HOST'] + app.url_path_for("save_track", track_id=deezer_track["id"]),
            )
        )

    return res


@app.get("/api/play/{track_id}.mp3")
async def play_track(request: Request, track_id: int) -> bytes:
    return Response(content=deezer_client.get_track_file_data(track_id), media_type="audio/mpeg")


@app.get("/api/save/{track_id}")
async def save_track(request: Request, track_id: int) -> bytes:
    
    track_file_data = deezer_client.get_track_file_data(track_id)
    track_data = deezer_client.get_track(track_id)
    track_hash = hashlib.sha256(track_file_data).hexdigest()
    track_params_from_db = file_app_client.get_file_params(track_hash)
    if track_params_from_db and "error" not in track_params_from_db:
        return JSONResponse(status_code=400, content={"error": "file already exist!"})
    # Сохраняем картинку песни
    track_album_image_hash = track_data["info"]["DATA"]["ALB_PICTURE"]
    album_image_url = f"https://cdns-images.dzcdn.net/images/cover/{track_album_image_hash}/500x500-000000-80-0-0.jpg"
    cover_data = requests.get(album_image_url).content
    cover_hash = hashlib.sha256(cover_data).hexdigest()
    is_uploaded = file_app_client.upload_cover(
        file_bytes=cover_data,
        source_name=SOURCE_NAME,
        source_id=track_id,
    )
    # Загружаем трек
    file_app_client.upload_music(
        file_bytes=track_file_data, 
        source_name=SOURCE_NAME,
        source_id=track_id,
        source_data=track_data["info"],
        image=cover_hash,
        )
    return JSONResponse(status_code=200, content={"success": "Upload Success!"})