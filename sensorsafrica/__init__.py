# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# from .celeryapp import app as celery_app

# __all__ = ['celery_app']

    # data = json.loads(event['body'])

    # node_uid = headers["HTTP_X_SENSOR"] or headers["HTTP_SENSOR"] or headers["HTTP_NODE"]
    # node_pin = headers["HTTP_X_PIN"] or headers["HTTP_PIN"] or '-'

    # values = data.pop('sensordatavalues', [])