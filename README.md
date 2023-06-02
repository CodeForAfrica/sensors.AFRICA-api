# sensors.AFRICA API

API to save and access data from deployed sensors in cities all around Africa.

## Documentation

The API is documented [here.](https://github.com/CodeForAfricaLabs/sensors.AFRICA-api/wiki/API-Documentation) 

## Development

Gitignore is standardized for this project using [gitignore.io](https://www.gitignore.io/) to support various development platforms.
To get the project up and running:

- Clone this repo
- 
### Prerequisites
  
  - Have [PostgreSQL](https://www.postgresql.org/download/) installed 
  - Have **psql** installed - a command line tool to interact with PostgreSQL. To install, follow instructions as shown [here](https://www.timescale.com/blog/how-to-install-psql-on-mac-ubuntu-debian-windows/).
  - Have a Python version 3.9.7 installed in your system. If you are using a different Python version you could use a   tool like [Pyenv](https://github.com/pyenv/pyenv) to manage different versions  
### Virtual environment
  
- Use virtualenv to create your virtual environment; `python -m venv venv` or `virtualenv venv`
- Activate the virtual environment; `source venv/bin/activate`
- ~~Install feinstaub; `pip install git+https://github.com/opendata-stuttgart/feinstaub-api`~~ issues detected. Feinstaub sensors app manually include in project directory 
- ~~Install the requirements; `pip install .`~~ Dependency hell with older conflicting module versions.
- Run the below commands in the virtual environment to install depencencies. Note : latest versions will be installed
```bash

pip install —upgrade pip
pip install —upgrade setuptools

pip install django django-cors-headers django-filter djangorestframework coreapi celery celery_slack python-dateutil timeago psycopg2-binary dj_database_url sentry_sdk django_extensions whitenoise

```

### Database setup
- Create a sensorsafrica database open your terminal and hit `psql postgres`, then run following sql script:

```sql
CREATE DATABASE sensorsafrica;
CREATE USER sensorsafrica WITH ENCRYPTED PASSWORD 'sensorsafrica';
GRANT ALL PRIVILEGES ON DATABASE sensorsafrica TO sensorsafrica;
```
### Running the app

Still in your virtual enviroment, run the following:

- Migrate the database; `python manage.py migrate`
- Run the server; `python manage.py runserver`


---

### Docker

Using docker compose:

- Build the project; `docker-compose build` or `make build`
- Run the project; `docker-compose up -d` or `make up`

Docker compose make commands:

- `make build`
- `make up` - run docker and detach
- `make log` - tail logs
- `make test` - run test
- `make migrate` - migrate database
- `make createsuperuser` - create a super user for admin
- `make compilescss`
- `make enter` - enter docker shell
- `make django` - enter docker django shell

**NOTE:**
`docker-compose` is strictly for development and testing purposes.
The Dockerfile is written for production since dokku is being used and it will look for Dockerfile.

### Tests

- Virtual Environment; `pytest --pylama`
- Docker; `docker-compose run api pytest --pylama`

**NOTE:**
If entrypoint and start scripts are changed, make sure they have correct/required permissions since we don't grant permissions to the files using the Dockerfile.
Run the commands:

```bash
chmod +x contrib/entrypoint.sh
chmod +x contrib/start.sh
```

## Deployment

### Dokku

On your local machine run:

```bash
git remote add dokku dokku@dokku.me:sensorsafrica-api
git push dokku master
```

For more information read [Deploying to Dokku](http://dokku.viewdocs.io/dokku/deployment/application-deployment/#deploying-to-dokku).

### Cronjob

This project uses celery to create cronjobs and flower to monitor the cron jobs as a web admin.
To create your jobs, add the task to the `tasks.py` and `CELERY_BEAT_SCHEDULE` in `settings.py`.

Everything starts automatically as setup in the `contrib/start.sh`:

```bash
celery -A sensorsafrica beat -l info &> /src/logs/celery.log  &
celery -A sensorsafrica worker -l info &> /src/logs/celery.log  &
celery -A sensorsafrica flower --basic_auth=$SENSORSAFRICA_FLOWER_ADMIN_USERNAME:$SENSORSAFRICA_FLOWER_ADMIN_PASSWORD &> /src/logs/celery.log  &
```

Note: If you run the project in the virtualenv you will have to start rabbitmq and pass that link to settings by the env variable `SENSORSAFRICA_RABBITMQ_URL`


## Monitoring

### Flower

It starts up in in the `contrib/start.sh`:

```bash
...
celery -A sensorsafrica flower --basic_auth=$SENSORSAFRICA_FLOWER_ADMIN_USERNAME:$SENSORSAFRICA_FLOWER_ADMIN_PASSWORD &> /src/logs/celery.log  &
```

### Slack

Provide channel webhook as an enivronment variable `SENSORSAFRICA_CELERY_SLACK_WEBHOOK`. The default options are used:

```
DEFAULT_OPTIONS = {
    "slack_beat_init_color": "#FFCC2B",
    "slack_broker_connect_color": "#36A64F",
    "slack_broker_disconnect_color": "#D00001",
    "slack_celery_startup_color": "#FFCC2B",
    "slack_celery_shutdown_color": "#660033",
    "slack_task_prerun_color": "#D3D3D3",
    "slack_task_success_color": "#36A64F",
    "slack_task_failure_color": "#D00001",
    "slack_request_timeout": 1,
    "flower_base_url": None,
    "show_celery_hostname": False,
    "show_task_id": True,
    "show_task_execution_time": True,
    "show_task_args": True,
    "show_task_kwargs": True,
    "show_task_exception_info": True,
    "show_task_return_value": True,
    "show_task_prerun": False,
    "show_startup": True,
    "show_shutdown": True,
    "show_beat": True,
    "show_broker": False,
    "use_fixed_width": True,
    "include_tasks": None,
    "exclude_tasks": None,
    "failures_only": False,
    "webhook": None,
    "beat_schedule": None,
    "beat_show_full_task_path": False,
}
```

### Sentry

Set the enivronment variable `SENSORSAFRICA_SENTRY_DSN`.

### Archiving

Archives are sent to CKAN and require environment configuration:

```
- CKAN_ARCHIVE_API_KEY=..
- CKAN_ARCHIVE_OWNER_ID=...
- CKAN_ARCHIVE_URL=<url that supports bulk uploads>
```

## Contributing

[opendata-stuttgart/feinstaub-api](https://github.com/opendata-stuttgart/feinstaub-api) prefer generating and applying migration to the database at the point of deployment (probably to reduce the number of changes to be applied).
We, on the other hand, prefer the Django recommended approach of creating and reviewing migration files at the development time, and then applying the same migration files to different environments; dev, staging and eventually production.

Hence, with any contribution, include both `sensors.AFRICA-api` and `opendata-stuttgart/feinstaub-api` migration files by running `python manage.py makemigrations` command before creating a PR.

## License

GNU GPLv3

Copyright (C) 2018 Code for Africa

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
