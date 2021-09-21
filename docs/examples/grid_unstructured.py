import h5py
import numpy as np

import XDMFWrite_h5py as xh

coor = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]])

conn = np.array([[0, 1, 4, 3], [1, 2, 5, 4]])

stress = np.array([1.0, 2.0])

with h5py.File("grid_unstructured.h5", "w") as file:

    file["/coor"] = coor
    file["/conn"] = conn
    file["/stress"] = stress

    grid = xh.Grid(
        xh.Unstructured(file, "/coor", "/conn", "Quadrilateral"),
        xh.Attribute(file, "/stress", "Cell"),
    )

    xh.write(grid, "grid_unstructured.xdmf")
