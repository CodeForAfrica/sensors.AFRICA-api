FROM python:3.6.3

# Create application subdirectories
WORKDIR /src
RUN mkdir media static logs
VOLUME ["/src/logs/"]


# Add application source code to SRCDIR
ADD ./sensors_africa /src/
WORKDIR /src/

# Upgrade pip + setuptools, install sensors_africa
RUN pip install -q -U pip setuptools gunicorn
# RUN pip install -q git+git+https://github.com/CodeForAfricaLabs/sensors.AFRICA-AQ-api/
RUN pip install -q .

# Server
EXPOSE 8000

COPY ./sensors_africa/start.sh /
CMD ["/start.sh "]