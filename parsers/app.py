from typing import List
from shared.file_app_client import FileAppClient

from deezer_client import DeezerClient
from yandex_client import YandexClient
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import hashlib
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from os import environ
from schemas import Track

DEEZER_SOURCE = "deezer"
YANDEX_SOURCE = "yandex"


SOURCE_NAME = "deezer"


parser_name = os.environ["PARSER"]




match parser_name:
    case "deezer":
        parser_client = DeezerClient()
    case "yandex":
        parser_client = YandexClient()
    case _:
        raise Exception(f"PARSER: {parser_name} not found   ")
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
    return parser_client.search(q)


@app.get("/api/play/{parser_name}/{track_id}.mp3")
async def play_track(request: Request, parser_name:str, track_id: int) -> bytes:
    return Response(content=parser_client.get_track_file_data(track_id), media_type="audio/mpeg")


@app.get("/api/save/{parser_name}/{track_id}")
async def save_track(request: Request, parser_name:str, track_id: int) -> bytes:
    
    parser_client.save_track(track_id, file_app_client)
    return JSONResponse(status_code=200, content={"success": "Upload Success!"})
