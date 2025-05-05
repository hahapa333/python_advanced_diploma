import os

from flask import Flask, jsonify, request, Blueprint
from werkzeug.utils import secure_filename

from models import Followers, Likes, Media, Twitt, User, db

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

MEDIA_FOLDER = os.path.join(os.getcwd(), "dist")
os.makedirs(MEDIA_FOLDER, exist_ok=True)  # создаёт папку, если нет


@api_blueprint.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'})


@api_blueprint.route("/users/me", methods=["GET"])
def get_client():
    try:
        http_key = request.headers.get("api-key")
        if not http_key:
            return jsonify({"result": "false", "error": "Missing API key"}), 400

        user = db.session.query(User).filter_by(api_key=http_key).first()
        if not user:
            return jsonify({"result": "false", "error": "Invalid API key"}), 403

        # Получаем подписчиков (те, кто подписаны на user)
        followers = db.session.query(Followers).filter_by(id_followings=user.id).all()
        followers_data = [
            {"id": f.id_followed, "name": f.followed_name} for f in followers
        ]

        # Получаем подписки (на кого подписан user)
        following = db.session.query(Followers).filter_by(id_followed=user.id).all()
        following_data = [
            {"id": f.id_followings, "name": f.following_name} for f in following
        ]

        return jsonify({
            "result": "true",
            "user": {
                "id": user.id,
                "name": user.name,
                "followers": followers_data,
                "following": following_data
            }
        })

    except Exception as e:
        return jsonify({
            "result": "false",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }), 500


"""добавляем пользователя"""


@api_blueprint.route("/user_add", methods=["POST"])
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


@api_blueprint.route("/medias", methods=["POST"])
def upload_media():
    try:
        api_key = request.headers.get("api-key")
        user = db.session.query(User).filter_by(api_key=api_key).first()
        if not user:
            return jsonify({
                "result": False,
                "error_type": "AuthError",
                "error_message": "Invalid API key"
            }), 403

        if "file" not in request.files:
            return jsonify({
                "result": False,
                "error_type": "ValidationError",
                "error_message": "Missing media file in form-data"
            }), 400

        media_file = request.files["file"]
        if media_file.filename == "":
            return jsonify({
                "result": False,
                "error_type": "ValidationError",
                "error_message": "Empty filename"
            }), 400

        filename = secure_filename(media_file.filename)
        file_path = os.path.join(MEDIA_FOLDER, filename)
        media_file.save(file_path)

        new_media = Media(
            tweet_id=None,  # Пока не привязан к твиту
            media_type="image",  # можно сделать динамическим по расширению
            media_url=f"/dist/{filename}"
        )
        db.session.add(new_media)
        db.session.commit()

        return jsonify({
            "result": True,
            "media_id": new_media.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "result": False,
            "error_type": str(type(e).__name__),
            "error_message": str(e)
        }), 500


"""создать твит """


@api_blueprint.route("/tweets", methods=["POST"])
def create_tweet():
    try:
        http_key = request.headers.get("api-key")
        user = db.session.query(User).filter_by(api_key=http_key).first()
        if not user:
            return jsonify({"result": False, "error": "Invalid API key"}), 403

        data = request.get_json()
        tweet_data = data.get("tweet_data")
        media_ids = data.get("tweet_media_ids", [])

        if not tweet_data:
            return jsonify({"result": False, "error": "Missing tweet_data"}), 400

        # Создание твита
        new_twitt = Twitt(tweet_data=tweet_data, user_id=user.id)
        db.session.add(new_twitt)
        db.session.flush()  # Получаем ID до коммита

        # Привязка медиа, если есть
        for media_id in media_ids:
            media = db.session.get(Media, media_id)
            if media:
                media.tweet_id = new_twitt.id

        db.session.commit()
        return jsonify({"result": True, "tweet_id": new_twitt.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "result": False,
            "error_type": str(type(e).__name__),
            "error_message": str(e)
        }), 500


"""получить твиты всех пользователей"""


