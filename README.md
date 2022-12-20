[![CI](https://github.com/tdegeus/XDMFWrite_h5py/workflows/CI/badge.svg)](https://github.com/tdegeus/XDMFWrite_h5py/actions)
[![readthedocs](https://readthedocs.org/projects/xdmfwrite_h5py/badge/?version=latest)](https://readthedocs.org/projects/xdmfwrite_h5py/badge/?version=latest)

Module to write XDMF files for HDF5 files. For example:

```python
with h5py.File(root.with_suffix(".h5")) as file, xh.Grid(root.with_suffix(".xdmf")) as xdmf:

    xdmf += xh.Unstructured(file["coor"], file["conn"], "Quadrilateral")
    xdmf += xh.Attribute(file["stress"], "Cell")
```

See
**Documentation: [xdmfwrite-h5py.readthedocs.io](https://xdmfwrite-h5py.readthedocs.io/en/latest/)**
for more information and examples.
