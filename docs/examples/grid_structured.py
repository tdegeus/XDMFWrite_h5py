import h5py
import numpy as np

import XDMFWrite_h5py as xh

coor = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]])

conn = np.arange(coor.shape[0])

radius = np.random.random(coor.shape[0])

with h5py.File("grid_structured.h5", "w") as file:

    file["/coor"] = coor
    file["/conn"] = conn
    file["/radius"] = radius

    grid = xh.Grid(
        xh.Structured(file, "/coor", "/conn"), xh.Attribute(file, "/radius", "Node")
    )

    xh.write(grid, "grid_structured.xdmf")
