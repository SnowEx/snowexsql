#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('docs/history.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as req:
    requirements = req.read().split('\n')

test_requirements = ['pytest>=3'] + requirements

setup(
    author="Micah Johnson",
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    description="SQL Database software for SnowEx data",
    entry_points={[],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='snowexsql',
    name='snowexsql',
    packages=find_packages(include=['snowexsql', 'snowexsql.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/SnowEx/snowexsql',
    version='0.4.1',
    zip_safe=False,
)
