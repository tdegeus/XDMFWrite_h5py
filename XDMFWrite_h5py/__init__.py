from xml.dom import minidom

import h5py
import numpy as np
from numpy.typing import ArrayLike

from ._version import version  # noqa: F401


def is_correct_shape(shape: ArrayLike, typename: str) -> bool:
    """
    Check that a shape matches the expected shape for a certain type.

    :param shape: Shape of a dataset.
    :param str typename: Element-type (see :py:func:`ElementType`).
    :return: Boolean.
    """

    if len(shape) == 1 and typename == "Polyvertex":
        return True

    if len(shape) != 2:
        return False

    if shape[1] == 3 and typename == "Triangle":
        return True

    if shape[1] == 4 and typename == "Quadrilateral":
        return True

    if shape[1] == 8 and typename == "Hexahedron":
        return True

    return False


def as3d(arg: ArrayLike) -> ArrayLike:
    r"""
    Return a list of vectors as a list of vectors in 3d (as required by ParaView).

    :param [N, d] arg: Input array (``d <= 3``).
    :return: The array zero-padded such that the shape is ``[N, 3]``
    """

    assert arg.ndim == 2

    if arg.shape[1] == 3:
        return arg

    ret = np.zeros([arg.shape[0], 3], dtype=arg.dtype)
    ret[:, : arg.shape[1]] = arg
    return ret


def ElementType() -> list[str]:
    r"""
    Available ElementTypes.

    :return: List with available ElementTypes.
    """
    return ["Polyvertex", "Triangle", "Quadrilateral", "Hexahedron"]


def AttributeCenter() -> list[str]:
    r"""
    Available AttributeCenters.

    :return: list with available AttributeCenters.
    """
    return ["Cell", "Node"]


def Geometry(file: h5py.File, dataset: str) -> list[str]:
    r"""
    Interpret a dataset as a Geometry (aka nodal-coordinates / vertices).

    :param h5py.File file: An open and readable h5py file.
    :param str dataset: Path to the dataset.
    :return: Relevant XDMF code bit (see :py:func:`write` to write as valid XDMF-file).
    """

    shape = file[dataset].shape
    shape_str = " ".join(str(i) for i in shape)
    fname = file.filename

    assert len(shape) == 2

    ret = []

    if shape[1] == 1:
        ret += ['<Geometry GeometryType="X">']
    elif shape[1] == 2:
        ret += ['<Geometry GeometryType="XY">']
    elif shape[1] == 3:
        ret += ['<Geometry GeometryType="XYZ">']
    else:
        raise OSError("Illegal number of dimensions.")

    ret += [f'<DataItem Dimensions="{shape_str}" Format="HDF"> {fname}:{dataset} </DataItem>']
    ret += ["</Geometry>"]

    return ret


def Topology(file: h5py.File, dataset: str, typename: str) -> list[str]:
    r"""
    Interpret a dataset as a Topology (aka connectivity).

    :param h5py.File file: An open and readable h5py file.
    :param str dataset: Path to the dataset.
    :param str typename: Element-type (see :py:func:`ElementType`).
    :return: Relevant XDMF code bit (see :py:func:`write` to write as valid XDMF-file).
    """

    shape = file[dataset].shape
    shape_str = " ".join(str(i) for i in shape)
    fname = file.filename

    if not is_correct_shape(shape, typename):
        raise OSError("Incorrect dimensions for type")

    ret = []
    ret += [f'<Topology NumberOfElements="{shape[0]:d}" TopologyType="{typename}">']
    ret += [f'<DataItem Dimensions="{shape_str}" Format="HDF"> {fname}:{dataset} </DataItem>']
    ret += ["</Topology>"]

    return ret


def Attribute(file: h5py.File, dataset: str, center: str, name: str = None) -> list[str]:
    r"""
    Interpret a dataset as an Attribute.

    :param h5py.File file: An open and readable h5py file.
    :param str dataset: Path to the dataset.
    :param str center: How to center the Attribute (see :py:func:`AttributeCenter`).
    :param str name: Name to use in the XDMF-file. By default the path of the dataset is used.
    :return: Relevant XDMF code bit (see :py:func:`write` to write as valid XDMF-file).
    """

    if name is None:
        name = dataset

    shape = file[dataset].shape
    shape_str = " ".join(str(i) for i in shape)
    fname = file.filename

    assert len(shape) > 0
    assert len(shape) < 3

    if len(shape) == 1:
        t = "Scalar"
    elif len(shape) == 2:
        t = "Vector"
    else:
        raise OSError("Type of data cannot be deduced")

    ret = []
    ret += [f'<Attribute AttributeType="{t}" Center="{center}" Name="{name}">']
    ret += [f'<DataItem Dimensions="{shape_str}" Format="HDF"> {fname}:{dataset} </DataItem>']
    ret += ["</Attribute>"]

    return ret


