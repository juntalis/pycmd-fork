# encoding: utf-8
"""
miscutil.py
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from functools import wraps as _wraps

##############
# Decorators #
##############

def once(func):
    """
    Fires once, then returns the same result for every call after that.

    :param function func: The decorated function
    :rtype: function
    """
    func._lazycall = (False, None,)

    # noinspection PyProtectedMember
    @_wraps(func)
    def lazy_deco(*args, **kwargs):
        if not func._lazycall[0]:
            func._lazycall = (True, func(*args, **kwargs),)
        return func._lazycall[1]
    return lazy_deco


def memoize(func):
    """
    From the Python Decorator Library (http://wiki.python.org/moin/PythonDecoratorLibrary):
    Cache the results of a function call with specific arguments. Note that this decorator ignores **kwargs.

    :param function func: The decorated function
    :rtype: function
    """
    cache = func._cache = dict()

    @_wraps(func)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = func(*args, **kwargs)
        return cache[args]
    return memoizer

def membername(obj, raise_error=True):
    """
    Given a module-level function/class, generate a "pretty" name
    based on module and name of the object.
    :param obj: Module-level object to get the name of
    :param raise_error: Whether or not to raise errors on failure
    :type raise_error: object
    :return: name or None (if `raise_error` is `False`)
    :rtype: str | None
    :raises ReferenceError: if `obj` is None and `raise_error` is `True`
    :raises AttributeError: if `obj` is missing name or module attrs
    """
    if obj is None:
        if not raise_error: return None
        raise ReferenceError('obj cannot be None!')
    elif not hasattr(obj, '__module__') or not hasattr(obj, '__name__'):
        if not raise_error: return None
        raise AttributeError('obj must have __module__ and __name__ fields!')

    # Module name defaults to 'PyCmd' when non-existent or '__main__'
    modobj, modname = obj.__module__, None
    if not hasattr(modobj, '__name__') or modobj.__name__ == '__main__':
        modname = 'PyCmd'
    else:
        modname = modobj.__name__

    return '{0}.{1}'.format(modname, obj.__name__)
