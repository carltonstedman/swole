# -*- coding: utf-8 -*-
"""Swole."""
# batteries included
from __future__ import absolute_import

from setuptools import find_packages, setup


with open('requirements.txt') as f:
    install_requirements = f.readline()

test_requirements = [
    'flake8>=3.7.9,<4',
    'mypy>=0.761',
    'pydocstyle>=5.0.1,<6',
    'pytest>=5.3.2,<5.4',
]

dev_requirements = test_requirements + [
    'black>=19.10b0',
    'coverage>=5.0,<6',
    'pdbpp>=0.10.2',
    'pytest-cov>=2.8.1',
    'pytest-sugar>=0.9.2',
]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Powerlifters',
    'Intended Audience :: Strength Enthusiasts',
    'License :: Unlicense',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
]


setup(
    author='Carlton Stedman',
    author_email='carlton@datarobot.com',
    classifiers=classifiers,
    description='Library and tooling for planning lifting progressions.',
    entry_points={'console_scripts': ['swole=swole.views.cli:main']},
    extras_require={'dev': dev_requirements, 'test': test_requirements},
    install_requires=install_requirements,
    keywords=['swole'],
    name='swole',
    package_data={'swole': ['programs/*']},
    package_dir={'swole': 'swole'},
    packages=find_packages(),
    tests_require=test_requirements,
    test_suite='tests',
    url='https://github.com/carltonstedman/swole',
    version='0.1.0.dev0',
)
