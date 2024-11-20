FROM python:3.9-slim

COPY requirements.txt requirements.txt
COPY firebase_authentication-0.0.1.tar.gz firebase_authentication-0.0.1.tar.gz
RUN pip install -U pip && pip install -r requirements.txt
RUN pip install firebase_authentication-0.0.1.tar.gz

COPY ./bin /app/bin
COPY app.py /app/app.py
COPY wsgi.py /app/wsgi.py
COPY config.py /app/config.py

WORKDIR /app

RUN useradd lingo
USER lingo

EXPOSE 8050

ENTRYPOINT ["bash", "/app/bin/run.sh"]