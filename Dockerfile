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
RUN pip install -q git+https://github.com/CodeForAfricaLabs/sensors.AFRICA-AQ-api
RUN pip install -q -U pip setuptools
RUN pip install -q . \
    && groupadd -r web \
    && useradd -r -g web web

RUN chown -R web /sensors_africa

COPY ./start.sh /start.sh
COPY ./entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /start.sh \
    && chmod +x /entrypoint.sh \
    && chown web /entrypoint.sh \
    && chmod +x /start.sh \
    && chown web /start.sh

ENTRYPOINT ["/entrypoint.sh"]