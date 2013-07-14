# encoding: utf-8
"""
pycmd
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
from libc.string cimport const_char, const_void
from cpython.string cimport PyString_FromStringAndSize

cdef extern from "msvcppy.h":
	# Registry stuff
	ctypedef void* PVOID
	ctypedef long LONG
	ctypedef unsigned long DWORD
	ctypedef DWORD* LPDWORD
	ctypedef PVOID HANDLE
	ctypedef HANDLE HKEY
	ctypedef HKEY* PHKEY
	ctypedef DWORD REGSAM
	ctypedef const_char* LPCSTR
	ctypedef char* LPSTR
	ctypedef unsigned char BYTE
	ctypedef BYTE* LPBYTE

	cdef HKEY CURRENT_USER_HKEY
	cdef HKEY LOCAL_MACHINE_HKEY

	cdef DWORD GetLastError()
	cdef LONG RegOpenKeyA(HKEY, LPCSTR, PHKEY)
	cdef LONG RegOpenKeyExA(HKEY, LPCSTR, DWORD, REGSAM, PHKEY)
	cdef LONG RegQueryValueExA(HKEY, LPCSTR, LPDWORD, LPDWORD, LPBYTE, LPDWORD)
	cdef LONG RegCloseKey(HKEY)
	cdef LPSTR LocalStringAlloc(DWORD)
	cdef void LocalStringFree(LPSTR)

	ctypedef struct COORD:
		short X
		short Y

	ctypedef struct SMALL_RECT:
		short Left
		short Top
		short Right
		short Bottom

	ctypedef struct CONSOLE_CURSOR_INFO:
		unsigned long dwSize
		int bVisible

	ctypedef struct CHAR_INFO:

