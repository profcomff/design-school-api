FROM python:3.10
WORKDIR /app
RUN mkdir -p static

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

ADD gunicorn_conf.py alembic.ini /app/
ADD migrations /app/migrations
ADD design_bot /app/design_bot

CMD [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "/app/gunicorn_conf.py" ,"design_bot.routes.base:app" ]
