FROM python:3.6.3

ENV PYTHONUNBUFFERED 1

# Create application root directory
WORKDIR /src

RUN mkdir media static logs
VOLUME [ "/src/logs" ]

# Upgrade pip and setuptools with trusted hosts
RUN python -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --upgrade pip setuptools

# Copy the current directory contents into the container at sensorsafrica
COPY . /src/

# Install dependencies
RUN pip install -q git+https://github.com/opendata-stuttgart/feinstaub-api && \
    pip install -q .

# Expose port server
EXPOSE 8000
EXPOSE 5555

COPY ./contrib/start.sh /start.sh
COPY ./contrib/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD [ "/start.sh" ]

