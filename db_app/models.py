from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from os import environ


class Base(DeclarativeBase):
    pass


class Track(Base):
    __tablename__ = "tracks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(127))
    artist_name: Mapped[str] = mapped_column(String(127))
    hashed: Mapped[Optional[str]] = mapped_column(String(31))
    data: Mapped[dict] = mapped_column(JSONB)
    def __repr__(self) -> str:
        return self.title


class TrackFile(Base):
    __tablename__ = "files"
    id: Mapped[str] = mapped_column(String(127), primary_key=True)
    info: Mapped[dict] = mapped_column(JSONB)
    track: Mapped["Track"] = relationship(
        # back_populates="files"
        )
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"))
