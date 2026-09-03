.PHONY: dev build up down test

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

test:
	python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
