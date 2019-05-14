.PHONY: help
help:
	@echo "make help ....... print this helpful documentation"
	@echo "make dep ........ install dependencies"
	@echo "make test ....... run unit test suite"
	@echo "make pep8 ....... run pep8 syntax checker"
	@echo "make lint ....... run pylint static analysis"
	@echo "make precommit .. run unit tests, pep8, pylint, 2to3"
	@echo "make doc ........ build HTML documentation"
	@echo "make clean ...... clean build artifacts"
	@echo "make release .... commit a git release"


.PHONY: dep
dep:
	pip install -U -r requirements.txt


.PHONY: test
test:
	python -m unittest discover -v


.PHONY: pep8
pep8:
	pep8 --max-line-length=120 solartime.py || true


.PHONY: 2to3
2to3:
	2to3 solartime.py


.PHONY: precommit
precommit: pep8 lint 2to3 test


.PHONY: lint
lint:
	pylint -f colorized --errors-only solartime.py


.PHONY: clean
clean:
	rm -rf dist __pycache__
	find . -name '*.pyc' -delete
	cd doc && make clean


.PHONY: release
release: clean
	git checkout master
	git merge --no-ff dev
	git tag $(VERSION)  # TODO
	python setup.py sdist upload


.PHONY: doc
doc:
	cd docs && make html

