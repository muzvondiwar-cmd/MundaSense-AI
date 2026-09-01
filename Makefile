PYTHON ?= python

.PHONY: install train evaluate test lint run verify seed

install:
	$(PYTHON) -m pip install -r requirements-lock.txt
	$(PYTHON) -m pip install -e . --no-deps --no-build-isolation

train:
	$(PYTHON) scripts/train_model.py --regenerate-data

evaluate:
	$(PYTHON) scripts/evaluate_model.py

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

run:
	$(PYTHON) -m streamlit run app.py

verify:
	$(PYTHON) scripts/verify_release.py

seed:
	$(PYTHON) scripts/seed_demo.py
