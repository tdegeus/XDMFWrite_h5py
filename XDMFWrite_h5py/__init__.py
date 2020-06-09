import h5py
from .detail import *

__version__ = '0.0.1'


def ElementType():
    r'''
Returns list with available ElementTypes
    '''
    return [
        'Polyvertex',
        'Triangle',
        'Quadrilateral',
        'Hexahedron']


def AttributeCenter():
    r'''
Returns list with available AttributeCenters
    '''
    return [
        'Cell',
        'Node']


def Geometry(file, dataset):
    r'''
Interpret a DataSet as a Geometry (a.k.a. nodal-coordinates or vertices).

:arguments:

    **file** (``<h5py.File>``)
        An open and readable h5py file.

    **dataset** (``<str>``)
        Path to the DataSet.

:returns:

    Sequence of strings to be used in an XDMF-file.
    '''
    ret = []
    shape = file[dataset].shape
    fname = file.filename

    assert len(shape) == 2

    if (shape[1] == 1):
        ret += ["<Geometry GeometryType=\"X\">"]
    elif (shape[1] == 2):
        ret += ["<Geometry GeometryType=\"XY\">"]
    elif (shape[1] == 3):
        ret += ["<Geometry GeometryType=\"XYZ\">"]
    else:
        raise IOError("Illegal number of dimensions.")

    ret += [
        indenter() + "<DataItem Dimensions=\"" + str(shape[0]) + " " +
        str(shape[1]) + "\" Format=\"HDF\">" + fname + ":" + dataset +
        "</DataItem>"]

    ret += ["</Geometry>"]

    return ret

def Topology(file, dataset, typename):
    r'''
Interpret a DataSet as a Topology (a.k.a. connectivity).

:arguments:

    **file** (``<h5py.File>``)
        An open and readable h5py file.

    **dataset** (``<str>``)
        Path to the DataSet.

    **typename** (``<str>``)
        Element-type (see ElementType).

:returns:

    Sequence of strings to be used in an XDMF-file.
    '''
    ret = []
    shape = file[dataset].shape
    fname = file.filename

    assert check_shape(shape, typename)

    ret += [
        "<Topology NumberOfElements=\"" + str(shape[0]) + "\" TopologyType=\"" +
        typename + "\">"]

    ret += [
        indenter() + "<DataItem Dimensions=\"" + join_as_string(shape, " ") +
        "\" Format=\"HDF\">" + fname + ":" + dataset +
        "</DataItem>"]

    ret += ["</Topology>"]

    return ret;


def Attribute(file, dataset, center, name=None):
    r'''
Interpret a DataSet as an Attribute.

:arguments:

    **file** (``<h5py.File>``)
        An open and readable h5py file.

    **dataset** (``<str>``)
        Path to the DataSet.

    **center** (``<str>``)
        How to center the Attribute (see AttributeCenter).

:options:

    **name** (``<str>``)
        Name to use in the XDMF-file. By default the path of the DataSet is used.

:returns:

    Sequence of strings to be used in an XDMF-file.
    '''
    if name is None:
        name = dataset

    ret = []
    shape = file[dataset].shape
    fname = file.filename

    assert len(shape) > 0
    assert len(shape) < 3

    if (len(shape) == 1):
        t = "Scalar"
    elif (len(shape) == 2):
        t = "Vector"
    else:
        raise IOError("Type of data cannot be deduced")

    ret += [
        "<Attribute AttributeType=\"" + t + "\" Center=\"" + center +
        "\" Name=\"" + name + "\">"]

    ret += [
        indenter() + "<DataItem Dimensions=\"" + join_as_string(shape, " ") +
        "\" Format=\"HDF\">" + fname + ":" + dataset + "</DataItem>"]

    ret += ["</Attribute>"]

    return ret


def Grid(*args, name='Grid'):
    r'''
Combine fields (e.g. Geometry, Topology, and Attribute) to a single grid.

:arguments:

    **args** (``<list<str>>``)
        The fields (themselves a sequence of strings) to write.

:options:

    **name** ([``'Grid'``] | ``<str>``)
        Name of the grid.

:returns:

    Sequence of strings to be used in an XDMF-file.
    '''
    ret = []
    ret += [
        "<Grid CollectionType=\"Temporal\" GridType=\"Collection\" Name=\"" + name + "\">"]
    ret += ["<Grid Name=\"" + name + "\">"]
    for arg in args:
        ret += arg
    ret += ["</Grid>"]
    ret += ["</Grid>"]
    indent(2, ret, 2, len(ret) - 2)
    return ret


