FROM python:3.6.3

ENV PYTHONUNBUFFERED 1

# Create root directory for our project in the container
RUN mkdir /sensors_africa
WORKDIR /sensors_africa

# Create application subdirectories
RUN mkdir media static logs

# Copy the current directory contents into the container at sensors_africa
ADD . /sensors_africa

# Install any needed packages
RUN pip install -q ./feinstaub
RUN pip install -q -U pip setuptools
RUN pip install -q . \
    && groupadd -r web \
    && useradd -r -g web web

RUN chown -R web /sensors_africa

COPY ./docker_compose/production/start.sh /start.sh
COPY ./docker_compose/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /start.sh \
    && chmod +x /entrypoint.sh \
    && chown django /entrypoint.sh \
    && chmod +x /start.sh \
    && chown django /start.sh

ENTRYPOINT ["/entrypoint.sh"]