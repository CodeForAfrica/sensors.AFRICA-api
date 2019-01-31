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

# Install feinstaub from sensors.AFRICA-AQ-api
RUN pip install -q git+https://github.com/CodeForAfricaLabs/sensors.AFRICA-AQ-api
RUN pip install -q -U pip setuptools
RUN pip install -q -U .

COPY ./contrib/start.sh /start.sh
COPY ./contrib/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "/start.sh" ]
