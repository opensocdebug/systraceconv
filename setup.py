# Copyright 2019 The Open SoC Debug Project
#
# SPDX-License-Identifier: Apache-2.0

from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='opensocdebug-systraceconv',

    use_scm_version = {
        "relative_to": __file__,
        "write_to": "opensocdebug/systraceconv/version.py",
    },

    description = ("Open SoC Debug is a way to interact with and obtain "
                   "information from a System-on-Chip (SoC)."),
    long_description = long_description,
    url = "http://www.opensocdebug.org",

    license = 'Apache License, Version 2.0',

    author='Stefan Wallentowitz',
    author_email='stefan@wallentowitz.de',

    packages=find_packages(),
    zip_safe=False,

    setup_requires=[
        'setuptools_scm',
    ],

    entry_points = {
        'console_scripts': [
            'opensocdebug-systraceconv=opensocdebug.systraceconv.converter:main'
        ]
    },

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
    ],
)