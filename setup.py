from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(
    name='alerts',
    version=version,
    description="Generate alerts based on collectd stats",
    long_description="""Generate alerts based on collectd stats""",
    classifiers=[ 
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Topic :: System :: Monitoring',
        'Programming Language :: Python',
    ],
    keywords='collectd alerts rrd monitoring',
    author='Michail Alexakis',
    author_email='drmalex07@gmail.com',
    url='https://github.com/drmalex07/alerts',
    license='GPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        "PasteDeploy",
        "thrush",
        "genshi",
        "zope.interface",
        "zope.schema",
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
