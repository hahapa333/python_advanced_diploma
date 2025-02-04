import pytest

from serv_er.server_all.src import User, db

from flask import Flask

app = Flask(__name__)

app.config["TESTING"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///twitter_test.db"
db.init_app(app)
# # папка для сохранения загруженных файлов
# UPLOAD_FOLDER = '/usr/share/nginx/html/dist'
# # расширения файлов, которые разрешено загружать
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@pytest.fixture
def test_user():
    with app.app_context():
        user = User(
        id=1,
        api_key="test",
        name="Kirill_test",)

        db.create_all()
        db.session.add(user)
        db.session.commit()
    yield app
    db.session.remove()
    # db.drop_all()