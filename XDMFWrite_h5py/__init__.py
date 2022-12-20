import os
import pathlib
from enum import StrEnum
from xml.dom import minidom

import h5py
import numpy as np
from numpy.typing import ArrayLike

from ._version import version  # noqa: F401


class ElementType(StrEnum):
    """
    Element types:

    -   Polyvertex
    -   Triangle
    -   Quadrilateral
    -   Hexahedron
    """

    Polyvertex = "Polyvertex"
    Triangle = "Triangle"
    Quadrilateral = "Quadrilateral"
    Hexahedron = "Hexahedron"


class AttributeCenter(StrEnum):
    """
    Attribute centers:

    -   Cell
    -   Node
    """

    Cell = "Cell"
    Node = "Node"


def shape_is_correct(shape: ArrayLike, element_type: ElementType) -> bool:
    """
    Check that a shape matches the expected shape for a certain type.

    :param shape: Shape of a dataset.
    :param element_type: Element-type (see :py:class:`ElementType`).
    :return: `True` is the shape is as expected (no guarantee that the data is correct).
    """

    if len(shape) == 1 and element_type == ElementType.Polyvertex:
        return True

    if len(shape) != 2:
        return False

    if shape[1] == 3 and element_type == ElementType.Triangle:
        return True

    if shape[1] == 4 and element_type == ElementType.Quadrilateral:
        return True

    if shape[1] == 8 and element_type == ElementType.Hexahedron:
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


class Field:
    """
    Base class of XDMF-fields.

    :param dataset: HDF5-dataset.
    :param name: Name to use in the XDMF-file [default: same as dataset].
    """

    def __init__(self, dataset: h5py.File, name: str):

        self.filename = dataset.parent.file.filename
        self.path = dataset.name
        self.shape = dataset.shape
        self.shape_str = " ".join(str(i) for i in self.shape)
        self.name = name

        if self.name is None:
            self.name = dataset.name

    def __iter__(self):
        return iter(self.__list__())

    def relpath(self, path: str | pathlib.Path) -> str:
        """
        Change the path of the HDF5-file to a path relative to another file (the XDMF-file).
        :param path: Path to make the file relative to.
        """
        self.filename = os.path.relpath(self.filename, pathlib.Path(path).parent)

    def __str__(self) -> str:
        """
        Return XML snippet.
        """
        return minidom.parseString("\n".join(self.__list__())).toprettyxml(newl="")


class Geometry(Field):
    """
    Interpret a dataset as a Geometry (aka nodal-coordinates / vertices).

    :param dataset: The dataset.
    """

    def __init__(self, dataset: h5py.Group):
        super().__init__(dataset, "Geometry")
        assert len(self.shape) == 2

    def __list__(self) -> list[str]:
        """
        :return: XDMF code snippet.
        """

        ret = []

        if self.shape[1] == 1:
            ret += ['<Geometry GeometryType="X">']
        elif self.shape[1] == 2:
            ret += ['<Geometry GeometryType="XY">']
        elif self.shape[1] == 3:
            ret += ['<Geometry GeometryType="XYZ">']
        else:
            raise OSError("Illegal number of dimensions.")

        ret += [
            (
                f'<DataItem Dimensions="{self.shape_str}" Format="HDF"> '
                f"{self.filename}:{self.path} </DataItem>"
            )
        ]
        ret += ["</Geometry>"]

        return ret


class Topology(Field):
    """
    Interpret a dataset as a Topology (aka connectivity).

    :param dataset: Dataset.
    :param element_type: Element-type (see :py:class:`ElementType`).
    """

    def __init__(self, dataset: h5py.Group, element_type: ElementType):
        super().__init__(dataset, "Topology")
        self.element_type = element_type

        if not shape_is_correct(self.shape, self.element_type):
            raise OSError("Incorrect dimensions for type")

    def __list__(self) -> list[str]:
        """
        :return: XDMF code snippet.
        """

        ret = []
        ret += [
            f'<Topology NumberOfElements="{self.shape[0]:d}" TopologyType="{self.element_type}">'
        ]
        ret += [
            (
                f'<DataItem Dimensions="{self.shape_str}" Format="HDF"> '
                f"{self.filename}:{self.path} </DataItem>"
            )
        ]
        ret += ["</Topology>"]

        return ret


