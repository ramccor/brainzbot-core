FROM metabrainz/python:3.13-20250616 as brainzbot-base

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


FROM brainzbot-base as brainzbot-prod

# runit service files
# All services are created with a `down` file, preventing them from starting
# rc.local removes the down file for the specific service we want to run in a container
# http://smarden.org/runit/runsv.8.html

# uwsgi (website)
COPY ./docker/services/uwsgi/uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY ./docker/services/uwsgi/consul-template-uwsgi.conf /etc/consul-template-uwsgi.conf
COPY ./docker/services/uwsgi/uwsgi.service /etc/service/uwsgi/run
RUN touch /etc/service/uwsgi/down

# plugins
COPY ./docker/services/plugins/consul-template-plugins.conf /etc/consul-template-plugins.conf
COPY ./docker/services/plugins/plugins.service /etc/service/plugins/run
RUN touch /etc/service/plugins/down

COPY ./docker/rc.local /etc/rc.local


FROM brainzbot-base as brainzbot-dev

CMD manage.py runserver 0.0.0.0:8080 --settings=botbot.settings
