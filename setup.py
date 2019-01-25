#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
from setuptools import find_packages, setup

NAME = 'fakehome'
DESCRIPTION = ''
URL = 'https://github.com/yop0/fakehome'
EMAIL = 'johan.medrano653@gmail.com'
AUTHOR = 'Johan Medrano'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.0'

REQUIRED = [
    'owlready2', 'tqdm', 'wget', 'networkx', 'numpy', 'scipy', 'matplotlib'
]

EXTRAS = {
    'draw3d': ['mayavi'],
}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    package_data={NAME: ['*_config.json']},
    include_package_data=True,
    install_requires=REQUIRED,
    extras_requires=EXTRAS,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 1 - Alpha',
    ],
)
