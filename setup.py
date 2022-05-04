from pathlib import Path

from setuptools import find_packages
from setuptools import setup

project_name = "XDMFWrite_h5py"

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name=project_name,
    license="MIT",
    author="Tom de Geus",
    author_email="tom@geus.me",
    description="Write XDMF files using h5py to open HDF5 file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="HDF5, h5py, XDMF, Paraview",
    url=f"https://github.com/tdegeus/{project_name:s}",
    packages=find_packages(),
    use_scm_version={"write_to": f"{project_name}/_version.py"},
    setup_requires=["setuptools_scm"],
    install_requires=["h5py", "numpy"],
)
