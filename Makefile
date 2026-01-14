.PHONY: install run-api run-ui run clean venv

# Define executables from the virtual environment
VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
UVICORN = $(VENV_DIR)/bin/uvicorn
STREAMLIT = $(VENV_DIR)/bin/streamlit

venv:
	python3 -m venv $(VENV_DIR)

install:
	$(PIP) install -r requirements.txt

run-api:
	$(UVICORN) backend.main:app --reload

run-ui:
	$(STREAMLIT) run frontend/app.py

run:
	@echo "Starting Backend and Frontend..."
	@trap 'kill %1; kill %2' SIGINT; \
	$(UVICORN) backend.main:app --reload & \
	$(STREAMLIT) run frontend/app.py & \
	wait

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
