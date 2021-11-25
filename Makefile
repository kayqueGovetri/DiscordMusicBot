BASE := $(shell /bin/pwd)
CODE_COVERAGE = 72
PIPENV ?= pipenv

###
# Lint section
###
_flake8:
	@flake8 --statistics --show-source rpa_commons/aws/ rpa_commons/rpa

_isort:
	@isort --diff --check-only rpa_commons/aws/ rpa_commons/rpa

_black:
	@black --check rpa_commons/aws/ rpa_commons/rpa

_isort-fix:
	@isort rpa_commons/aws/ rpa_commons/rpa

_black_fix:
	@black rpa_commons/aws/ rpa_commons/rpa

_pip_install_requirements:
	pip3 install -r requirements.txt

_pip_install_requirements_dev:
	pip3 install -r requirements_dev.txt

_pre_commit_install:
	pre-commit install

lint: _flake8 _isort _black  ## Check code lint
format-code: _isort-fix _black_fix ## Format code
install_dev: _pip_install_requirements _pip_install_requirements_dev _pre_commit_install ## Project installation
install_prod: _pip_install_requirements