#/usr/bin/env python

_platform_ = __import__('platform')
isx64 = _platform_.architecture()[0] == '64bit'
del _platform_

def is_x64(): return isx64

__all__ = ['is_x64', 'isx64']