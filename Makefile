.PHONY: install run-api run-ui run clean

install:
	pip install -r requirements.txt

run-api:
	uvicorn backend.main:app --reload

run-ui:
	streamlit run frontend/app.py

run:
	@echo "Starting Backend and Frontend..."
	@trap 'kill %1; kill %2' SIGINT; \
	uvicorn backend.main:app --reload & \
	streamlit run frontend/app.py & \
	wait

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
