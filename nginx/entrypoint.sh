#!/bin/sh

if [ -z "$NGINX_CONF" ]; then
  CONF_TYPE="http"
else
  CONF_TYPE="$NGINX_CONF"
fi

echo "Using $CONF_TYPE configuration"

cp "/etc/nginx/conf.d/app.${CONF_TYPE}.conf" /etc/nginx/conf.d/default.conf

# Start Nginx and reload periodically
nginx -g "daemon off;" &
pid=$!

while :; do
  sleep 6h
  nginx -s reload
done &

wait $pid
