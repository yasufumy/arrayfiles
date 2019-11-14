init:
	pipenv install --skip-lock --dev
	pipenv run flake8 --install-hook git
	git config --bool flake8.strict true
test:
	pipenv run pytest --cov=easyfile --cov-report=term-missing tests
