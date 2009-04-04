from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='skink',
      version=version,
      description="skink is a Continuous Integration server in python",
      long_description="""\
skink is a Continuous Integration server in python.
For reference to what a skink is check http://www.wildherps.com/species/E.skiltonianus.html""",
      classifiers=["Development Status :: 2 - Pre-Alpha",
				   "Intended Audience :: Developers",
				   "License :: OSI Approved",
				   "Natural Language :: English",
				   "Programming Language :: Python :: 2.5",], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Continuous Integration CI python',
      author='Bernardo Heynemann',
      author_email='heynemann@gmail.com',
      url='http://www.skinkci.org',
      license='OSI',
      packages=["skink",],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          CherryPy,
          Genshi,
          Babel,
          FormEncode
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
