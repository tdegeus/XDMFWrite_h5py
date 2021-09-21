import h5py
import numpy as np

import XDMFWrite_h5py as xh

coor = np.array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]])

conn = np.array([[0, 1, 4, 3], [1, 2, 5, 4]])

disp = np.array(
    [[0.0, 0.0], [0.1, 0.0], [0.2, 0.0], [0.0, 0.0], [0.1, 0.0], [0.2, 0.0]]
)

stress = np.array([1.0, 2.0])

with h5py.File("timeseries.h5", "w") as file:

    file["/coor"] = coor
    file["/conn"] = conn

    series = xh.TimeSeries()

    for i in range(4):

        file[f"/stress/{i:d}"] = float(i) * stress
        file[f"/disp/{i:d}"] = float(i) * xh.as3d(disp)

        # It is important that fields have the same name for the entire time series
        series.push_back(
            xh.Unstructured(file, "/coor", "/conn", "Quadrilateral"),
            xh.Attribute(file, f"/disp/{i:d}", "Node", name="Displacement"),
            xh.Attribute(file, f"/stress/{i:d}", "Cell", name="Stress"),
        )

    xh.write(series, "timeseries.xdmf")
