from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base


# Setting up test database
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    # Before the test runs, drop the tables in the database
    Base.metadata.drop_all(bind=engine)
    # After the test runs, create the tables in the database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def ovveride_get_db():

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = ovveride_get_db
    yield TestClient(app)
