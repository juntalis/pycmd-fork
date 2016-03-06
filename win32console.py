"""
win32console.py
Minimal fill-in for pywin32's win32console module. Many of the functions
(see: GetStdHandle) do not have a result that'd be compatible with code
written for PyWin32. Since there were only a handful of lines in console.py
that referenced members of win32console's wrapper types, I didn't think it was
worth the time it'd take to write a set of matching Python classes.
"""
from win32common import *
from win32tchar import _TFUNC

#############
# Constants #
#############

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

ENABLE_WINDOW_INPUT = 0x0008
ENABLE_MOUSE_INPUT = 0x0010
ENABLE_PROCESSED_INPUT = 0x0001

WHITE = 0x7
BLACK = 0x0

## Key Events
CTRL_C_EVENT = 0x0000
CTRL_BREAK_EVENT = 0x0001

## Mouse Events
MOUSE_MOVED = 0x0001

## Virtual Key Codes
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12

#######################
# Structures & Unions #
#######################

class CONSOLE_CURSOR_INFO(Structure):
    _fields_ = [ ('Size', c_int),
                 ('Visible', c_int) ]

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    """
    Ctypes implementation of the Win32 CONSOLE_SCREEN_BUFFER_INFO struct. In
    order to reduce the number of changes made to the original PyCmd source
    files, I reused the fieldnames from PyCmd's implementation. (despite how
    much having inconsistent naming styles drives me fucking crazy)
    """
    _fields_ = [ ('size', COORD),
                 ('cursorPosition', COORD),
                 ('attributes', WORD),
                 ('window', SMALL_RECT),
                 ('maxWindowSize', COORD) ]

PCONSOLE_CURSOR_INFO = POINTER(CONSOLE_CURSOR_INFO)
PCONSOLE_SCREEN_BUFFER_INFO = POINTER(CONSOLE_SCREEN_BUFFER_INFO)

class CHAR_UNION(Union):
    _fields_ = [ ('CharA', c_char),
                 ('CharW', c_wchar) ]

class KEY_EVENT_RECORD(Structure):
    """
    Note: I realize ctypes has the `_anonymous_` class variable, but since PyPy doesn't
    support _anonymous_ (or didn't last time I checked), we're using properties as shortcuts
    for accessing the CHAR_UNION fields.

    https://msdn.microsoft.com/en-us/library/windows/desktop/ms684166%28v=vs.85%29.aspx
    """
    _CharT = _TFUNC('Char')
    _fields_ = [ ('KeyDown', BOOL),
                 ('RepeatCount', WORD),
                 ('VirtualKeyCode', WORD),
                 ('VirtualScanCode', WORD),
                 ('CharU', CHAR_UNION),
                 ('ControlKeyState', DWORD) ]

    @property
    def CharA(self):
        return self.CharU.CharA

    @CharA.setter
    def CharA(self, value):
        self.uChar.CharU = value

    @property
    def CharW(self):
        return self.CharU.CharW

    @CharW.setter
    def CharW(self, value):
        self.CharU.CharW = value

    @property
    def Char(self):
        return getattr(self, KEY_EVENT_RECORD._CharT)

    @Char.setter
    def Char(self, value):
        setattr(self, KEY_EVENT_RECORD._CharT, value)

class MOUSE_EVENT_RECORD(Structure):
    _fields_ = [ ('MousePosition', COORD),
                 ('ButtonState', DWORD),
                 ('ControlKeyState', DWORD),
                 ('EventFlags', DWORD) ]

class WINDOW_BUFFER_SIZE_RECORD(Structure):
    _fields_ = [ ('Size', COORD) ]

class MENU_EVENT_RECORD(Structure):
    _fields_ = [ ('CommandId', DWORD) ]

class FOCUS_EVENT_RECORD(Structure):
    _fields_ = [ ('SetFocus', BOOL) ]

## Event Types
KEY_EVENT = 0x0001
MENU_EVENT = 0x0008
MOUSE_EVENT = 0x0002
FOCUS_EVENT = 0x0010
WINDOW_BUFFER_SIZE_EVENT = 0x0004

## Map event codes to the proper union member
_event_mapping = dict()
_event_mapping[ KEY_EVENT ] = 'KeyEvent'
_event_mapping[ MENU_EVENT ] = 'MenuEvent'
_event_mapping[ FOCUS_EVENT ] = 'FocusEvent'
_event_mapping[ MOUSE_EVENT ] = 'MouseEvent'
_event_mapping[ WINDOW_BUFFER_SIZE_EVENT ] = 'WindowBufferSizeEvent'

