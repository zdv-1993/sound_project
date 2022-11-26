
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from os import environ


engine = create_engine(f"postgresql+psycopg2://{environ['POSTGRES_USER']}:{environ['POSTGRES_PASSWORD']}@{environ['POSTGRES_HOST']}:{environ['POSTGRES_PORT']}/{environ['POSTGRES_DB']}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

