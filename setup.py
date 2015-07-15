from codecs import open
import os

from setuptools import setup, find_packages


ROOT = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(ROOT, 'VERSION')) as f:
    VERSION = f.read().strip()

setup(
    name='django-migration-fixture',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    license='MIT',
    version=str(VERSION),
    description="Django app to easily turn initial_data.* fixtures into Django 1.7 data migrations.",
    author='Alex Hayes',
    author_email='alex@alution.com',
    url='https://github.com/alexhayes/django-migration-fixture',
    download_url='https://github.com/alexhayes/django-migration-fixture/tarball/%s' % VERSION,
    keywords=['django', 'migrations', 'initial data'],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Software Development :: Code Generators',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],

    include_package_data=True,

)

