#
# Copyright (C) 2014, All Rights Reserved, PokitDok, Inc.
# https://www.pokitdok.com
#
# Please see the License.txt file for more information.
# All other rights reserved.
#
"""
PokitDok Platform API Client for Python
---------------------------------------

The PokitDok Platform API Client makes it easy it interact with the
PokitDok Platform APIs when writing client applications in Python.

See https://platform.pokitdok.com for more information.


The PokitDok Platform API Client for Python is distributed under the MIT License.
"""
from setuptools import setup


setup(
    name="pokitdok",
    version="2.7.2",
    license="MIT",
    author="PokitDok, Inc.",
    author_email="platform@pokitdok.com",
    url="https://platform.pokitdok.com",
    download_url='https://github.com/pokitdok/pokitdok-python/tarball/2.7.2',
    description="PokitDok Platform API Client",
    long_description=__doc__,
    packages=["pokitdok", "pokitdok.api", "tests"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[
        "requests>=2.3.0", "oauthlib==0.7.2", "requests-oauthlib==0.4.1",
    ],
    test_suite='nose.collector',
    tests_require=["nose==1.3.7"],
    keywords=['health', 'api', 'pokitdok', 'X12', 'eligibility', 'claims', 'providers', 'prices', 'healthcare',
              'referrals', 'authorizations', 'insurance', 'plans', 'benefits', 'enrollment'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
