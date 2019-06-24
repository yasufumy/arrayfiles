init:
	pipenv install --skip-lock --dev
test:
	pipenv run pytest --cov=easyfile --cov-report=term-missing tests
