import os

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

from models import Followers, Likes, Media, Twitt, User, db

app = Flask(__name__, static_url_path="/dist", static_folder="/usr/share/nginx/html")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://postgres:postgres@db:5432/twitter_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
# папка для сохранения загруженных файлов
UPLOAD_FOLDER = "/usr/share/nginx/html/dist"
# расширения файлов, которые разрешено загружать
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
user = User()
i_media_id = -1


@app.before_request
def before_request_func():
    db.create_all()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

    """получить клиента"""


@app.route("/api/users/me/", methods=["GET"])
def get_client():
    try:
        http_key = request.headers.get("api-key")
        users = db.session.query(User).filter(http_key == User.api_key).all()
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
    except IndexError as e:
        assert e
        return {
            "result": "false",
            "error_type": e,
            "error_message": e
        }


"""добавляем пользователя"""


@app.route("/user_add", methods=["POST"])
def add_user():
    try:
        id = request.form.get("id", type=int)
        name = request.form.get("name", type=str)
        api_key = request.form.get("api_key", type=str)
        new_u = User(id=id, name=name, api_key=api_key)
        db.session.add(new_u)
        db.session.commit()
        return new_u.to_json()
    except TypeError as e:
        assert e
        return {
            "result": "false",
            "error_type": e,
            "error_message": e
        }


"""загружаем файлы"""


@app.route("/api/medias", methods=["POST"])
def upload_file():
    try:
        file = request.files["file"]
        # безопасно извлекаем оригинальное имя файла
        filename = secure_filename(file.filename)
        # сохраняем файл
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        id = request.form.get("id", type=int)
        path = request.form.get("path", type=str, default=filename)
        media = Media(id=id, path=path)
        db.session.add(media)
        db.session.commit()
        return {"result": "true", "media_id": media.id}
    except TypeError as e:
        assert e
        return {
            "result": "false",
            "error_type": f"{e}",
            "error_message": f"{e}"
        }


"""создать твит """


@app.route("/api/tweets/", methods=["POST"])
def create_api_handler():
    try:
        global i_media_id
        http_key = request.headers.get("api-key")
        users = db.session.query(User).filter(http_key == User.api_key).all()
        media = db.session.query(Media).all()
        tweet = db.session.query(Twitt).all()
        if len(media) <= len(tweet):
            medias = Media(path="")
            db.session.add(medias)
            db.session.commit()

            """Создание нового твита"""
            id = request.form.get("id", type=int)
            tweet_data = request.form.get(
                "tweet_data", type=str, default=request.json["tweet_data"]
            )
            for u in users:
                i_media_id += 1
                new_twitt = Twitt(
                    tweet_data=tweet_data,
                    tweet_media_ids=medias,
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
        else:
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
        return {"result": "false", "error_type": f"{e}", "error_message": "error index"}


"""удалить твит"""


@app.route("/api/tweets/<int:id>", methods=["DELETE"])
def del_twit(id: int):
    try:
        global i_media_id
        i_media_id -= 1
        twitt_delete = db.session.query(Twitt).filter(Twitt.id == id).one()
        db.session.delete(twitt_delete)
        db.session.commit()
        return jsonify("result true")
    except IndexError as e:
        assert e
        return {"result": "false", "error_type": f"{e}", "error_message": "error index"}


"""получить твиты всех пользователей"""


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

        return {"result": "true", "tweets": tw_list}
    except (IndexError, KeyError) as e:
        assert e
        return {"result": "false", "error_type": f"{e}", "error_message": "error index"}


"""подписаться на пользователя """

followed_list = []
following_list = []


@app.route("/api/users/<int:id>/follow", methods=["POST"])
def users_follow(id: int):
    try:
        http_key = request.headers.get("api-key")
        user_following = db.session.query(User).filter(id == User.id).all()
        users = (
            db.session.query(User)
            .filter(id != User.id)
            .filter(http_key == User.api_key)
            .all()
        )
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
    except IndexError as e:
        assert e
        return {"result": "false", "error_type": f"{e}", "error_message": "error index"}


"""отписаться"""


@app.route("/api/users/<int:id>/follow", methods=["DELETE"])
def del_follow(id: int):
    try:
        follow_del = (
            db.session.query(Followers).filter(Followers.id_followings == id).first()
        )
        db.session.delete(follow_del)
        db.session.commit()
        return {"result": "true"}
    except IndexError as e:
        assert e
        return {"result": "false", "error_type": f"{e}", "error_message": "error index"}


"""получить клиента по его id"""


@app.route("/api/users/<int:id>", methods=["GET"])
def users_id(id: int):
    try:
        i = -1
        followed_list.clear()
        following_list.clear()
        users = db.session.query(User).filter(User.id == id).all()
        foll = db.session.query(Followers).all()
        for fl in foll:
            if fl.id_followed == id:
                following_list.append({"id": fl.id_followings, "name": fl.following_name})
            elif fl.id_followings == id:
                followed_list.append({"id": fl.id_followed, "name": fl.followed_name})
        for u in users:
            i += 1
            return {
                "result": "true",
                "user": {
                    "id": u.id,
                    "name": u.name,
                    "followers": followed_list,
                    "following": following_list,
                },
            }
    except IndexError as e:
        assert e
        return {"result": "false", "error_type": f"{e}", "error_message": "error index"}


"""ставим лайк"""

like_list = []


@app.route("/api/tweets/<int:id>/likes", methods=["POST"])
def add_likes(id: int):
    try:
        http_key = request.headers.get("api-key")
        users = db.session.query(User).filter(User.api_key == http_key).all()
        for tw in users:
            likes = Likes(
                user_id=tw.id, tweet_id=id, name_user_like=tw.name, api_key=tw.api_key
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

        return {"result": "true", "like": like_list}
    except (IndexError, TypeError) as e:
        assert e
        return {"result": "false", "error_type": f"{e}", "error_message": "error index"}


"""Удаляем лайк"""


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
        return {"result": "false", "error_type": f"{e}", "error_message": "error index"}
