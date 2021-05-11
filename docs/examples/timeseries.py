import XDMFWrite_h5py as xh
import h5py
import numpy as np

coor = np.array([
    [0, 0],
    [0, 1],
    [0, 2],
    [1, 0],
    [1, 1],
    [1, 2]])

conn = np.array([
    [0, 1, 4, 3],
    [1, 2, 5, 4]])

disp = np.array([
    [0.0, 0.0],
    [0.1, 0.0],
    [0.2, 0.0],
    [0.0, 0.0],
    [0.1, 0.0],
    [0.2, 0.0]])

stress = np.array([1.0, 2.0])

with h5py.File("timeseries.h5", "w") as file:

    file["/coor"] = coor
    file["/conn"] = conn

    series = xh.TimeSeries()

    for i in range(4):

        file["/stress/{0:d}".format(i)] = float(i) * stress
        file["/disp/{0:d}".format(i)] = float(i) * xh.as3d(disp)

        # It is important that fields have the same name for the entire time series
        series.push_back(
            xh.Unstructured(file, "/coor", "/conn", "Quadrilateral"),
            xh.Attribute(file, "/disp/{0:d}".format(i), "Node", name="Displacement"),
            xh.Attribute(file, "/stress/{0:d}".format(i), "Cell", name="Stress"))

    xh.write(series, "timeseries.xdmf")

