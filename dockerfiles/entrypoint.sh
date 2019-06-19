#!/bin/bash
set -e
if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    /usr/bin/python3.4 manage.py makemigrations --noinput
    /usr/bin/python3.4 manage.py migrate --noinput
fi

if [ "x$DJANGO_MANAGEPY_COLLECTSTATIC" = 'xon' ]; then
	/usr/bin/python3.4 manage.py collectstatic --noinput
fi


python /app/BEacon/manage.py migrate --fake
supervisord -n -c /app/BEacon/dockerfiles/supervisor-app.conf

exec "$@"
