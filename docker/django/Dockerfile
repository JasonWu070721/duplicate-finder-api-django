FROM python:3.9
LABEL maintainer="jasonwu070721@gmail.com"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

WORKDIR /app

EXPOSE 8000

ENTRYPOINT [ "/bin/bash", "docker-entrypoint.sh" ]

CMD python manage.py runserver 0.0.0.0:8000
