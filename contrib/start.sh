#!/bin/sh
python manage.py migrate --noinput                # Apply database migrations
python manage.py collectstatic --clear --noinput  # Collect static files

# recreate the cached static json files
python manage.py cache_static_json_data --interval 5m
python manage.py cache_static_json_data --interval 1h
python manage.py cache_static_json_data --interval 24h

# Prepare log files and start outputting logs to stdout
touch /src/logs/celery.log
touch /src/logs/gunicorn.log
touch /src/logs/access.log
tail -n 0 -f /src/logs/*.log &

#purge all configured task queues
celery -A sensorsafrica purge
celery -A sensorsafrica beat -l info &> /src/logs/celery.log  &
celery -A sensorsafrica worker --hostname=$DOKKU_APP_NAME -l info &> /src/logs/celery.log  &
celery -A sensorsafrica flower --basic_auth=$SENSORSAFRICA_FLOWER_ADMIN_USERNAME:$SENSORSAFRICA_FLOWER_ADMIN_PASSWORD &> /src/logs/celery.log  &

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class gevent \
    --log-level=info \
    --log-file=/src/logs/gunicorn.log \
    --access-logfile=/src/logs/access.log \
    --name sensorsafrica --reload sensorsafrica.wsgi:application \
    --chdir sensorsafrica/
