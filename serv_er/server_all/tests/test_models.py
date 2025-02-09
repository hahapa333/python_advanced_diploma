import json


def test_create_user(client) -> None:
    user_data = {"api_key": "test", "name": "Kirill_test",}
    resp = client.post("/user_add", data=user_data)

    assert resp.status_code == 200

def test_media_db(client) -> None:

    media_data = {"id": 1, "path": "human.jpeg" }
    resp = client.post("/api/medias", data=media_data)
    assert resp.status_code == 200

def test_create_twit(client) -> None:

        twit_data = {"tweet_data": "DSDFSF",
                 "tweet_media_ids": 1,
                 }
        resp = client.post("/api/tweets/", json=twit_data)
        assert resp.status_code == 200

def test_get_twit(client) -> None:
    resp = client.get("api/tweets/")
    assert resp.json["result"] == "true"

def test_del_twit(client) -> None:

    resp = client.delete(f"/api/tweets/{1}")

    assert resp.status_code == 200


def test_user(client) -> None:
    resp = client.get("/users/1")
    assert resp.status_code == 200
    assert resp.json == {"result": "true", "user":{"id": 1, "name": "Kirill_test"}  }


def test_user_get_all(client) -> None:
    resp = client.get("/api/users/me/")
    assert resp.status_code == 200
    assert resp.json == {"result": "true",
                         "user": {
                             "id": 1,
                             "name": "Kirill_test",
                             "followers": [],
                             "following": []
                         }}


def test_like(client) -> None:

    resp = client.post(f"/api/tweets/{1}/likes")
    assert resp.status_code == 200

def test_del_like(client) -> None:
    # del_data = {"id": 1}
    resp = client.delete(f"/api/tweets/{1}/likes")

    assert resp.status_code == 200

def test_followers(client) -> None:
    resp = client.post(f"/api/users/{1}/follow")
    assert resp.status_code == 200

def test_del_followers(client) -> None:
    resp = client.delete(f"/api/users/{1}/follow")
    assert resp.status_code == 200


