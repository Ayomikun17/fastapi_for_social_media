from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models


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


@pytest.fixture
def test_create_user(client):
    user_data = {"email": "markjj@gmail.com", "password": "134567890"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user["password"] = user_data["password"]

    assert res.status_code == 201
    return new_user


@pytest.fixture
def token(test_create_user):
    token = create_access_token({"user_id": test_create_user["id"]})
    return token


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    return client


@pytest.fixture
def test_posts(test_create_user, session):
    posts_data = [
        {
            "title": "1st title",
            "content": "1st content",
            "owner_id": test_create_user["id"],
        },
        {
            "title": "2nd title",
            "content": "2nd content",
            "owner_id": test_create_user["id"],
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_create_user["id"],
        },
        {
            "title": "4th title",
            "content": "4th content",
            "owner_id": test_create_user["id"],
        },
    ]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)

    session.add_all(posts)

    session.commit()

    posts = session.query(models.Post).all()
    return posts
