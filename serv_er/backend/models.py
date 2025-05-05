from typing import Any, Dict

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Followers(db.Model):
    __tablename__ = "followers"
    id = db.Column(db.Integer, primary_key=True)
    id_followings = db.Column(db.Integer, nullable=False)
    id_followed = db.Column(db.Integer, nullable=False)
    following_name = db.Column(db.String(200), nullable=False)
    followed_name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"подписчики {self.id_following}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Twitt(db.Model):
    __tablename__ = "twitts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    tweet_data = db.Column(db.String(50), nullable=False)

    media = db.relationship("Media", backref="twitt")

    def __repr__(self):
        return f"новый твит {self.tweet_data}"


class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.Integer, db.ForeignKey("twitts.id"))
    media_type = db.Column(db.String(10))
    media_url = db.Column(db.String(200))

    def __repr__(self):
        return f"{self.media_url} {self.id}"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    twit_table = db.relationship("Twitt", backref="author", lazy="dynamic")

    def __repr__(self):
        return f"{self.name} {self.id} {self.api_key}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Likes(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tweet_id = db.Column(db.Integer, db.ForeignKey("twitts.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "tweet_id", name="_user_tweet_uc"),
    )

    def __repr__(self):
        return f"User {self.user_id} liked Tweet {self.tweet_id}"
