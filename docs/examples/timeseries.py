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

disp = np.array(
    [
        [0.0, 0.0],
        [0.1, 0.0],
        [0.2, 0.0],
        [0.0, 0.0],
        [0.1, 0.0],
        [0.2, 0.0],
    ]
)

stress = np.array([1.0, 2.0])

file_hdf5 = root.with_suffix(".h5")
file_xdmf = root.with_suffix(".xdmf")

with h5py.File(file_hdf5, "w") as file, xh.TimeSeries(file_xdmf) as xdmf:

    file["coor"] = coor
    file["conn"] = conn

    for i in range(4):

        file[f"/stress/{i:d}"] = float(i) * stress
        file[f"/disp/{i:d}"] = float(i) * xh.as3d(disp)

        xdmf += xh.TimeStep()
        xdmf += xh.Unstructured(file["coor"], file["conn"], xh.ElementType.Quadrilateral)
        xdmf += xh.Attribute(file[f"/disp/{i:d}"], xh.AttributeCenter.Node, name="Displacement")
        xdmf += xh.Attribute(file[f"/stress/{i:d}"], xh.AttributeCenter.Cell, name="Stress")
