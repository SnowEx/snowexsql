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
    # Ignore the -r on the two lines
    setup_requirements = req.read().split('\n')[2:]

setup_requirements += requirements
test_requirements = ['pytest>=3'] + requirements

setup(
    author="Micah Johnson",
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="SQL Database software for SnowEx data",
    entry_points={
        'console_scripts': [
            'clear_dataset=snowexsql.cli:clear_dataset',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='snowexsql',
    name='snowexsql',
    packages=find_packages(include=['snowexsql', 'snowexsql.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/SnowEx/snowexsql',
    version='0.3.0',
    zip_safe=False,
)
