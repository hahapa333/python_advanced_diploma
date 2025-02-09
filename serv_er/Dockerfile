FROM python:latest

RUN apt-get update && apt-get install -y python3-dev supervisor nginx \
    && rm -rf /var/lib/apt/lists/* && pip install psycopg2

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY ./src /app/
COPY ./dist /usr/share/nginx/html/dist
COPY . /app
# COPY ./index.html /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY supervisord.ini /etc/supervisor/conf.d/supervisord.ini



CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]