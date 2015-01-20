"""
Fabric fabfile for solartime module.

Run `pip install fabric` to install, then `fab --list` to see available commands.
"""

from fabric.api import local, lcd, with_settings


def test():
    """Run project unit tests."""
    local('python -m unittest discover -v -s test')
unittest = test


@with_settings(warn_only=True)
def pep8():
    """Check source for PEP8 conformance."""
    local('pep8 --max-line-length=120 solartime.py')


def precommit():
    """Run pre-commit unit tests and lint checks."""
    pep8()
    local('pylint -f colorized --errors-only solartime')
    local('2to3 solartime')
    test()


def lint(fmt='colorized'):
    """Run verbose PyLint on source. Optionally specify fmt=html for HTML output."""
    if fmt == 'html':
        outfile = 'pylint_report.html'
        local('pylint -f %s solartime > %s || true' % (fmt, outfile))
        local('open %s' % outfile)
    else:
        local('pylint -f %s solartime || true' % fmt)
pylint = lint


def clean():
    """Clean up generated files."""
    local('rm -rf dist')
    local('rm -f pylint_report.html')
    local('find . -name "*.pyc" | xargs rm')
    with lcd('doc'):
        local('make clean')


def release(version):
    """Perform git-flow release merging and PyPI upload."""
    clean()
    local('git checkout master')
    local('git merge --no-ff dev')
    local('git tag %s' % version)
    local('python setup.py sdist upload')


def doc(fmt='html'):
    """Build Sphinx HTML documentation."""
    with lcd('docs'):
        local('make %s' % fmt)
    if fmt == 'html':
        local('open docs/_build/html/index.html')
docs = doc
