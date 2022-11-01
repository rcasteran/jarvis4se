#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# jarvis4se version
VERSION = "1.3.2"


def readme():
    """print long description"""
    with open('README.md', "r", encoding="utf-8") as f:
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
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.8",
    ],
    keywords='',
    packages=find_packages(include=['jarvis4se', 'jarvis4se.*']),
    install_requires=[
        'ipython >= 7.27.0',
        'lxml >= 4.6.3',
        'notebook >= 6.4.3',
        'plantuml == 0.3.0',
        'pandas~=1.4.1'],
    python_requires='>=3.8',
)
