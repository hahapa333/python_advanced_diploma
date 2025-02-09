from typing import List, Dict, Any
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
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}

class Twitt(db.Model):
    __tablename__ = 'twitts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tweet_data = db.Column(db.String(50), nullable=False)
    tweet_media_id = db.Column(db.Integer, db.ForeignKey('media.id'))


    def __repr__(self):
        return f"новый твит {self.tweet_data}"



    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    twit_table = db.relationship("Twitt", backref="author", lazy="dynamic")


    def __repr__(self):
        return f"{self.name} {self.id} {self.api_key}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}



class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), nullable=False)
    tweet_id = db.relationship("Twitt", backref="tweet_media_ids", lazy="dynamic")


    def __repr__(self):
        return f"{self.path} {self.id}"

class Likes(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer)
    tweet_id = db.Column(db.Integer)
    name_user_like = db.Column(db.String(50))


    def __repr__(self):
        return f"{self.count_like}"