class TimeSeries:
    r'''
Combine a series of fields (e.g. Geometry, Topology, and Attribute) to a time-series.
    '''


    def __init__(self, name='TimeSeries'):
        self.name = name
        self.n = 0
        self.lines = []


    def push_back(self, *args, name=None, t=None):
        r'''
Add a time-step given by a combination of fields (e.g. Geometry, Topology, and Attribute).

:arguments:

    **args** (``<list<str>>``)
        The fields (themselves a sequence of strings) to write.

:options:

    **name** (``<str>``)
        Name of the increment.

    **t** (``<str>``)
        Time value of the increment.
        '''
        if name is None:
            name = "Increment " + str(self.n)
        if t is None:
            t = self.n

        self.lines += ["<Grid Name=\"" + name + "\">"]
        self.lines += [indenter() + "<Time Value=\"" + str(t) + "\"/>"]
        start = len(self.lines)
        for arg in args:
            self.lines += arg
        stop = len(self.lines)
        indent(1, self.lines, start, stop)
        self.lines += ["</Grid>"]
        self.n += 1


    def get():
        r'''
Get sequence of strings to be used in an XDMF-file.

:returns:

    Sequence of strings to be used in an XDMF-file.
        '''
        ret = []
        ret += [
            "<Grid CollectionType=\"Temporal\" GridType=\"Collection\" Name=\"" + self.name + "\">"]
        ret += self.lines
        ret += ["</Grid>"]
        indent(1, ret, 1, len(ret) - 1)
        return ret


def Structured(file, dataset_geometry, dataset_topology):
    r'''
Interpret a DataSets as a Structured (individual points). This is simply short for the
concatenation of ``Geometry(file, "/coor")`` and
``Topology(file, "/conn", ElementType::Polyvertex)``.

:arguments:

    **file** (``<h5py.File>``)
        An open and readable h5py file.

    **dataset_geometry** (``<str>``)
        Path to the Geometry DataSet.

    **dataset_topology** (``<str>``)
        Path to a mock Topology arange(N), with N the number of nodes (vertices).

:returns:

    Sequence of strings to be used in an XDMF-file.
    '''
    shape_geometry = file[dataset_geometry].shape
    shape_topology = file[dataset_topology].shape

    assert shape_geometry[0] == shape_topology[0]

    return Geometry(file, dataset_geometry) + Topology(file, dataset_topology, 'Polyvertex')


def Unstructured(file, dataset_geometry, dataset_topology, typename):
    r'''
Interpret a DataSets as a Unstructured
(Geometry and Topology / nodal-coordinates and connectivity). This is simply short for the
concatenation of ``Geometry(file, "/coor")`` and
``Topology(file, "/conn", typename)``.

:arguments:

    **file** (``<h5py.File>``)
        An open and readable h5py file.

    **dataset_geometry** (``<str>``)
        Path to the Geometry DataSet.

    **dataset_topology** (``<str>``)
        Path to a mock Topology arange(N), with N the number of nodes (vertices).

    **typename** (``<str>``)
        Element-type (see ElementType).

:returns:

    Sequence of strings to be used in an XDMF-file.
    '''
    return Geometry(file, dataset_geometry) + Topology(file, dataset_topology, typename)


def write(arg, filename=None):
    r'''
Write a complete XDMF-file, e.g. from Grid or TimeSeries.

:arguments:

    **arg** (``<list<str>>``)
        The data (any of the XDMFWrite_h5py-classes or a sequence of strings) to write.

:options:

    **filename** (``<str>``)
        File to write to. Optional.
    '''
    ret = []
    try:
        lines = arg.get()
    except:
        lines = arg
    ret += ["<Xdmf Version=\"3.0\">"]
    ret += [indenter() + "<Domain>"]
    ret += lines
    ret += [indenter() + "</Domain>"]
    ret += ["</Xdmf>"]
    indent(2, ret, 2, len(ret) - 2);
    ret = '\n'.join(ret)

    if filename is not None:
        open(filename, 'w').write(ret)

    return ret
