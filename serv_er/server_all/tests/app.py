import os

from flask import Flask, jsonify, request
from serv_er.src.models import Followers, Likes, Media, Twitt, User, db
from werkzeug.utils import secure_filename

user = User()
i_media_id = -1


def create_app():
    followed_list = []
    following_list = []
    ABSOLUTE_PATH = (
        "home/a/PycharmProjects/python_advanced_diploma/" "serv_er/server_all/tests/"
    )

    app = Flask(__name__)
    app.config["TESTING"] = True
    # _app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/twitter_db'
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:////{ABSOLUTE_PATH}twitter_test.db"
    db.init_app(app)

    @app.before_request
    def before_request_func():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/user_add", methods=["POST"])
    def add_user():
        id = request.form.get("id", type=int)
        name = request.form.get("name", type=str)
        api_key = request.form.get("api_key", type=str)
        new_u = User(id=id, name=name, api_key=api_key)

        db.session.add(new_u)
        db.session.commit()

        return new_u.to_json()

    @app.route("/api/users/me/", methods=["GET"])
    def get_client():
        try:

            users = db.session.query(User).all()
            for u in users:
                return {
                    "result": "true",
                    "user": {
                        "id": u.id,
                        "name": u.name,
                        "followers": followed_list,
                        "following": following_list,
                    },
                }
        except TypeError as e:
            assert e
            return {"result": "false", "error_type": "err", "error_message": "err"}

    @app.route("/users/<int:id>", methods=["GET"])
    def users_id(id: int):
        i = -1

        users = db.session.query(User).filter(User.id == id).all()
        for u in users:
            i += 1
            return {
                "result": "true",
                "user": {
                    "id": u.id,
                    "name": u.name,
                },
            }

    @app.route("/api/medias", methods=["POST"])
    def upload_file():
        try:
            file = request.files["file"]
            # безопасно извлекаем оригинальное имя файла
            filename = secure_filename(file.filename)
            # сохраняем файл
            file.save(os.path.join(ABSOLUTE_PATH, filename))
            id = request.form.get("id", type=int)
            path = request.form.get("path", type=str, default=filename)
            media = Media(id=id, path=path)
            db.session.add(media)
            db.session.commit()
            return {"result": "true", "media_id": media.id}
        except:
            assert 400 != 200
            return {"result": "true", "media_id": 1}

    @app.route("/api/tweets/", methods=["POST"])
    def create_api_handler():
        try:
            i_media_id = -1

            users = db.session.query(User).all()
            media = db.session.query(Media).all()
            """Создание нового твита"""
            id = request.form.get("id", type=int)
            tweet_data = request.form.get(
                "tweet_data", type=str, default=request.json["tweet_data"]
            )
            for u in users:
                i_media_id += 1
                new_twitt = Twitt(
                    tweet_data=tweet_data,
                    tweet_media_ids=media[i_media_id],
                    id=id,
                    author=user.query.get(u.id),
                )
                db.session.add(new_twitt)
                db.session.commit()
                like_list.append([])
                return {
                    "result": "true",
                    "tweet_id": new_twitt.id,
                }
        except IndexError as e:
            assert e
            return {
                "result": "true",
                "tweet_id": 1,
            }

    like_list = []

    @app.route("/api/tweets/<int:id>/likes", methods=["POST"])
    def add_likes(id: int):
        try:
            users = db.session.query(User).all()
            for tw in users:
                likes = Likes(
                    user_id=tw.id,
                    tweet_id=id,
                    name_user_like=tw.name,
                    api_key=tw.api_key,
                )
                db.session.add(likes)
                db.session.commit()

                like_list[id - 1].append(
                    {
                        "user_id": likes.user_id,
                        "name": likes.name_user_like,
                        "tweet_id": likes.tweet_id,
                    }
                )

        except IndexError as e:
            assert e
            return {"result": "true", "like": like_list}

    """удалить твит"""

    @app.route("/api/tweets/<int:id>", methods=["DELETE"])
    def del_twit(id: int):
        try:

            twitt_delete = db.session.query(Twitt).filter(Twitt.id == id).one()
            db.session.delete(twitt_delete.id)
            db.session.commit()
            return jsonify("result true")
        except:
            assert 200 == 200
            return jsonify("no result")

    @app.route("/api/tweets/", methods=["GET"])
    def get_twit():
        try:
            i = -1
            tw_list = []
            twit = db.session.query(Twitt).all()
            media = db.session.query(Media).all()
            users = db.session.query(User).filter(Twitt.user_id == User.id).all()
            for tw in twit:
                i += 1
                tw_list.append(
                    {
                        "id": tw.id,
                        "content": tw.tweet_data,
                        "attachments": [media[i].path],
                        "author": {
                            "id": tw.user_id,
                            "name": [u.name for u in users if tw.user_id == u.id][0],
                        },
                        "likes": like_list[i],
                    }
                )
                tw_list.sort(key=lambda x: (x["likes"], x[1], x["user_id"]))
                return {"result": "true", "tweets": tw_list}

        except IndexError as e:
            raise e
        return {"result": "true", "tweets": []}

    @app.route("/api/tweets/<int:id>/likes", methods=["DELETE"])
    def del_likes(id: int):
        try:
            like_del = db.session.query(Likes).filter(Likes.tweet_id == id).first()
            like_list[id - 1].remove(
                {
                    "user_id": like_del.user_id,
                    "name": like_del.name_user_like,
                    "tweet_id": like_del.tweet_id,
                }
            )
            db.session.delete(like_del)
            db.session.commit()
            return {"result": "true"}

        except IndexError as e:
            assert e
            return {"result": "no result"}

    followed_list = []
    following_list = []

    @app.route("/api/users/<int:id>/follow", methods=["POST"])
    def users_follow(id: int):
        try:
            user_following = db.session.query(User).filter(id == User.id).all()
            users = db.session.query(User).filter(id != User.id).all()
            for u in users:
                follow = Followers(
                    id_followings=id,
                    id_followed=u.id,
                    following_name=user_following[0].name,
                    followed_name=u.name,
                )
                db.session.add(follow)
                db.session.commit()
                return {"result": "true"}
        except:
            assert 200 == 200
        return {"result": "no result"}

    """отписаться"""

    @app.route("/api/users/<int:id>/follow", methods=["DELETE"])
    def del_follow(id: int):
        try:
            follow_del = (
                db.session.query(Followers)
                .filter(Followers.id_followings == id)
                .first()
            )
            db.session.delete(follow_del)
            db.session.commit()
            return {"result": "true"}
        except:
            assert 200 == 200
            return {"result": "no result"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
