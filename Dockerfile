FROM python:3.9.7

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
# RUN pip install -q git+https://github.com/opendata-stuttgart/feinstaub-api

# Install sensors.AFRICA-api and its dependencies
RUN pip install -q -U .

# Expose port server
EXPOSE 8000
EXPOSE 5555

COPY ./contrib/start.sh /start.sh
COPY ./contrib/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "/start.sh" ]
