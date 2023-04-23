from setuptools import setup, find_packages
import json


def find_requirements():
    with open("Pipfile.lock") as lock:
        requirements: dict[str, dict] = json.load(lock)["default"]
        return [name + info["version"] for name, info in requirements.items()]


setup(
    name="ctOS",
    version="0.1.0",
    author="Viktor A. Rozenko Voitenko",
    description="Crypto Trading Operating System",
    url="https://github.com/bumblebee-crypto/ctos#readme",
    python_requires=">=3.9, <4",
    packages=find_packages(),
    install_requires=find_requirements(),
)
