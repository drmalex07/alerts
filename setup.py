from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='alerts',
      version=version,
      description="Alerts on excessive use of system resources",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='collectd alerts rrd monitoring',
      author='Michail Alexakis',
      author_email='drmalex07@gmail.com',
      url='',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "thrush",
          "psutil",
          "genshi",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
