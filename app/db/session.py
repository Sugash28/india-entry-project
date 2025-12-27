from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
# For now using sqlite for demonstration if no DB is configured
SQLALCHEMY_DATABASE_URL = "sqlite:///../sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
