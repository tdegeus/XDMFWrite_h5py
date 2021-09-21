import h5py
import numpy as np
from numpy.typing import ArrayLike

from . import detail
from ._version import version  # noqa: F401


def as3d(arg: ArrayLike) -> ArrayLike:
    r"""
    Return a list of vectors as a list of vectors in 3d (as required by ParaView).

    :param [N, d] arg: Input array (`d <= 3`).
    :return: The array zero-padded such that the shape is ``[N, 3]``
    """

    assert arg.ndim == 2

    if arg.shape[1] == 3:
        return arg

    ret = np.zeros([arg.shape[0], 3], dtype=arg.dtype)
    ret[:, : arg.shape[1]] = arg
    return ret


def ElementType():
    r"""
    Available ElementTypes.

    :return: List with available ElementTypes.
    """
    return ["Polyvertex", "Triangle", "Quadrilateral", "Hexahedron"]


def AttributeCenter():
    r"""
    Available AttributeCenters.

    :return: list with available AttributeCenters.
    """
    return ["Cell", "Node"]


def Geometry(file: h5py.File, dataset):
    r"""
    Interpret a DataSet as a Geometry (alias: nodal-coordinates, vertices).

    :param h5py.File file: An open and readable h5py file.
    :param str dataset: Path to the DataSet.
    :return: Sequence of strings to be used in an XDMF-file.
    """
    ret = []
    shape = file[dataset].shape
    fname = file.filename

    assert len(shape) == 2

    if shape[1] == 1:
        ret += ['<Geometry GeometryType="X">']
    elif shape[1] == 2:
        ret += ['<Geometry GeometryType="XY">']
    elif shape[1] == 3:
        ret += ['<Geometry GeometryType="XYZ">']
    else:
        raise OSError("Illegal number of dimensions.")

    ret += [
        detail.indenter()
        + '<DataItem Dimensions="'
        + str(shape[0])
        + " "
        + str(shape[1])
        + '" Format="HDF">'
        + fname
        + ":"
        + dataset
        + "</DataItem>"
    ]

    ret += ["</Geometry>"]

    return ret


def Topology(file, dataset, typename):
    r"""
    Interpret a DataSet as a Topology (alias: connectivity).

    :param h5py.File file: An open and readable h5py file.
    :param str dataset: Path to the DataSet.
    :param str typename: Element-type (see ElementType).
    :return: Sequence of strings to be used in an XDMF-file.
    """
    ret = []
    shape = file[dataset].shape
    fname = file.filename

    assert detail.check_shape(shape, typename)

    ret += [
        '<Topology NumberOfElements="'
        + str(shape[0])
        + '" TopologyType="'
        + typename
        + '">'
    ]

    ret += [
        detail.indenter()
        + '<DataItem Dimensions="'
        + detail.join_as_string(shape, " ")
        + '" Format="HDF">'
        + fname
        + ":"
        + dataset
        + "</DataItem>"
    ]

    ret += ["</Topology>"]

    return ret


def Attribute(file, dataset, center, name=None):
    r"""
    Interpret a DataSet as an Attribute.

    :param h5py.File file: An open and readable h5py file.
    :param str dataset: Path to the DataSet.
    :param str center: How to center the Attribute (see AttributeCenter).
    :param str name: Name to use in the XDMF-file. By default the path of the DataSet is used.
    :return: Sequence of strings to be used in an XDMF-file.
    """
    if name is None:
        name = dataset

    ret = []
    shape = file[dataset].shape
    fname = file.filename

    assert len(shape) > 0
    assert len(shape) < 3

    if len(shape) == 1:
        t = "Scalar"
    elif len(shape) == 2:
        t = "Vector"
    else:
        raise OSError("Type of data cannot be deduced")

    ret += [
        '<Attribute AttributeType="'
        + t
        + '" Center="'
        + center
        + '" Name="'
        + name
        + '">'
    ]

    ret += [
        detail.indenter()
        + '<DataItem Dimensions="'
        + detail.join_as_string(shape, " ")
        + '" Format="HDF">'
        + fname
        + ":"
        + dataset
        + "</DataItem>"
    ]

    ret += ["</Attribute>"]

    return ret


