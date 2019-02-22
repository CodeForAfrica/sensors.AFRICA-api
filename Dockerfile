FROM python:3.6.3

ENV PYTHONUNBUFFERED 1

# Create root directory for our project in the container
RUN mkdir /src

# Create application subdirectories
WORKDIR /src
RUN mkdir media static logs
VOLUME [ "/src/logs" ]

# Copy the current directory contents into the container at sensorsafrica
ADD . /src/

# Upgrade pip and setuptools
RUN pip install -q -U pip setuptools

# Install feinstaub from opendata-stuttgart
RUN pip install -q git+https://github.com/opendata-stuttgart/feinstaub-api

# Install sensors.AFRICA-api and its dependencies
RUN pip install -q -U .

# Add crontab file in the cron directory
ADD crontab /etc/cron.d/$DOKKU_APP_NAME

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/$DOKKU_APP_NAME

# Create the log file
RUN touch /var/log/cron.log

#Install Cron
RUN apt-get update
RUN apt-get -y install cron

# Expose port server
EXPOSE 8000

COPY ./contrib/start.sh /start.sh
COPY ./contrib/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "/start.sh" ]
