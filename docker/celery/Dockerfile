FROM python:3.9
LABEL maintainer="jasonwu070721@gmail.com"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

WORKDIR /app

ENV PATH=/node/bin:$PATH
ENTRYPOINT [ "/bin/bash", "docker-entrypoint.sh" ]

CMD celery -A config worker -l info
