import pathlib

import h5py
import numpy as np

import XDMFWrite_h5py as xh

root = pathlib.Path(__file__).parent / pathlib.Path(__file__).stem

coor = np.array(
    [
        [0, 0],
        [0, 1],
        [0, 2],
        [1, 0],
        [1, 1],
        [1, 2],
    ]
)

conn = np.array(
    [
        [0, 1, 4, 3],
        [1, 2, 5, 4],
    ]
)

stress = np.array([1.0, 2.0])

with h5py.File(root.with_suffix(".h5"), "w") as file, xh.Grid(root.with_suffix(".xdmf")) as xdmf:

    file["coor"] = coor
    file["conn"] = conn
    file["stress"] = stress

    xdmf += xh.Unstructured(file["coor"], file["conn"], "Quadrilateral")
    xdmf += xh.Attribute(file["stress"], "Cell")
