#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open


with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='fir_articles',
    version='0.1.0',
    description="Plugin for FIR (Fast Incident Response) to manage KB articles",
    long_description=readme,
    author="Gaetan Crahay",
    author_email='gaetan@crahay.eu',
    url='https://github.com/crahayg/fir_articles_plugin',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.7',
    ],
    license="Apache 2.0, see LICENSE",
    zip_safe=False,
    keywords='FIR KB',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ]
)
