#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import find_packages, setup

setup(
    name='eventmonkey',
    version='1.3.0',
    description='A Windows Event Processing Utility',
    author = 'G-C Partners, LLC',
    author_email = 'dev@g-cpartners.com',
    url='https://github.com/devgc/EventMonkey',
    download_url = 'https://github.com/devgc/EventMonkey/archive/1.3.0.tar.gz',
    license="Apache Software License v2",
    zip_safe=False,
    include_package_data=True,
    dependency_links = [
        'https://github.com/devgc/GcHelpers/tarball/master#egg=gchelpers-0.0.1'
    ],
    install_requires=[
        'lxml',
        'bs4',
        'progressbar2',
        'pyyaml',
        'gchelpers==0.0.1',
        'python-dateutil==2.4.2'
    ],
    packages=find_packages(
        '.'
    ),
    scripts=[
        u'EventMonkey.py',
    ],
    classifiers=[
        'Programming Language :: Python',
    ]
)