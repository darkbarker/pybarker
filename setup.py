from setuptools import setup, find_packages
from os.path import join, dirname

import pybarker

setup(
    name="pybarker",
    version=pybarker.__version__,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    long_description=open(join(dirname(__file__), "README.md")).read(),
    install_requires=["unidecode"],
)
