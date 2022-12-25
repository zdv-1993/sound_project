from sqlalchemy.orm import Session

from models import Track, TrackFile
from schemas import CreateTrack, CreateTrackFile


def get_track(db: Session, track_id: int):
    return db.query(Track).filter(Track.id == track_id).first()


def get_track_by_hash(db: Session, hash_val: str):
    return db.query(Track).filter(Track.hashed == hash_val).first()

def get_tracks(db: Session):
    return db.query(Track, TrackFile).join(TrackFile, Track.id == TrackFile.track_id).all()

def get_track_file(db: Session, track_file_id: str):
    return db.query(TrackFile).filter(TrackFile.id == track_file_id).first()


def create_track(db: Session, create_track: CreateTrack):
    created_data = create_track.dict()
    created_data["hashed"] = create_track.hashed
    created_track = Track(**created_data)
    db.add(created_track)
    db.commit()
    return created_track


def create_track_file(db: Session, create_track_file: CreateTrackFile):
    created_track_file = TrackFile(**create_track_file.dict())
    db.add(created_track_file)
    db.commit()
    return created_track_file


def get_track_file(db: Session, track_file_id: str):
    return db.query(TrackFile).filter(TrackFile.id == track_file_id).first()


# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()


# def create_user(db: Session, user: schemas.UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user