class EVENT_UNION(Union):
    _fields_ = [ (_event_mapping[KEY_EVENT], KEY_EVENT_RECORD),
                 (_event_mapping[MENU_EVENT], MENU_EVENT_RECORD),
                 (_event_mapping[FOCUS_EVENT], FOCUS_EVENT_RECORD),
                 (_event_mapping[MOUSE_EVENT], MOUSE_EVENT_RECORD),
                 (_event_mapping[WINDOW_BUFFER_SIZE_EVENT], WINDOW_BUFFER_SIZE_RECORD) ]

class INPUT_RECORD(Structure):
    _fields_ = [ ('EventType', WORD),
                 ('Event', EVENT_UNION) ]

    def __init__(self, *args, **kwargs):
        super(INPUT_RECORD, self).__init__(*args, **kwargs)
        self._record = None

    def _get_event_record(self):
        if self._record is None:
            fieldname = _event_mapping[ self.EventType ]
            self._record = getattr(self.Event, fieldname)
        return self._record

    def __getattr__(self, key):
        if key != 'Event' and key != 'EventType' and key != '_record':
            record = self._get_event_record()
            if hasattr(record, key):
                return getattr(record, key)
        return super(INPUT_RECORD, self).__getattribute__(key)

    def __setattr__(self, key, value):
        if key != 'Event' and key != 'EventType' and key != '_record':
            record = self._get_event_record()
            if hasattr(record, key):
                setattr(record, key, value)
                return
        return super(INPUT_RECORD, self).__setattr__(key, value)

# noinspection PyTypeChecker
PINPUT_RECORD = POINTER(INPUT_RECORD)

def PyINPUT_RECORDType(EventType):
    """
    Wrapper for a INPUT_RECORD struct. Create using PyINPUT_RECORDType(EventType)
    """
    return INPUT_RECORD(EventType)

GetStdHandle = kernel32.GetStdHandle
GetStdHandle.restype = HANDLE
GetStdHandle.argtypes = [ DWORD ]
GetStdHandle._flags_ |= FUNCFLAG_USE_LASTERROR
GetStdHandle.errcheck = errcheck_handle_result

GetConsoleWindow = kernel32.GetConsoleWindow
GetConsoleWindow.restype = HWND
GetConsoleWindow.argtypes = [ ]
GetConsoleWindow._flags_ |= FUNCFLAG_USE_LASTERROR
GetConsoleWindow.errcheck = errcheck_handle_result

GetConsoleScreenBufferInfo  = BOOLFUNC('GetConsoleScreenBufferInfo', [ HANDLE, PCONSOLE_SCREEN_BUFFER_INFO ])

SetConsoleCursorPosition    = BOOLFUNC('SetConsoleCursorPosition', [ HANDLE, COORD ])
SetConsoleCursorInfo        = BOOLFUNC('SetConsoleCursorInfo', [ HANDLE, PCONSOLE_CURSOR_INFO ])

SetConsoleWindowInfo        = BOOLFUNC('SetConsoleWindowInfo', [ HANDLE, BOOL, PSMALL_RECT ])

SetConsoleTextAttribute     = BOOLFUNC('SetConsoleTextAttribute', [ HANDLE, WORD ])
ReadConsoleOutputAttribute  = BOOLFUNC('ReadConsoleOutputAttribute', [ HANDLE, LPWORD, DWORD, COORD, LPDWORD ])
WriteConsoleOutputAttribute = BOOLFUNC('WriteConsoleOutputAttribute', [ HANDLE, LPWORD, DWORD, COORD, LPDWORD ])


SetConsoleTitle             = BOOLFUNC('SetConsoleTitle', [ LPTSTR ], use_tchar=True)
FlushConsoleInputBuffer     = BOOLFUNC('FlushConsoleInputBuffer', [ HANDLE ], use_last_error=False) # Suppress errcheck
ReadConsoleInput            = BOOLFUNC('ReadConsoleInput', [ HANDLE, PINPUT_RECORD, DWORD, LPDWORD ], use_tchar=True)
WriteConsoleInput           = BOOLFUNC('WriteConsoleInput', [ HANDLE, PINPUT_RECORD, DWORD, LPDWORD ], use_tchar=True)

def ReadOneConsoleInput(handle):
    # noinspection PyCallingNonCallable
    count = DWORD(1)
    record = INPUT_RECORD()
    if ReadConsoleInput(handle, byref(record), 1, byref(count)) and count.value == 1:
        return record
    else:
        raise WindowsError('Could not read one input event.')

def WriteOneConsoleInput(handle, record):
    # noinspection PyCallingNonCallable
    count = DWORD(1)
    return WriteConsoleInput(handle, byref(record), 1, byref(count)) and count.value == 1
