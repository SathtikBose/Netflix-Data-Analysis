.PHONY: setup data clean eda app test lint help

PYTHON ?= python
PIP ?= pip

help:
	@echo "Available commands:"
	@echo "  make setup  - Install pinned dependencies and editable package"
	@echo "  make data   - Download or verify the Netflix dataset"
	@echo "  make clean  - Run data cleaning & preprocessing pipeline"
	@echo "  make eda    - Run full pipeline including EDA charts and findings"
	@echo "  make app    - Launch the interactive Streamlit dashboard"
	@echo "  make test   - Run pytest unit and smoke tests"
	@echo "  make lint   - Run ruff linter"

setup:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e . --no-deps

data:
	$(PYTHON) -m netflix_analysis.data_loader

clean:
	$(PYTHON) -m netflix_analysis.pipeline --stage clean

eda:
	$(PYTHON) -m netflix_analysis.pipeline --stage all

app:
	streamlit run app/streamlit_app.py

test:
	pytest --cov=netflix_analysis --cov-report=term-missing

lint:
	ruff check src tests app
