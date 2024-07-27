from app import schemas
import pytest


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    def validate(post):
        return schemas.PostOut(**post)

    post_map = map(validate, res.json())
    posts_list = list(post_map)

    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200


def test_unauthorized_user_get_all_post(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthorized_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/467")
    assert res.status_code == 404


def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json())
    assert post.post.id == test_posts[0].id
    assert post.post.content == test_posts[0].content
    assert post.post.title == test_posts[0].title


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("Anime of the year", "announcement drops soon", True),
        ("Action movie of the year", "announcement drops soon", False),
        ("Anime of the year 34", "announcement drops soon", True),
    ],
)
def test_create_post(
    authorized_client, test_create_user, test_posts, title, content, published
):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published}
    )

    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_create_user["id"]


def create_post_default_published_true(authorized_client, test_create_user, test_posts):
    res = authorized_client.post(
        "/posts/", json={"title": "ajnkjvk", "content": "bbbdvd"}
    )

    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == "ajnkjvk"
    assert created_post.content == "bbbdvd"
    assert created_post.published == True
    assert created_post.owner_id == test_create_user["id"]


def test_unauthorized_user_create_post(client, test_create_user, test_posts):
    res = client.post("/posts/", json={"title": "ajnkjvk", "content": "bbbdvd"})
    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_create_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_delete_post_success(authorized_client, test_create_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204


def delete_post_not_exist(authorized_client, test_create_user):
    res = authorized_client.delete(f"/posts/75777777775")
    assert res.status_code == 404

def delete_other_user_post(authorized_client, test_create_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403