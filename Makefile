init:
	pip install pipenv --upgrade
    pipenv install --dev --skip-lock
docs:
    cd docs && make html
