import jwt
from app import schemas
from app.config import settings


def test_root(client):
    res = client.get("/")
    print(res.json().get("message"))
    assert res.json().get("message") == "Hello World"
    assert res.status_code == 200


def test_login_user(client, test_create_user):
    res = client.post(
        "/login",
        data={
            "username": test_create_user["email"],
            "password": test_create_user["password"],
        },
    )
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(
        login_res.access_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    id = str(payload.get("user_id"))

    assert id == str(test_create_user["id"])
    assert login_res.token_type == "bearer"
    assert res.status_code == 200
