#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('docs/history.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as req:
    requirements = req.read().split('\n')

with open('requirements_dev.txt') as req:
    # Ignore the -r on the first line
    setup_requirements = req.read().split('\n')[1:]

setup_requirements += requirements
test_requirements = ['pytest>=3'] + requirements
print(setup_requirements)
setup(
    author="Micah Johnson",
    author_email='micah.johnson150@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="SQL Databse software for SnowEx data",
    entry_points={
        'console_scripts': [
            'snowxsql=snowxsql.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='snowxsql',
    name='snowxsql',
    packages=find_packages(include=['snowxsql', 'snowxsql.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/hpmarshall/SnowEx2020_SQLcode',
    version='0.1.0',
    zip_safe=False,
)
