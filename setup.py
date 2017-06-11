# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

test_requirements = ['pytest', 'pytest-cov']
required = ['appdirs']

setup(
    name='pdfebc',
    version='0.2.0',
    description='Application to compress PDF documents into an ebook reader-friendly size.',
    long_description=readme,
    author='Simon Larsén',
    author_email='slarse@kth.se',
    url='https://github.com/slarse/pdfebc',
    download_url='https://github.com/slarse/pdfebc/archive/v0.2.0.tar.gz',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['bin/pdfebc'],
    tests_require=test_requirements,
    install_requires=required
)
