# sensors.AFRICA API

API to save data from deployed sensors in Africa.

pip install -d git+https://github.com/CodeForAfricaLabs/sensors.AFRICA-AQ-api/ #feinstaub

**NOTE:** 
- `docker-compose` is scritly for development and testing purposes. 
- The Dockerfile is written for production since dokku is being used and it will look for Dockerfile. Option to look into production and development as an enhancement with plugins such as [dokku-dockerfile](https://github.com/mimischi/dokku-dockerfile)

## Tests

**Using docker**

```docker-compose run web pytest sensors_africa/```

**Without Docker**

You have to set environment variables like the following command.

```DBNAME=test_sensorsafricapytest DBUSER=postgres DBPASS= pytest pytest ./sensors_africa```