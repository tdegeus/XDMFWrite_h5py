def indenter():
    return " " * 4


def indent(n, lines, start, stop):
    i = n * indenter()
    for j in range(start, stop):
        lines[j] = i + lines[j]
    return lines


def check_shape(shape, typename):
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


def join_as_string(arg, sep):
    return sep.join([str(i) for i in arg])
