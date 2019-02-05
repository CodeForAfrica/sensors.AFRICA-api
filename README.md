# sensors.AFRICA API [![Build Status](https://travis-ci.org/CodeForAfricaLabs/sensors.AFRICA-api.svg?branch=master)](https://travis-ci.org/CodeForAfricaLabs/sensors.AFRICA-api)

API to save and access data from deployed sensors in cities all around Africa.

## Development

- Clone this repo

### Virtual environment

- Use virtualenv to crete your virtual environment; `virtualenv venv`
- Activate the virtual environment; `source venv/bin/activate`
- Install the requirements; `pip install .`
- Create a sensorsafrica database with the following sql script:

```sql
CREATE DATABASE sensorsafrica;
CREATE USER sensorsafrica WITH ENCRYPTED PASSWORD 'sensorsafrica';
GRANT ALL PRIVILEGES ON DATABASE sensorsafrica TO sensorsafrica;
```

- Migrate the database; `python manage.py migrate`
- Run the server; `python manage.py runserver`

### Docker

Using docker compose:

- Build the project; `docker-compose build`
- Run the project; `docker-compose up -d`

**NOTE:**
`docker-compose` is strictly for development and testing purposes.
The Dockerfile is written for production since dokku is being used and it will look for Dockerfile.

### Tests

- Using docker; `docker-compose run api pytest --pylama`
- Without Docker; `pytest --pylama`

**NOTE:**
If entrypoint and start scripts are changed, make sure they have permissions since we don't grant permissions to the files using the Dockerfile.
Run the commands:

```bash
chmod +x contrib/entrypoint.sh
chmod +x contrib/start.sh
```

## Deployment

We deploy to staging firs and then deploy to production after confirming everything works fine.

### Dokku

- Add the dokku remote url for the evironment you want to deploy to such as stanging and production; `git remote add staging dokku@dokku-2.sensors.africa:sensorsfrica-staging`
- Then push a branch to the staging master; `git push staging <branch>:master`

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
