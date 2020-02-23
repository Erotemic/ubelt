#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Installation:
    pip install git+https://github.com/Erotemic/ubelt.git

Developing:
    git clone https://github.com/Erotemic/ubelt.git
    pip install -e ubelt
"""
import sys
from os.path import exists

from setuptools import find_packages
from setuptools import setup


def parse_version(fpath):
    """
    Statically parse the version number from a python file
    """
    import ast
    if not exists(fpath):
        raise ValueError('fpath={!r} does not exist'.format(fpath))
    with open(fpath, 'r') as file_:
        sourcecode = file_.read()
    pt = ast.parse(sourcecode)
    class VersionVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:
                if getattr(target, 'id', None) == '__version__':
                    self.version = node.value.s
    visitor = VersionVisitor()
    visitor.visit(pt)
    return visitor.version


def parse_description():
    """
    Parse the description in the README file

    CommandLine:
        pandoc --from=markdown --to=rst --output=README.rst README.md
        python -c "import setup; print(setup.parse_description())"
    """
    from os.path import dirname, join, exists
    readme_fpath = join(dirname(__file__), 'README.rst')
    # This breaks on pip install, so check that it exists.
    if exists(readme_fpath):
        with open(readme_fpath, 'r') as f:
            text = f.read()
        return text
    return ''


def parse_requirements(fname='requirements.txt', with_version=False):
    """
    Parse the package dependencies listed in a requirements file but strips
    specific versioning information.

    Args:
        fname (str): path to requirements file
        with_version (bool, default=False): if true include version specs

    Returns:
        List[str]: list of requirements items
    """
    from os.path import exists
    import re
    require_fpath = fname

    def parse_line(line):
        """
        Parse information from a line in a requirements text file
        """
        if line.startswith('-r '):
            # Allow specifying requirements in other files
            target = line.split(' ')[1]
            for info in parse_require_file(target):
                yield info
        else:
            info = {'line': line}
            if line.startswith('-e '):
                info['package'] = line.split('#egg=')[1]
            else:
                # Remove versioning from the package
                pat = '(' + '|'.join(['>=', '==', '>']) + ')'
                parts = re.split(pat, line, maxsplit=1)
                parts = [p.strip() for p in parts]

                info['package'] = parts[0]
                if len(parts) > 1:
                    op, rest = parts[1:]
                    if ';' in rest:
                        # Handle platform specific dependencies
                        # setuptools.readthedocs.io/en/latest/setuptools.html
                        # #declaring-platform-specific-dependencies
                        version, plat_deps = map(str.strip, rest.split(';'))
                        info['platform_deps'] = plat_deps
                    else:
                        version = rest  # NOQA
                    info['version'] = (op, version)
            yield info

    def parse_require_file(fpath):
        with open(fpath, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    for info in parse_line(line):
                        yield info

    def gen_packages_items():
        if exists(require_fpath):
            for info in parse_require_file(require_fpath):
                parts = [info['package']]
                if with_version and 'version' in info:
                    parts.extend(info['version'])
                if not sys.version.startswith('3.4'):
                    # apparently package_deps are broken in 3.4
                    plat_deps = info.get('platform_deps')
                    if plat_deps is not None:
                        parts.append(';' + plat_deps)
                item = ''.join(parts)
                yield item

    packages = list(gen_packages_items())
    return packages


def native_mb_python_tag(plat_impl=None, version_info=None):
    """
    Get the correct manylinux python version tag for this interpreter

    Example:
        >>> print(native_mb_python_tag())
        >>> print(native_mb_python_tag('PyPy', (2, 7)))
        >>> print(native_mb_python_tag('CPython', (3, 8)))
    """
    if plat_impl is None:
        import platform
        plat_impl = platform.python_implementation()

    if version_info is None:
        import sys
        version_info = sys.version_info

    major, minor = version_info[0:2]
    ver = '{}{}'.format(major, minor)

    if plat_impl == 'CPython':
        # TODO: get if cp27m or cp27mu
        impl = 'cp'
        if ver == '27':
            IS_27_BUILT_WITH_UNICODE = True  # how to determine this?
            if IS_27_BUILT_WITH_UNICODE:
                abi = 'mu'
            else:
                abi = 'm'
        else:
            if ver == '38':
                # no abi in 38?
                abi = ''
            else:
                abi = 'm'
        mb_tag = '{impl}{ver}-{impl}{ver}{abi}'.format(**locals())
    elif plat_impl == 'PyPy':
        abi = ''
        impl = 'pypy'
        ver = '{}{}'.format(major, minor)
        mb_tag = '{impl}-{ver}'.format(**locals())
    else:
        raise NotImplementedError(plat_impl)
    return mb_tag


NAME = 'ubelt'
VERSION = parse_version('ubelt/__init__.py')


if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        author='Jon Crall',
        description=('A Python utility belt containing simple tools, '
                     'a stdlib like feel, and extra batteries.'),
        long_description=parse_description(),
        long_description_content_type='text/x-rst',
        install_requires=parse_requirements('requirements/runtime.txt'),
        extras_require={
            'all': parse_requirements('requirements.txt'),
            'tests': parse_requirements('requirements/tests.txt'),
            'optional': parse_requirements('requirements/optional.txt'),
        },
        author_email='erotemic@gmail.com',
        url='https://github.com/Erotemic/ubelt',
        license='Apache 2',
        packages=find_packages('.'),
        classifiers=[
            # List of classifiers available at:
            # https://pypi.python.org/pypi?%3Aaction=list_classifiers
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities',
            # This should be interpreted as Apache License v2.0
            'License :: OSI Approved :: Apache Software License',
            # Supported Python versions
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
    )
