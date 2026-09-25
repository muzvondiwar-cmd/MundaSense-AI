PYTHON ?= python

.PHONY: install migrate train evaluate test frontend-test frontend-build frontend-lint lint run dev api verify seed docker-up

install:
	$(PYTHON) -m pip install -r requirements-lock.txt
	$(PYTHON) -m pip install -e . --no-deps --no-build-isolation
	cd frontend && npm install

migrate:
	$(PYTHON) -m alembic upgrade head

train:
	$(PYTHON) scripts/train_model.py --regenerate-data

evaluate:
	$(PYTHON) scripts/evaluate_model.py

test:
	$(PYTHON) -m pytest
	cd frontend && npm test

frontend-test:
	cd frontend && npm test

frontend-build:
	cd frontend && npm run build

frontend-lint:
	cd frontend && npm run lint

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

run:
	$(PYTHON) -m streamlit run app.py

dev:
	$(PYTHON) scripts/dev.py

api:
	$(PYTHON) -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

verify:
	$(PYTHON) scripts/verify_release.py

seed:
	$(PYTHON) scripts/seed_demo.py

docker-up:
	docker compose up --build
