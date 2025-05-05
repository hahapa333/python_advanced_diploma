from flask import Flask
from routes import api_blueprint  # Убедитесь, что это имя соответствует Blueprint в routes.py
from models import db
import os
import time
import psycopg2
from psycopg2 import OperationalError


# Ждём PostgreSQL перед запуском
def wait_for_db(host, port, user, password, db_name, timeout=30):
    start_time = time.time()
    while True:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=db_name
            )
            conn.close()
            print("✅ Database is ready.")
            break
        except OperationalError:
            if time.time() - start_time > timeout:
                raise RuntimeError("❌ Database not responding in time.")
            print("⏳ Waiting for database...")
            time.sleep(2)


wait_for_db("db", 5432, "postgres", "postgres", "twitter_db")

app = Flask(__name__, static_folder="dist", static_url_path="/dist")

app.config['UPLOAD_FOLDER'] = 'app/dist'
# Конфигурация базы данных (пример с PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@db:5432/twitter_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# Регистрация Blueprint'а
app.register_blueprint(api_blueprint, url_prefix="/api")

from flask import send_from_directory


# Отдаёт index.html для всех маршрутов, кроме /api и /dist
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_vue_app(path):
    if path.startswith("api") or path.startswith("dist"):
        return "Not Found", 404  # или ничего не делать — они уже обрабатываются
    return send_from_directory(app.static_folder, "index.html")


# раздача медиа
@app.route('/dist/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
