from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

setup(
    name="sage-data-entities",
    version='0.1.0',
    description="Sage Data Entities python package",
    long_description=readme,
    url='https://github.com/iperezx/sage-data-entities',
    packages=find_packages(exclude=('tests')),
    python_requires=">=3.6",
    install_requires=required,
    setup_requires=['wheel'],
)