
from setuptools import setup
from setuptools import find_packages

import re

filepath = 'XDMFWrite_h5py/__init__.py'
__version__ = re.findall(r'__version__ = \'(.*)\'', open(filepath).read())[0]

setup(
    name='XDMFWrite_h5py',
    version=__version__,
    license='MIT',
    author='Tom de Geus',
    author_email='tom@geus.me',
    description='Write XDMF files using h5py to open HDF5 file',
    long_description='Write XDMF files using h5py to open HDF5 file',
    keywords='HDF5, h5py, XDMF, Paraview',
    url='https://github.com/tdegeus/XDMFWrite_h5py',
    packages=find_packages(),
    install_requires=['docopt>=0.6.2', 'h5py>=2.8.0'])