class Attribute(Field):
    """
    Interpret a dataset as an Attribute.

    :param dataset: Dataset.
    :param center: How to center the Attribute (see :py:class:`AttributeCenter`).
    :param name: Name to use in the XDMF-file [default: same as dataset]
    """

    def __init__(self, dataset: h5py.File, center: str, name: str = None):
        super().__init__(dataset, name)
        self.center = center
        assert len(self.shape) > 0
        assert len(self.shape) < 3

    def __list__(self) -> list[str]:
        """
        :return: XDMF code snippet.
        """

        if len(self.shape) == 1:
            t = "Scalar"
        elif len(self.shape) == 2:
            t = "Vector"
        else:
            raise OSError("Type of data cannot be deduced")

        ret = []
        ret += [f'<Attribute AttributeType="{t}" Center="{self.center}" Name="{self.name}">']
        ret += [
            (
                f'<DataItem Dimensions="{self.shape_str}" Format="HDF"> '
                f"{self.filename}:{self.path} </DataItem>"
            )
        ]
        ret += ["</Attribute>"]

        return ret


def _asfile(lines: list[str]) -> str:
    """
    Convert a list of lines to an XDMF-file.
    :param lines: List of lines.
    :return: XDMF-file.
    """
    ret = []
    ret += ['<Xdmf Version="3.0">']
    ret += ["<Domain>"]
    ret += lines
    ret += ["</Domain>"]
    ret += ["</Xdmf>"]
    return ret


class File:
    """
    Base class of XDMF-files.
    The class allows (requires) to open the file in context-manager mode.

    :param filename: Filename of the XDMF-file.
    :param mode: Write mode.
    """

    def __init__(self, filename: str, mode: str = "w"):
        self.filename = filename
        self.mode = mode
        self.lines = []

    def __iter__(self):
        return iter(self.__list__())

    def __str__(self) -> str:
        return minidom.parseString("\n".join(self.__list__())).toprettyxml(newl="")

    def __list__(self) -> list[str]:
        return _asfile(self.lines)

    def __add__(self, content: Field | list[str] | str):
        """
        Add content to file.
        :param content: Content to add.
        """

        if isinstance(content, list):
            self.lines += content
            return self

        if isinstance(content, Field):
            content.relpath(self.filename)  # todo: operation that does not modify "content"
            self.lines += list(content)
            return self

        self.lines += [content]
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        with open(self.filename, self.mode) as file:
            file.write(str(self))


class TimeStep:
    """
    Mark a time-step in a :py:class:`TimeSeries`.

    :param name: Name of the time step.
    :param time: Value of time
    """

    def __init__(self, name: str = None, time: float = None):
        self.name = name
        self.time = time


class Grid(File):
    """
    XDMF-file with one grid. The grid can contain:

    -   :py:class:`Geometry`.
    -   :py:class:`Topology`.
    -   :py:class:`Attribute`.
    -   :py:class:`Structured`.
    -   :py:class:`Unstructured`.

    See :py:class:`Structured` or :py:class:`Unstructured` for suggested usage.

    :param filename: Filename of the XDMF-file.
    :param mode: Write mode.
    :param name: Name of the grid.
    """

    def __init__(self, filename: str, mode: str = "w", name: str = "Grid"):
        super().__init__(filename, mode)
        self.name = name

    def __list__(self) -> list[str]:

        ret = []
        ret += [f'<Grid CollectionType="Temporal" GridType="Collection" Name="{self.name}">']
        ret += [f'<Grid Name="{self.name}">']
        ret += self.lines
        ret += ["</Grid>"]
        ret += ["</Grid>"]

        return _asfile(ret)


