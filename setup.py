#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='neonx',
    version='0.1.1',
    description='Handles conversion of date from NetworkX graph to Neo4j',
    long_description=readme + '\n\n' + history,
    author='Rohit Aggarwal',
    author_email='rohit.neonx@mailnull.com',
    url='https://github.com/ducky427/neonx',
    packages=[
        'neonx',
    ],
    package_dir={'neonx': 'neonx'},
    include_package_data=True,
    install_requires=['networkx', 'requests'
    ],
    license="MIT",
    zip_safe=False,
    keywords='neonx',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)