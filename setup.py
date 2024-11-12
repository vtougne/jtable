#!/usr/bin/env python3

from setuptools import setup, find_packages

from jtable.version import __version__


setup(
    name="jtable",
    version=__version__,
    packages=find_packages(),
    # install_requires=[
    #     'tabulate',
    #     'PyYAML',
    #     'Jinja2'
    # ],
    include_package_data=True,
    package_data={'': ['resources/*','tabulate/*','jinja2/*','yaml/*']},

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
