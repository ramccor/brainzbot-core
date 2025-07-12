ARG PYTHON_BASE_IMAGE_VERSION=3.13-20250616
FROM metabrainz/python:$PYTHON_BASE_IMAGE_VERSION AS brainzbot-base

LABEL org.label-schema.vcs-url="https://github.com/metabrainz/brainzbot-core.git" \
      org.label-schema.vcs-ref="" \
      org.label-schema.schema-version="1.0.0-rc1" \
      org.label-schema.vendor="MetaBrainz Foundation" \
      org.label-schema.name="MetaBrainz" \
      org.metabrainz.based-on-image="metabrainz/python:$PYTHON_BASE_IMAGE_VERSION"

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y build-essential

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

ARG GIT_COMMIT_SHA
LABEL org.label-schema.vcs-ref=$GIT_COMMIT_SHA
ENV GIT_SHA ${GIT_COMMIT_SHA}

FROM brainzbot-base as brainzbot-dev

CMD manage.py runserver 0.0.0.0:8080 --settings=botbot.settings
