FROM metabrainz/python:2.7-20220421

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV PYTHONUNBUFFERED 1

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y libmemcached-dev \
    build-essential locales git-core \
    libpq-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev \
    curl

EXPOSE 8080

WORKDIR /srv/botbot-web

COPY requirements.txt /srv/botbot-web

RUN pip install --no-cache-dir -r requirements.txt

COPY . /srv/botbot-web

CMD manage.py runserver 0.0.0.0:8080 --settings=botbot.settings