class TimeSeries(File):
    r"""
    XDMF-file with a series of 'time-steps' of grids, separated by :py:class:`TimeStep`.
    The grid can contain:

    -   :py:class:`Geometry`.
    -   :py:class:`Topology`.
    -   :py:class:`Attribute`.
    -   :py:class:`Structured`.
    -   :py:class:`Unstructured`.

    Usage::

        with h5py.File("my.h5", "w") as file, xh.TimeSeries("my.xdmf") as xdmf:

            file["coor"] = coor
            file["conn"] = conn

            for i in range(4):

                file[f"/stress/{i:d}"] = float(i) * stress
                file[f"/disp/{i:d}"] = float(i) * xh.as3d(disp)

                xdmf += xh.TimeStep()
                xdmf += xh.Unstructured(file["coor"], file["conn"], xh.ElementType.Quadrilateral)
                xdmf += xh.Attribute(file[f"/disp/{i:d}"], xh.AttributeCenter.Node, name="Disp")
                xdmf += xh.Attribute(file[f"/stress/{i:d}"], xh.AttributeCenter.Cell, name="Stress")

    :param name: Name of the TimeSeries.
    """

    def __init__(self, filename: str, mode: str = "w", name: str = "TimeSeries"):
        super().__init__(filename, mode)
        self.name = name
        self.start = []
        self.settings = []

    def __add__(self, other: TimeStep | Field | list[str] | str):

        if isinstance(other, TimeStep):
            self.start += [len(self.lines)]
            self.settings += [other]
            return self

        super().__add__(other)
        return self

    def __list__(self) -> list[str]:

        ret = []
        ret += [f'<Grid CollectionType="Temporal" GridType="Collection" Name="{self.name}">']

        start = [i for i in self.start] + [len(self.lines)]

        for i in range(len(self.start)):

            if self.settings[i].name is None:
                name = f"Increment {i:d}"
            else:
                name = self.settings[i].name

            if self.settings[i].time is None:
                t = i
            else:
                t = self.settings[i].time

            ret += [f'<Grid Name="{name}">']
            ret += [f'<Time Value="{str(t)}"/>']
            ret += self.lines[start[i] : start[i + 1]]  # noqa: E203
            ret += ["</Grid>"]

        ret += ["</Grid>"]
        return _asfile(ret)


class _Grid(Field):
    """
    Base class for a grid.
    """

    def __init__(
        self, dataset_geometry: h5py.Group, dataset_topology: h5py.Group, element_type: ElementType
    ):
        self.geometry = Geometry(dataset_geometry)
        self.topology = Topology(dataset_topology, element_type)

    def __iter__(self):
        return iter(self.__list__())

    def relpath(self, path: str | pathlib.Path):
        self.geometry.relpath(path)
        self.topology.relpath(path)

    def __list__(self) -> list[str]:
        return list(self.geometry) + list(self.topology)


class Structured(_Grid):
    """
    Interpret DataSets as a Structured (individual points).
    Short for the concatenation of:

    -   ``Geometry(file["coor"])``
    -   ``Topology(file["conn"], ElementType.Polyvertex)``.

    Usage::

        with h5py.File("my.h5", "w") as file, xh.Grid("my.xdmf") as xdmf:

            file["coor"] = coor
            file["conn"] = conn
            file["radius"] = radius

            xdmf += xh.Structured(file["coor"], file["conn"])
            xdmf += xh.Attribute(file["radius"], "Node")

    :param dataset_geometry: Geometry dataset.
    :param dataset_topology: Mock Topology ``numpy.arange(N)``, ``N`` = number of nodes (vertices).
    """

    def __init__(self, dataset_geometry: h5py.Group, dataset_topology: h5py.Group):
        super().__init__(dataset_geometry, dataset_topology, ElementType.Polyvertex)


class Unstructured(_Grid):
    """
    Interpret DataSets as a Unstructured
    (Geometry and Topology, aka nodal-coordinates and connectivity).
    Short for the concatenation of:

    -   ``Geometry(file["coor"])``
    -   ``Topology(file["conn"], element_type)``.

    Usage::

        with h5py.File("my.h5", "w") as file, xh.Unstructured("my.xdmf") as xdmf:

            file["coor"] = coor
            file["conn"] = conn
            file["stress"] = stress

            xdmf += xh.Unstructured(file["coor"], file["conn"], "Quadrilateral")
            xdmf += xh.Attribute(file["stress"], "Cell")

    :param dataset_geometry: Path to the Geometry dataset.
    :param dataset_topology: Path to the Topology dataset.
    :param element_type: Element-type (see :py:class:`ElementType`).
    """

    def __init__(
        self, dataset_geometry: h5py.Group, dataset_topology: h5py.Group, element_type: ElementType
    ):
        super().__init__(dataset_geometry, dataset_topology, element_type)
