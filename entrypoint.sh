#!/bin/bash
set -e
cmd="$@"

function postgres_ready(){
python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="$SENSORSAFRICA_DBNAME", 
                            user="$SENSORSAFRICA_DBUSER", 
                            password="$SENSORSAFRICA_DBPASS", 
                            host="$SENSORSAFRICA_DBHOST")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."
exec $cmd