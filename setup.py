#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# jarvis4se version
VERSION = "1.1.2"


def readme():
    """print long description"""
    with open('README.md') as f:
        return f.read()


setup(
    name="jarvis4se",
    version=VERSION,
    description="Jarvis 4 Systems Engineers",
    long_description=readme(),
    url="https://github.com/rcasteran/jarvis4se",
    author="Justin ANCELOT",
    author_email="not2behere@gmx.fr",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Engineering Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
    ],
    keywords='',
    packages=find_packages(include=['jarvis4se', 'jarvis4se.*']),
    install_requires=['pytest', 'pytest_mock'],
    python_requires='>=3.7.6',
)
