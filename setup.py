from setuptools import setup

version = '3.0.0'

setup(name='skink',
      version=version,
      description="Skink is a Continuous Integration server in python",
      long_description="""\
Skink is a Continuous Integration server in python.
For reference to what a skink is check http://www.wildherps.com/species/E.skiltonianus.html""",
      classifiers=["Development Status :: 2 - Pre-Alpha",
				   "Intended Audience :: Developers",
				   "License :: OSI Approved",
				   "Natural Language :: English",
				   "Programming Language :: Python :: 2.6",],
      keywords='Continuous Integration CI python',
      author='Bernardo Heynemann',
      author_email='heynemann@gmail.com',
      url='http://www.skinkci.org',
      license='OSI',
      packages=["skink",],
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

