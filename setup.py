# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in landa/__init__.py
from landa import __version__ as version

setup(
	name='landa',
	version=version,
	description='Datenmanagementsystem des ',
	author='Landesverband Sächsischer Angler e. V.Real Experts GmbH',
	author_email='office@realexperts.de',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
