from setuptools import find_packages
from setuptools import setup

setup(
    name="XDMFWrite_h5py",
    license="MIT",
    author="Tom de Geus",
    author_email="tom@geus.me",
    description="Write XDMF files using h5py to open HDF5 file",
    long_description="Write XDMF files using h5py to open HDF5 file",
    keywords="HDF5, h5py, XDMF, Paraview",
    url="https://github.com/tdegeus/XDMFWrite_h5py",
    packages=find_packages(),
    use_scm_version={"write_to": "XDMFWrite_h5py/_version.py"},
    setup_requires=["setuptools_scm"],
    install_requires=["h5py", "numpy"],
)
