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

conn = np.arange(coor.shape[0])

radius = np.random.random(coor.shape[0])


with h5py.File(root.with_suffix(".h5"), "w") as file, xh.Grid(root.with_suffix(".xdmf")) as xdmf:

    file["coor"] = coor
    file["conn"] = conn
    file["radius"] = radius

    xdmf += xh.Structured(file["coor"], file["conn"])
    xdmf += xh.Attribute(file["radius"], "Node")
