COMPOSE = docker-compose

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

logst:
	$(COMPOSE) logs -f

compilescss:
	$(COMPOSE) exec api python manage.py compilescss
	$(COMPOSE) exec api python manage.py collectstatic --clear --noinput

enter:
	$(COMPOSE) exec api bash

shell:
	$(COMPOSE) exec api python manage.py shell

migrate:
	$(COMPOSE) exec api python manage.py migrate

test:
	$(COMPOSE) exec api python manage.py pytest --pylama

createsuperuser:
	$(COMPOSE) exec api python manage.py createsuperuser


clean:
	@find . -name "*.pyc" -exec rm -rf {} \;
	@find . -name "__pycache__" -delete
