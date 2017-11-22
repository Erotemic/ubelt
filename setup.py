#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Installation:
    pip install git+https://github.com/Erotemic/ubelt.git

Developing:
    git clone https://github.com/Erotemic/ubelt.git
    pip install -e ubelt

Pypi:
     # Presetup
     pip install twine

     # First tag the source-code
     VERSION=$(python -c "import setup; print(setup.version)")
     echo $VERSION
     git tag $VERSION -m "tarball tag $VERSION"
     git push --tags origin master

     # NEW API TO UPLOAD TO PYPI
     # https://packaging.python.org/tutorials/distributing-packages/

     # Build wheel or source distribution
     python setup.py bdist_wheel --universal

     # Use twine to upload. This will prompt for username and password
     twine upload --username erotemic --skip-existing dist/*

     # Check the url to make sure everything worked
     https://pypi.org/project/ubelt/

     # ---------- OLD ----------------
     # Check the url to make sure everything worked
     https://pypi.python.org/pypi?:action=display&name=ubelt

"""
from setuptools import setup


def parse_version(package):
    """
    Statically parse the version number from __init__.py

    CommandLine:
        python -c "import setup; print(setup.parse_version('ubelt'))"
    """
    from os.path import dirname, join
    import ast
    init_fpath = join(dirname(__file__), package, '__init__.py')
    with open(init_fpath) as file_:
        sourcecode = file_.read()
    pt = ast.parse(sourcecode)
    class VersionVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:
                if target.id == '__version__':
                    self.version = node.value.s
    visitor = VersionVisitor()
    visitor.visit(pt)
    return visitor.version


def parse_description():
    """
    Parse the description in the README file

    CommandLine:
        python -c "import setup; print(setup.parse_description())"
    """
    from os.path import dirname, join, exists
    readme_fpath = join(dirname(__file__), 'README.md')
    # print('readme_fpath = %r' % (readme_fpath,))
    # This breaks on pip install, so check that it exists.
    if exists(readme_fpath):
        # try:
        #     # convert markdown to rst for pypi
        #     import pypandoc
        #     return pypandoc.convert(readme_fpath, 'rst')
        # except Exception as ex:
            # strip out markdown to make a clean readme for pypi
            textlines = []
            with open(readme_fpath, 'r') as f:
                capture = False
                for line in f.readlines():
                    if '# Purpose' in line:
                        capture = True
                    elif line.startswith('##'):
                        break
                    elif capture:
                        textlines += [line]
            text = ''.join(textlines).strip()
            text = text.replace('\n\n', '_NLHACK_')
            text = text.replace('\n', ' ')
            text = text.replace('_NLHACK_', '\n\n')
            return text
    return ''


def parse_requirements(fname='requirements.txt'):
    """
    Parse the package dependencies listed in a requirements file.

    CommandLine:
        python -c "import setup; print(setup.parse_requirements())"
    """
    from os.path import dirname, join, exists
    require_fpath = join(dirname(__file__), fname)
    # This breaks on pip install, so check that it exists.
    if exists(require_fpath):
        with open(require_fpath, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            lines = [line for line in lines if not line.startswith('#')]
            return lines
    return []


if __name__ == '__main__':
    setup(
        name='ubelt',
        version=parse_version('ubelt'),
        author='Jon Crall',
        description='A "utility belt" of commonly needed utility and helper functions',
        long_description=parse_description(),
        install_requires=parse_requirements('requirements.txt'),
        extras_require={
            'all': parse_requirements('optional-requirements.txt')
        },
        author_email='erotemic@gmail.com',
        url='https://github.com/Erotemic/ubelt',
        license='Apache 2',
        packages=['ubelt', 'ubelt.meta', 'ubelt._internal'],
        classifiers=[
            # List of classifiers available at:
            # https://pypi.python.org/pypi?%3Aaction=list_classifiers
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities',
            # This should be interpreted as Apache License v2.0
            'License :: OSI Approved :: Apache Software License',
            # Supported Python versions
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
        ],
    )
