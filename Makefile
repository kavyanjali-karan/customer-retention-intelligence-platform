install:
	pip install -r requirements.txt

test:
	pytest

run:
	uvicorn api.main:app --reload