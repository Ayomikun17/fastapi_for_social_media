import pytest
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


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@gmail.com", "password123", 403),
        ("jack@gmail.com", "wrongpassword", 403),
        ("wrongemail@gmail.com", "wrongpassword", 403),
        (None, "password123", 422),
        ("jack@gmail.com", None, 422)
    ]
)
def test_incorrect_login(test_create_user, client, email, password, status_code):
    res = client.post(
        "/login",
        data={"username": email, "password": password, },
    )

    assert res.status_code == status_code
    # assert res.json().get("detail") == "Invalid Credentials"
