# sensors.AFRICA API

API to save data from deployed sensors in Africa.

pip install -d git+https://github.com/CodeForAfricaLabs/sensors.AFRICA-AQ-api/ #feinstaub

## Tests

**Using docker**

```docker-compose run web pytest sensors_africa/```

**Without Docker**

You have to set environment variables like the following command.

```DBNAME=test_sensorsafricapytest DBUSER=postgres DBPASS= pytest pytest ./sensors_africa```