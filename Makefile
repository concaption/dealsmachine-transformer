.PHONY: setup install test format lint docker-build docker-run docker-compose-up clean

setup:
	python -m venv .venv
	.venv/Scripts/activate && pip install --upgrade pip
	.venv/Scripts/activate && pip install -r requirements.txt

install:
	pip install --upgrade pip
	pip install -r requirements.txt

run:
	python api.py

test:
	python test_api.py

run-docker:
	docker compose up --build

stop-docker:
	docker compose down