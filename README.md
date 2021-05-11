[![CI](https://github.com/tdegeus/XDMFWrite_h5py/workflows/CI/badge.svg)](https://github.com/tdegeus/XDMFWrite_h5py/actions)
[![readthedocs](https://readthedocs.org/projects/xdmfwrite_h5py/badge/?version=latest)](https://readthedocs.org/projects/xdmfwrite_h5py/badge/?version=latest)

# XDMFWrite_h5py

XDFM meets h5py: Write XDFM files to interpret HDF5 files.

<!-- MarkdownTOC -->

- [Fields](#fields)
    - [Geometry \(nodal-coordinates or vertices\)](#geometry-nodal-coordinates-or-vertices)
    - [Topology \(connectivity\)](#topology-connectivity)
    - [Attribute](#attribute)
- [Short-hand](#short-hand)
    - [Unstructured](#unstructured)
    - [Structured](#structured)
- [Grids](#grids)
    - [Grid](#grid)
    - [TimeSeries](#timeseries)
- [Output](#output)
    - [write](#write)

<!-- /MarkdownTOC -->

## Fields

### Geometry (nodal-coordinates or vertices)

Interpret a DataSet as a Geometry (a.k.a. nodal-coordinates or vertices).

### Topology (connectivity)

Interpret a DataSet as a Topology (a.k.a. connectivity).

### Attribute 

Interpret a DataSet as an Attribute. 

## Short-hand

### Unstructured

Interpret a DataSets as Unstructured. 
The call

```python
Structured(file, "/path/to/geometry", "/path/to/topology", typename)
```

Is simply short for 

```python
Geometry(file, "/path/to/geometry") +
Topology(file, "/path/to/topology", typename)
```

### Structured

Interpret a DataSets as Structured (individual points). 
Use is made of a mock Topology `arange(N)`, with `N` the number of nodes (vertices).
The call

```python
Structured(file, "/path/to/geometry", "/path/to/topology");
```

Is simply short for 

```python
Geometry(file, "/path/to/geometry") +
Topology(file, "/path/to/topology", 'Polyvertex')
```

## Grids

### Grid

Combine fields (e.g. Geometry, Topology, and Attribute) to a single grid.

### TimeSeries

Combine a series of fields (e.g. Geometry, Topology, and Attribute) to a time-series.
The syntax is as follows:

```python
series = TimeSeries()
series.push_back(...)
series.push_back(...)
```

To then write a file simply pass `series` to `write`. 
To alternatively get the sequence of strings of TimeSeries use `series.get()`.

## Output

### write

Write a complete XDMF-file, e.g. from Grid or TimeSeries.
