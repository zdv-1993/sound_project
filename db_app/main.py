from typing import Union

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates

from models import Track, Base
from database import engine, SessionLocal

from fastapi.responses import HTMLResponse, Response, JSONResponse

from fastapi.staticfiles import StaticFiles
import orm
from schemas import TrackApiOutput
from os import environ

from shared.file_app_client import FileAppClient
from importer import run_import

app = FastAPI()


Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="/app/static"), name="static")


templates = Jinja2Templates(directory="/app/templates")

file_app_client = FileAppClient()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def search_view(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/tracks")
def all_tracks(db = Depends(get_db)):
    run_import()
    res = []
    for track_item, track_file_item in orm.get_tracks(db):
        path = environ['DB_SITE_PROJECT_HOST'] + app.url_path_for("play_track", track_hash=track_file_item.id, track_len=track_file_item.info["len"])
        
        res.append(TrackApiOutput(
            id=track_item.id,
            title=track_item.title,
            link=path,
            artist=track_item.artist_name,
        ))
    return res


@app.get("/api/play/{track_len}/{track_hash}.mp3")
async def play_track(request: Request, track_len:int, track_hash: str) -> bytes:
    return Response(content=file_app_client.get_file_data(track_hash, track_len), media_type="audio/mpeg")
