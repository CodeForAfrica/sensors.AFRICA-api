# sensors.AFRICA API [![Build Status](https://travis-ci.org/CodeForAfricaLabs/sensors.AFRICA-api.svg?branch=master)](https://travis-ci.org/CodeForAfricaLabs/sensors.AFRICA-api)

API to save data from deployed sensors in Africa.

pip install -d git+https://github.com/CodeForAfricaLabs/sensors.AFRICA-AQ-api/ #feinstaub

standardize gitignore using [gitignore.io](https://www.gitignore.io/)
currently using: `https://www.gitignore.io/api/vim,venv,emacs,linux,macos,python,django,virtualenv,intellij+all,visualstudiocode `

**NOTE:** 
- `docker-compose` is strictly for development and testing purposes. 
- The Dockerfile is written for production since dokku is being used and it will look for Dockerfile. Option to look into production and development as an enhancement with plugins such as [dokku-dockerfile](https://github.com/mimischi/dokku-dockerfile)

## Tests

**Using docker**

```
docker-compose run api pytest sensorsafrica/
```

**Without Docker**

You have to set environment variables like the following command.

```
SENSORSAFRICA_DBNAME=sensorsafrica SENSORSAFRICA_DBUSER=Karim SENSORSAFRICA_DBPASS= pytest ./sensorsafrica
```

**NOTE:** If entrypoint and start scripts are changed, make sure they have permissions since we don't grant permissions to the files using the Dockerfile. Run the commands:
```
chmod +x entrypoint.sh
chmod +x start.sh
```
