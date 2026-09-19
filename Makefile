.PHONY: install migrate test check run worker beat
install:
	python -m pip install -r requirements.txt
migrate:
	python manage.py migrate
test:
	python -m pytest
check:
	python manage.py check
	python manage.py makemigrations --check --dry-run
run:
	python manage.py runserver
worker:
	celery -A config worker -l INFO
beat:
	celery -A config beat -l INFO
