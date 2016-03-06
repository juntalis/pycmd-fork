# encoding: utf-8
"""
tchar.py
I've been having a bit of trouble finding any documentation that
details the specifics of Window's support for Unicode in earlier
versions of Windows. That being the case, I've used the "TCHAR"
approach, just in case I need to offer an implementation that
uses the ANSI API.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import os, ctypes, _ctypes
from functools import wraps as _wraps

## TCHAR configuration
# TODO: This is just a placeholder. Need to look into when unicode filepaths were introduced in Windows, and
TCHAR_UNICODE = os.path.supports_unicode_filenames

# Set the appropriate string char/string variations.
if TCHAR_UNICODE:
    _T = tstr = unicode
    TCHAR_SUFFIX = 'W'
    tstring_at = ctypes.wstring_at
    TCHAR = c_tchar = ctypes.c_wchar
    LPCTSTR = LPTSTR = c_tchar_p = ctypes.c_wchar_p
    create_tstring_buffer = ctypes.create_unicode_buffer
else:
    _T = tstr= str
    TCHAR_SUFFIX = 'A'
    tstring_at = ctypes.string_at
    TCHAR = c_tchar = ctypes.c_char
    LPCTSTR = LPTSTR = c_tchar_p = ctypes.c_char_p
    create_tstring_buffer = ctypes.create_string_buffer

_TFUNC = lambda name: name + TCHAR_SUFFIX
_TPAIR = lambda name, dll: (_TFUNC(name), dll,)

class WinFunctionTypeWrapper(object):
    __slots__ = ('_functype', '_funcdoc', '_use_tchar',)

    def __init__(self, restype, *argtypes, **kwargs):
        """
        Same arguments as ctypes.WINFUNCTYPE, with the added ability to specify use_tchar=True.
        """
        self._use_tchar = kwargs.pop('use_tchar', False)
        self._funcdoc = kwargs.pop('doc', None)
        self._functype = ctypes.WINFUNCTYPE(restype, *argtypes, **kwargs)

    def __call__(self, procpair, paramflags=None):
        """
        :param procpair:(name,dll,)
        :type procpair:tuple
        :param paramflags:Optional paramflags args. See ctypes documentation.
        :type paramflags:tuple
        :return:Callable function pointer
        :rtype:_ctypes._CFuncPtr
        """
        # Check if we need to add TCHAR_SUFFIX
        if self._use_tchar:
            procpair = _TPAIR(*procpair)

        # Apply our prototype
        proto = self._functype(procpair, paramflags)

        # Attach documentation if any was specified
        if self._funcdoc is not None:
            proto.__doc__ = self._funcdoc

        return proto

@_wraps(ctypes.WINFUNCTYPE)
def WINFUNCTYPE(restype, *argtypes, **kwargs):
    return WinFunctionTypeWrapper(restype, *argtypes, **kwargs)

class WinDLL(ctypes.WinDLL):

    @_wraps(ctypes.WinDLL.__getitem__)
    def __getitem__(self, name_or_ordinal):
        if isinstance(name_or_ordinal, basestring) and name_or_ordinal[-1] == 'T':
            name_or_ordinal = _TFUNC(name_or_ordinal[:-1])
        return super(WinDLL, self).__getitem__(name_or_ordinal)

__all__ = [ '_T', 'tstr', 'tstring_at', 'c_tchar', 'c_tchar_p', 'create_tstring_buffer',
            'WINFUNCTYPE', 'WinDLL', 'TCHAR', 'LPTSTR', 'LPCTSTR', '_ctypes', 'ctypes', '_TFUNC' ]