@api_blueprint.route("/tweets", methods=["GET"])
def get_tweets():
    try:
        http_key = request.headers.get("api-key")
        user = db.session.query(User).filter_by(api_key=http_key).first()
        if not user:
            return jsonify({"result": False, "error_type": "AuthError", "error_message": "Invalid API key"}), 403

        tweets = db.session.query(Twitt).order_by(Twitt.id.desc()).all()

        tweets_list = []
        for tweet in tweets:
            # Медиафайлы
            attachments = [media.media_url for media in tweet.media]

            # Автор
            author = {
                "id": tweet.author.id,
                "name": tweet.author.name
            }

            # Лайки
            likes_query = db.session.query(Likes).filter_by(tweet_id=tweet.id).all()
            likes = []
            for like in likes_query:
                liked_user = db.session.query(User).get(like.user_id)
                if liked_user:
                    likes.append({
                        "user_id": liked_user.id,
                        "name": liked_user.name
                    })

            tweets_list.append({
                "id": tweet.id,
                "content": tweet.tweet_data,
                "attachments": attachments,
                "author": author,
                "likes": likes
            })

        return jsonify({
            "result": True,
            "tweets": tweets_list
        }), 200

    except Exception as e:
        return jsonify({
            "result": False,
            "error_type": str(type(e).__name__),
            "error_message": str(e)
        }), 500


"""удалить твит"""


@api_blueprint.route("/tweets/<int:id>", methods=["DELETE"])
def del_twit(id):
    try:
        twitt = db.session.query(Twitt).filter_by(id=id).first()
        if not twitt:
            return jsonify({"result": "false", "error": "Tweet not found"}), 404

        # Удаляем медиа и лайки, если это нужно каскадно
        db.session.query(Media).filter_by(tweet_id=id).delete()
        db.session.query(Likes).filter_by(tweet_id=id).delete()

        db.session.delete(twitt)
        db.session.commit()
        return jsonify({"result": "true"})
    except Exception as e:
        return {"result": "false", "error_type": type(e).__name__, "error_message": str(e)}, 500


"""подписаться на пользователя """


@api_blueprint.route("/users/<int:id>/follow", methods=["POST"])
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


@api_blueprint.route("/users/<int:id>/follow", methods=["DELETE"])
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


@api_blueprint.route("/users/<int:id>", methods=["GET"])
def users_id(id):
    try:
        user = db.session.query(User).get(id)
        if not user:
            return {"result": "false", "error": "User not found"}, 404

        followers = db.session.query(Followers).filter_by(id_followings=id).all()
        following = db.session.query(Followers).filter_by(id_followed=id).all()

        followers_data = [{"id": f.id_followed, "name": f.followed_name} for f in followers]
        following_data = [{"id": f.id_followings, "name": f.following_name} for f in following]

        return {
            "result": "true",
            "user": {
                "id": user.id,
                "name": user.name,
                "followers": followers_data,
                "following": following_data
            }
        }
    except Exception as e:
        return {"result": "false", "error_type": type(e).__name__, "error_message": str(e)}, 500


"""ставим лайк"""


@api_blueprint.route("/tweets/<int:tweet_id>/likes", methods=["POST"])
def like_tweet(tweet_id):
    try:
        api_key = request.headers.get("api-key")
        user = db.session.query(User).filter_by(api_key=api_key).first()
        if not user:
            return jsonify({"result": False, "error_type": "AuthError", "error_message": "Invalid API key"}), 403

        tweet = db.session.get(Twitt, tweet_id)
        if not tweet:
            return jsonify({"result": False, "error_type": "NotFound", "error_message": "Tweet not found"}), 404

        # Проверим, существует ли уже лайк
        existing_like = db.session.query(Likes).filter_by(user_id=user.id, tweet_id=tweet_id).first()
        if existing_like:
            return jsonify({"result": True})  # Уже лайкнуто — ничего не делаем

        like = Likes(user_id=user.id, tweet_id=tweet_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({"result": True}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "result": False,
            "error_type": str(type(e).__name__),
            "error_message": str(e)
        }), 500


@api_blueprint.route("/tweets/<int:tweet_id>/likes", methods=["DELETE"])
def unlike_tweet(tweet_id):
    try:
        api_key = request.headers.get("api-key")
        user = db.session.query(User).filter_by(api_key=api_key).first()
        if not user:
            return jsonify({"result": False, "error_type": "AuthError", "error_message": "Invalid API key"}), 403

        like = db.session.query(Likes).filter_by(user_id=user.id, tweet_id=tweet_id).first()
        if not like:
            return jsonify({"result": True})  # Уже не лайкнуто

        db.session.delete(like)
        db.session.commit()
        return jsonify({"result": True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "result": False,
            "error_type": str(type(e).__name__),
            "error_message": str(e)
        }), 500
