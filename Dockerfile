FROM python:3.6.3

ENV PYTHONUNBUFFERED 1

# Create root directory for our project in the container
RUN mkdir /src

# Create application subdirectories
WORKDIR /src
RUN mkdir media static logs
VOLUME [ "src/logs" ]

# Copy the current directory contents into the container at sensors_africa
ADD . /src/

# Install gunicorn with gevent
RUN pip install -q -U gunicorn[gevent]
# Install feinstaub from sensors.AFRICA-AQ-api
RUN pip install -q git+https://github.com/CodeForAfricaLabs/sensors.AFRICA-AQ-api
RUN pip install -q -U pip setuptools
# Install any needed packages
RUN pip install -q . \
    && groupadd -r web \
    && useradd -r -g web web

RUN chown -R web /src

COPY ./start.sh /start.sh
COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]