def Grid(*args, name="Grid"):
    r"""
    Combine fields (e.g. Geometry, Topology, and Attribute) to a single grid.

    :type args: List of strings
    :param args: The fields (themselves a sequence of strings) to write.
    :param str name: Name of the grid.
    :return: Sequence of strings to be used in an XDMF-file.
    """
    ret = []
    ret += [
        '<Grid CollectionType="Temporal" GridType="Collection" Name="' + name + '">'
    ]
    ret += ['<Grid Name="' + name + '">']
    for arg in args:
        ret += arg
    ret += ["</Grid>"]
    ret += ["</Grid>"]
    detail.indent(2, ret, 2, len(ret) - 2)
    return ret


class TimeSeries:
    r"""
    Combine a series of fields (e.g. Geometry, Topology, and Attribute) to a time-series.
    """

    def __init__(self, name="TimeSeries"):
        self.name = name
        self.n = 0
        self.lines = []

    def push_back(self, *args, name=None, t=None):
        r"""
        Add a time-step given by a combination of fields (e.g. Geometry, Topology, and Attribute).

        :type args: List of strings
        :param args: The fields (themselves a sequence of strings) to write.
        :param str name: Name of the increment.
        :param str t: Time value of the increment.
        """
        if name is None:
            name = "Increment " + str(self.n)
        if t is None:
            t = self.n

        self.lines += ['<Grid Name="' + name + '">']
        self.lines += [detail.indenter() + '<Time Value="' + str(t) + '"/>']
        start = len(self.lines)
        for arg in args:
            self.lines += arg
        stop = len(self.lines)
        detail.indent(1, self.lines, start, stop)
        self.lines += ["</Grid>"]
        self.n += 1

    def get(self):
        r"""
        Get sequence of strings to be used in an XDMF-file.

        :return: Sequence of strings to be used in an XDMF-file.
        """
        ret = []
        ret += [
            '<Grid CollectionType="Temporal" GridType="Collection" Name="'
            + self.name
            + '">'
        ]
        ret += self.lines
        ret += ["</Grid>"]
        detail.indent(1, ret, 1, len(ret) - 1)
        return ret


def Structured(file, dataset_geometry, dataset_topology):
    r"""
    Interpret a DataSets as a Structured (individual points). This is simply short for the
    concatenation of ``Geometry(file, "/coor")`` and
    ``Topology(file, "/conn", ElementType::Polyvertex)``.

    :param h5py.File file: An open and readable h5py file.
    :param str dataset_geometry: Path to the Geometry DataSet.
    :param str dataset_topology:
        Path to a mock Topology ``numpy.arange(N)``, with ``N`` the number of nodes (vertices).

    :return: Sequence of strings to be used in an XDMF-file.
    """
    shape_geometry = file[dataset_geometry].shape
    shape_topology = file[dataset_topology].shape

    assert shape_geometry[0] == shape_topology[0]

    return Geometry(file, dataset_geometry) + Topology(
        file, dataset_topology, "Polyvertex"
    )


def Unstructured(file, dataset_geometry, dataset_topology, typename):
    r"""
    Interpret a DataSets as a Unstructured
    (Geometry and Topology / nodal-coordinates and connectivity). This is simply short for the
    concatenation of ``Geometry(file, "/coor")`` and
    ``Topology(file, "/conn", typename)``.

    :param h5py.File file: An open and readable h5py file.
    :param str dataset_geometry: Path to the Geometry DataSet.
    :param str dataset_topology: Path to a mock Topology == arange(N), N = #nodes (vertices).
    :param str typename: Element-type (see ElementType).
    :return: Sequence of strings to be used in an XDMF-file.
    """
    return Geometry(file, dataset_geometry) + Topology(file, dataset_topology, typename)


def write(arg, filename=None):
    r"""
    Write a complete XDMF-file, e.g. from Grid or TimeSeries.

    :type args: List of strings
    :param args: The data (any of the XDMFWrite_h5py-classes or a sequence of strings) to write.
    :param str filename: File to write to. Optional.
    """
    ret = []
    try:
        lines = arg.get()
    except:  # noqa: E722
        lines = arg
    ret += ['<Xdmf Version="3.0">']
    ret += [detail.indenter() + "<Domain>"]
    ret += lines
    ret += [detail.indenter() + "</Domain>"]
    ret += ["</Xdmf>"]
    detail.indent(2, ret, 2, len(ret) - 2)
    ret = "\n".join(ret)

    if filename is not None:
        with open(filename, "w") as file:
            file.write(ret)

    return ret
