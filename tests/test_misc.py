import os
import pathlib
import unittest

import h5py
import numpy as np

import XDMFWrite_h5py as xh

root = pathlib.Path(__file__).parent
hdf5_file = root / "tmp.h5"
xdmf_file = root / "tmp.xdmf"


class TestMisc(unittest.TestCase):
    def test_grid_structured(self):

        expected = """
<?xml version="1.0" ?><Xdmf Version="3.0">
    <Domain>
        <Grid CollectionType="Temporal" GridType="Collection" Name="Grid">
            <Grid Name="Grid">
                <Geometry GeometryType="XY">
                    <DataItem Dimensions="6 2" Format="HDF"> tmp.h5:/coor </DataItem>
                </Geometry>
                <Topology NumberOfElements="6" TopologyType="Polyvertex">
                    <DataItem Dimensions="6" Format="HDF"> tmp.h5:/conn </DataItem>
                </Topology>
                <Attribute AttributeType="Scalar" Center="Node" Name="/radius">
                    <DataItem Dimensions="6" Format="HDF"> tmp.h5:/radius </DataItem>
                </Attribute>
            </Grid>
        </Grid>
    </Domain>
</Xdmf>
        """

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

        with h5py.File(hdf5_file, "w") as file, xh.Grid(xdmf_file) as xdmf:

            file["coor"] = coor
            file["conn"] = conn
            file["radius"] = radius

            xdmf += xh.Structured(file["coor"], file["conn"])
            xdmf += xh.Attribute(file["radius"], "Node")

        with open(xdmf_file) as file:
            output = file.read()
            output = output.strip().replace("\t", "    ").split("\n")

        expected = expected.strip().split("\n")

        os.remove(hdf5_file)
        os.remove(xdmf_file)

        self.assertEqual(len(output), len(expected))

        for i in range(len(output)):
            self.assertEqual(output[i].strip(), expected[i].strip())

    def test_grid_unstructured(self):

        expected = """
<?xml version="1.0" ?><Xdmf Version="3.0">
    <Domain>
        <Grid CollectionType="Temporal" GridType="Collection" Name="Grid">
            <Grid Name="Grid">
                <Geometry GeometryType="XY">
                    <DataItem Dimensions="6 2" Format="HDF"> tmp.h5:/coor </DataItem>
                </Geometry>
                <Topology NumberOfElements="2" TopologyType="Quadrilateral">
                    <DataItem Dimensions="2 4" Format="HDF"> tmp.h5:/conn </DataItem>
                </Topology>
                <Attribute AttributeType="Scalar" Center="Cell" Name="/stress">
                    <DataItem Dimensions="2" Format="HDF"> tmp.h5:/stress </DataItem>
                </Attribute>
            </Grid>
        </Grid>
    </Domain>
</Xdmf>
        """

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

        with h5py.File(hdf5_file, "w") as file, xh.Grid(root / "grid_unstructured.xdmf") as xdmf:

            file["coor"] = coor
            file["conn"] = conn
            file["stress"] = stress

            xdmf += xh.Unstructured(file["coor"], file["conn"], "Quadrilateral")
            xdmf += xh.Attribute(file["stress"], "Cell")

        with open(root / "grid_unstructured.xdmf") as file:
            output = file.read()
            output = output.strip().replace("\t", "    ").split("\n")

        expected = expected.strip().split("\n")

        os.remove(hdf5_file)
        os.remove(root / "grid_unstructured.xdmf")

        self.assertEqual(len(output), len(expected))

        for i in range(len(output)):
            self.assertEqual(output[i].strip(), expected[i].strip())

    def test_timeseries(self):

        expected = """
<?xml version="1.0" ?><Xdmf Version="3.0">
    <Domain>
        <Grid CollectionType="Temporal" GridType="Collection" Name="TimeSeries">
            <Grid Name="Increment 0">
                <Time Value="0"/>
                <Geometry GeometryType="XY">
                    <DataItem Dimensions="6 2" Format="HDF"> tmp.h5:/coor </DataItem>
                </Geometry>
                <Topology NumberOfElements="2" TopologyType="Quadrilateral">
                    <DataItem Dimensions="2 4" Format="HDF"> tmp.h5:/conn </DataItem>
                </Topology>
                <Attribute AttributeType="Vector" Center="Node" Name="Disp">
                    <DataItem Dimensions="6 3" Format="HDF"> tmp.h5:/disp/0 </DataItem>
                </Attribute>
                <Attribute AttributeType="Scalar" Center="Cell" Name="Stress">
                    <DataItem Dimensions="2" Format="HDF"> tmp.h5:/stress/0 </DataItem>
                </Attribute>
            </Grid>
            <Grid Name="Increment 1">
                <Time Value="1"/>
                <Geometry GeometryType="XY">
                    <DataItem Dimensions="6 2" Format="HDF"> tmp.h5:/coor </DataItem>
                </Geometry>
                <Topology NumberOfElements="2" TopologyType="Quadrilateral">
                    <DataItem Dimensions="2 4" Format="HDF"> tmp.h5:/conn </DataItem>
                </Topology>
                <Attribute AttributeType="Vector" Center="Node" Name="Disp">
                    <DataItem Dimensions="6 3" Format="HDF"> tmp.h5:/disp/1 </DataItem>
                </Attribute>
                <Attribute AttributeType="Scalar" Center="Cell" Name="Stress">
                    <DataItem Dimensions="2" Format="HDF"> tmp.h5:/stress/1 </DataItem>
                </Attribute>
            </Grid>
            <Grid Name="Increment 2">
                <Time Value="2"/>
                <Geometry GeometryType="XY">
                    <DataItem Dimensions="6 2" Format="HDF"> tmp.h5:/coor </DataItem>
                </Geometry>
                <Topology NumberOfElements="2" TopologyType="Quadrilateral">
                    <DataItem Dimensions="2 4" Format="HDF"> tmp.h5:/conn </DataItem>
                </Topology>
                <Attribute AttributeType="Vector" Center="Node" Name="Disp">
                    <DataItem Dimensions="6 3" Format="HDF"> tmp.h5:/disp/2 </DataItem>
                </Attribute>
                <Attribute AttributeType="Scalar" Center="Cell" Name="Stress">
                    <DataItem Dimensions="2" Format="HDF"> tmp.h5:/stress/2 </DataItem>
                </Attribute>
            </Grid>
            <Grid Name="Increment 3">
                <Time Value="3"/>
                <Geometry GeometryType="XY">
                    <DataItem Dimensions="6 2" Format="HDF"> tmp.h5:/coor </DataItem>
                </Geometry>
                <Topology NumberOfElements="2" TopologyType="Quadrilateral">
                    <DataItem Dimensions="2 4" Format="HDF"> tmp.h5:/conn </DataItem>
                </Topology>
                <Attribute AttributeType="Vector" Center="Node" Name="Disp">
                    <DataItem Dimensions="6 3" Format="HDF"> tmp.h5:/disp/3 </DataItem>
                </Attribute>
                <Attribute AttributeType="Scalar" Center="Cell" Name="Stress">
                    <DataItem Dimensions="2" Format="HDF"> tmp.h5:/stress/3 </DataItem>
                </Attribute>
            </Grid>
        </Grid>
    </Domain>
</Xdmf>
        """

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

        with h5py.File(hdf5_file, "w") as file, xh.TimeSeries(root / "timeseries.xdmf") as xdmf:

            file["coor"] = coor
            file["conn"] = conn

            for i in range(4):

                file[f"/stress/{i:d}"] = float(i) * stress
                file[f"/disp/{i:d}"] = float(i) * xh.as3d(disp)

                xdmf += xh.TimeStep()
                xdmf += xh.Unstructured(file["/coor"], file["/conn"], xh.ElementType.Quadrilateral)
                xdmf += xh.Attribute(file[f"/disp/{i:d}"], xh.AttributeCenter.Node, name="Disp")
                xdmf += xh.Attribute(file[f"/stress/{i:d}"], xh.AttributeCenter.Cell, name="Stress")

        with open(root / "timeseries.xdmf") as file:
            output = file.read()
            output = output.strip().replace("\t", "    ").split("\n")

        expected = expected.strip().split("\n")

        os.remove(hdf5_file)
        os.remove(root / "timeseries.xdmf")

        self.assertEqual(len(output), len(expected))

        for i in range(len(output)):
            self.assertEqual(output[i].strip(), expected[i].strip())
