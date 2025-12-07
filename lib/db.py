from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lib.models import Base

# Create SQLite database
engine = create_engine('sqlite:///pennypilote.db')
Session = sessionmaker(bind=engine)
session = Session()

def init_db():
    Base.metadata.create_all(engine)