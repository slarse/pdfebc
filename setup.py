# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pdfebc',
    version='0.0.1',
    description='Application to compress PDF documents into an ebook reader-friendly size.',
    long_description=readme,
    author='Simon Larsén',
    author_email='slarse@kth.se',
    url='https://github.com/slarse/pdfebc',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['bin/pdfebc']
)
