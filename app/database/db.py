from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database_models import Base
from app.config import SQLITE_DB_PATH
from sqlalchemy import event
from sqlalchemy.engine import Engine

DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crée les tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

# Pour SQLite uniquement : activer les foreign keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 