def Grid(*args: list[str], name: str = "Grid") -> list[str]:
    r"""
    Combine fields (:py:func:`Geometry`, :py:func:`Topology`, and :py:func:`Attribute`)
    to a single grid.

    :type args: List of strings
    :param args: The fields (themselves a sequence of strings) to write.
    :param str name: Name of the grid.
    :return: Relevant XDMF code bit (see :py:func:`write` to write as valid XDMF-file).
    """

    ret = []
    ret += [f'<Grid CollectionType="Temporal" GridType="Collection" Name="{name}">']
    ret += [f'<Grid Name="{name}">']
    for arg in args:
        ret += arg
    ret += ["</Grid>"]
    ret += ["</Grid>"]

    return ret


class TimeSeries:
    r"""
    Combine a series of fields (:py:func:`Geometry`, :py:func:`Topology`, and :py:func:`Attribute`)
    to a time-series.
    """

    def __init__(self, name: str = "TimeSeries"):
        """
        :param name: Name of the TimeSeries.
        """

        self.name = name
        self.n = 0
        self.lines = []

    def push_back(self, *args: list[str], name: str = None, t: float = None):
        r"""
        Add a time-step given by a combination of fields
        (:py:func:`Geometry`, :py:func:`Topology`, and :py:func:`Attribute`).

        :type args: List of strings
        :param args: The fields (themselves a sequence of strings) to write.
        :param str name: Name of the increment.
        :param str t: Time value of the increment.
        """

        if name is None:
            name = "Increment " + str(self.n)
        if t is None:
            t = self.n

        self.lines += [f'<Grid Name="{name}">']
        self.lines += [f'<Time Value="{str(t)}"/>']
        for arg in args:
            self.lines += arg
        self.lines += ["</Grid>"]
        self.n += 1

    def get(self) -> list[str]:
        r"""
        Get sequence of strings to be used in an XDMF-file.

        :return: Relevant XDMF code bit (see :py:func:`write` to write as valid XDMF-file).
        """

        ret = []
        ret += [f'<Grid CollectionType="Temporal" GridType="Collection" Name="{self.name}">']
        ret += self.lines
        ret += ["</Grid>"]
        return ret


def Structured(file: h5py.File, dataset_geometry: str, dataset_topology: str) -> list[str]:
    r"""
    Interpret DataSets as a Structured (individual points).
    This is simply short for the concatenation of ``Geometry(file, "/coor")`` and
    ``Topology(file, "/conn", ElementType::Polyvertex)``.

    :param h5py.File file: An open and readable h5py file.
    :param str dataset_geometry: Path to the Geometry dataset.
    :param str dataset_topology:
        Path to a mock Topology ``numpy.arange(N)``, with ``N`` the number of nodes (vertices).

    :return: Relevant XDMF code bit (see :py:func:`write` to write as valid XDMF-file).
    """

    shape_geometry = file[dataset_geometry].shape
    shape_topology = file[dataset_topology].shape

    assert shape_geometry[0] == shape_topology[0]

    return Geometry(file, dataset_geometry) + Topology(file, dataset_topology, "Polyvertex")


def Unstructured(
    file: h5py.File, dataset_geometry: str, dataset_topology: str, typename: str
) -> list[str]:
    r"""
    Interpret DataSets as a Unstructured
    (Geometry and Topology, aka nodal-coordinates and connectivity). This is simply short for the
    concatenation of ``Geometry(file, "/coor")`` and
    ``Topology(file, "/conn", typename)``.

    :param h5py.File file: An open and readable h5py file.
    :param str dataset_geometry: Path to the Geometry dataset.
    :param str dataset_topology: Path to a mock Topology == arange(N), N = #nodes (vertices).
    :param str typename: Element-type (see :py:func:`ElementType`).
    :return: Relevant XDMF code bit (see :py:func:`write` to write as valid XDMF-file).
    """
    return Geometry(file, dataset_geometry) + Topology(file, dataset_topology, typename)


def write(arg: list[str], filename: str = None):
    r"""
    Write a complete XDMF-file, for example from Grid or TimeSeries.

    :type args: List of strings
    :param args: The data (any of the XDMFWrite_h5py-classes or a sequence of strings) to write.
    :param str filename: File to write to. Optional.
    """

    if isinstance(arg, TimeSeries):
        lines = arg.get()
    elif isinstance(arg, str):
        lines = [arg]
    else:
        lines = arg

    ret = []
    ret += ['<Xdmf Version="3.0">']
    ret += ["<Domain>"]
    ret += lines
    ret += ["</Domain>"]
    ret += ["</Xdmf>"]
    ret = minidom.parseString("\n".join(ret)).toprettyxml(newl="")

    if filename is not None:
        with open(filename, "w") as file:
            file.write(ret)

    return ret
