#!/usr/bin/env python3
import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
from jtable.version import __version__

class CustomInstallCommand(install):
    def run(self):
        dependencies_dir = os.path.join(os.path.dirname(__file__), "dependencies")
        requirements_file = os.path.join(dependencies_dir, "requirements.txt")
        if os.path.exists(requirements_file):
            print(f"Installing dependencies from {requirements_file}")
            subprocess.check_call(["pip", "install", "--no-index", "--find-links", dependencies_dir, "-r", requirements_file])
        
        # Continuer avec l'installation normale
        install.run(self)

setup(
    name="jtable",
    version=__version__,
    packages=find_packages(include=["jtable", "jtable.*"]),
    # Supprimé install_requires car les dépendances sont gérées localement
    include_package_data=True,
    package_data={'': ['resources/*']},
    entry_points={
        'console_scripts': [
            'jtable=jtable.jtable:main',
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,  # Utilisation de la classe personnalisée
    },
    author="Vincent Tougne",
    author_email="vtougne@gmail.com",
    description="Tabulate JSON data and transform them using Jinja templates.",
    license="MIT",
    license_files=["LICENSE.txt"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    url="https://github.com/vtougne/jtable",
)
