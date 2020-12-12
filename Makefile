COMPOSE = docker-compose

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

log:
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
	$(COMPOSE) exec api pytest --pylama

testexpr:
	$(COMPOSE) exec api pytest --pylama -k '$(expr)'

createsuperuser:
	$(COMPOSE) exec api python manage.py createsuperuser

down:
	$(COMPOSE) down

clean:
	@find . -name "*.pyc" -exec rm -rf {} \;
	@find . -name "__pycache__" -delete
