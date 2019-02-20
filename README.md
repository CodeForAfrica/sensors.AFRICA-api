# sensors.AFRICA API [![Build Status](https://travis-ci.org/CodeForAfricaLabs/sensors.AFRICA-api.svg?branch=master)](https://travis-ci.org/CodeForAfricaLabs/sensors.AFRICA-api)

API to save and access data from deployed sensors in cities all around Africa.

## Development

Gitignore is standardized for this project using [gitignore.io](https://www.gitignore.io/) to support various development platforms.
To get the project up and running:

- Clone this repo

### Virtual environment

- Use virtualenv to create your virtual environment; `virtualenv venv`
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

### Cronitor

[Setup cronitor:](https://cronitor.io/docs/using-cronitor-cli)

```bash
wget https://cronitor.io/dl/cronitor-cli-stable-linux-amd64.tgz
sudo tar xvf cronitor-cli-stable-linux-amd64.tgz -C /usr/bin/
sudo /usr/bin/cronitor configure --api-key 1e5db066119f4b439352ef5e70eaaecc
rm cronitor-cli-stable-linux-amd64.tgz
```

Follow the [intergratation guide](https://cronitor.io/docs/integration-guide) to get the monitor working.

### Crontab

- Change users to dokku; `sudo su dokku`
- Edit dokku's crontab; `crontab -e`
- To export csv to openAFRICA as archives add the following:

```bash
1 0 * * * cronitor exec <cronitor monitor code> dokku enter < dokku app name > web python3 manage.py upload_to_ckan >> /var/log/cron.log 2>&1
```

- To calculate data statistics add the following:

```bash
0 * * * * cronitor exec <cronitor monitor code> dokku enter sensorsafrica-staging web python3 manage.py calculate_data_statistics  >> /var/log/cron.log 2>&1
```

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
