
from shared.file_app_client import FileAppClient

from deezer_client import DeezerClient
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from typing import List


class Track(BaseModel):
    name: str
    artist: str
    image: str
    path: str



deezer_client = DeezerClient()


app = FastAPI()

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
                path=app.url_path_for("play_track", track_id=deezer_track["id"])
            )
        )

    return res


@app.get("/api/play/{track_id}.mp3")
async def play_track(request: Request, track_id: int) -> bytes:
    
    return Response(content=deezer_client.get_track_file_data(track_id), media_type="audio/mpeg")


@app.get("/api/save/{track_id}")
async def play_track(request: Request, track_id: int) -> bytes:
    track_file_data = deezer_client.get_track_file_data(track_id)

    return Response(content=deezer_client.get_track_file_data(track_id), media_type="audio/mpeg")