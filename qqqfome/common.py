from . import strings as s


def check_type(var, name, t):
    if not isinstance(t, type(str)):
        t = type(t)
    if not isinstance(var, t):
        raise ValueError(s.type_error.format(
            name, str(t), str(type(var))))