from sqlalchemy import create_engine
from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

engine = create_engine(
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db/{POSTGRES_DB}'
)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()
