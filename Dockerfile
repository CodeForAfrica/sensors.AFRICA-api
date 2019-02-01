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

# Install feinstaub from sensors.AFRICA-AQ-api
RUN pip install -q git+https://github.com/CodeForAfricaLabs/sensors.AFRICA-AQ-api

# Install sensors.AFRICA-api and its dependencies
RUN pip install -q -U .

COPY ./contrib/start.sh /start.sh
COPY ./contrib/entrypoint.sh /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "/start.sh" ]
