import pytest
from serv_er.backend.models import User, db as _db, Media, Likes, Twitt, Followers
from serv_er.server_all.tests.app import create_app


app_test = create_app()


@pytest.fixture
def app_():

    with app_test.app_context():
        _db.create_all()

        user = User\
        (
            api_key="test",
            name="Test"
        )

        _db.session.add(user)
        _db.session.commit()
        yield app_test
        _db.session.close()
        _db.drop_all()


@pytest.fixture
def test_add_media():

    with app_test.app_context():
        _db.create_all()
        media = Media(path="human.jpeg", id=1)
        _db.session.add(media)
        _db.session.commit()
        yield app_test
        _db.session.close()
        _db.drop_all()

@pytest.fixture
def test_add_likes_db():
    with app_test.app_context():
        _db.create_all()
        media = Likes(tweet_id=1)
        _db.session.add(media)
        _db.session.commit()
        yield app_test
        _db.session.close()
        _db.drop_all()

@pytest.fixture
def test_add_tweet_db():
    with app_test.app_context():
        _db.create_all()
        media = Twitt(
                tweet_data="DSDFSF",
                tweet_media_ids =1,
                id=2,
                author=1,)
        _db.session.add(media)
        _db.session.commit()
        yield app_test
        _db.session.close()
        _db.drop_all()

@pytest.fixture
def test_del_tweet():
    with app_test.app_context():
        _db.session.delete(1)
        _db.session.commit()
        yield app_test
        _db.session.close()
        _db.drop_all()

@pytest.fixture
def test_add_followers():
    with app_test.app_context():
        _db.create_all()
        media = Followers(
                id_followings=2,
                id_followed=1,
                following_name="Test",
                followed_name="Test",)
        _db.session.add(media)
        _db.session.commit()
        yield app_test
        _db.session.close()
        _db.drop_all()

@pytest.fixture
def client(app_):
    client = app_.test_client()
    yield client

# if __name__ == '__main__':
#     # app = create_app()
#     _app.run()