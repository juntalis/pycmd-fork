"""
win32gui.py
Minimal fill-in for pywin32's win32gui module.
"""
from win32common import *
from win32con import FLASHW_ALL, FLASHW_CAPTION, FLASHW_STOP, FLASHW_TIMER, \
     FLASHW_TIMERNOFG, FLASHW_TRAY

#######################
# Structures & Unions #
#######################

class FLASHWINFO(SizedStructure32):
    _fields_ = [('hwnd', HWND),
                ('flags', DWORD),
                ('count', UINT),
                ('timeout', DWORD)]

PFLASHWINFO = POINTER(FLASHWINFO)

#########################
# C Function Prototypes #
#########################

_FlashWindowEx = BOOLFUNC('FlashWindowEx', [ PFLASHWINFO ], dll=user32)
GetForegroundWindow = HANDLEFUNC('GetForegroundWindow', [ ], dll=user32,
                                 errcheck=None)

#####################
# Function Wrappers #
#####################

def FlashWindow(hwnd, count=0, timeout=0, **kwargs):
    if not hwnd: return False

    # Resolve the flags.
    flags = 0
    if kwargs.pop('caption', False):
        flags |= FLASHW_CAPTION
    if kwargs.pop('taskbar', True):
        flags |= FLASHW_TRAY
    if kwargs.pop('foreground', False):
        flags |= FLASHW_TIMERNOFG
    if kwargs.pop('start', False):
        flags |= FLASHW_TIMER
    if kwargs.pop('stop', False):
        flags = FLASHW_STOP

    flashwin = FLASHWINFO(hwnd, flags, count, timeout)
    return _FlashWindowEx(byref(flashwin))

def FlashWindowEx(hwnd, flags, count, timeout):
    """ The FlashWindowEx function flashes the specified window a specified
        number of times. """
    if not hwnd: return False
    flashwin = FLASHWINFO(hwnd, flags, count, timeout)
    return _FlashWindowEx(byref(flashwin))

