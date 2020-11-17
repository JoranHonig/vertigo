import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

REQUIREMENTS = (HERE / "requirements.txt")

requirements = [x for x in map(str.strip, REQUIREMENTS.read_text().split("\n")) if x != ""]

setup(
    name="eth-vertigo",
    version="1.2.0",
    description="Mutation Testing for Ethereum Smart Contracts",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/joranhonig/vertigo",
    author="Joran Honig",
    author_email="joran.honig@gmail.com",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vertigo=eth_vertigo.cli.main:cli",
        ]
    },
)
