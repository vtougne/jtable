#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="jtable",
    version="0.9.6",
    packages=find_packages(),
    install_requires=[
        'tabulate',
        'PyYAML',
        'Jinja2'
    ],
    entry_points={
            'console_scripts': [
                'jtable=jtable.jtable:main',
            ],
        },

    author="Vincent Tougne",
    author_email="vtougne@gmail.com",
    description="tabulate json data and transform them using jinja",
    url="https://github/vtougne",
)
