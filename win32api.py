# Thinking about porting this over to cython.
from ctypes import *
from ctypes.wintypes import *
import os as _os

kernel32 = WinDLL('kernel32')
user32 = WinDLL('user32')

#############
# Constants #
#############
# From wincon.h
RIGHT_ALT_PRESSED = 1 # the right alt key is pressed.
LEFT_ALT_PRESSED = 2 # the left alt key is pressed.
RIGHT_CTRL_PRESSED = 4 # the right ctrl key is pressed.
LEFT_CTRL_PRESSED = 8 # the left ctrl key is pressed.
SHIFT_PRESSED = 16 # the shift key is pressed.

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
ENABLE_WINDOW_INPUT = 0x0008
ENABLE_MOUSE_INPUT = 0x0010
ENABLE_PROCESSED_INPUT = 0x0001
WHITE = 0x7
BLACK = 0

CTRL_C_EVENT = 0x0000
KEY_EVENT = 0x0001
CTRL_BREAK_EVENT = 0x0001
MOUSE_MOVED = 0x0001
MOUSE_EVENT = 0x0002
WINDOW_BUFFER_SIZE_EVENT = 0x0004
MENU_EVENT = 0x0008
FOCUS_EVENT = 0x0010

CW_USEDEFAULT = -2147483648
FLASHW_STOP = 0
FLASHW_CAPTION = 1
FLASHW_TRAY = 2
FLASHW_ALL = (FLASHW_CAPTION | FLASHW_TRAY)
FLASHW_TIMER = 4
FLASHW_TIMERNOFG = 12

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12

GENERIC_READ = 0x80000000L
GENERIC_WRITE = 0x40000000

GHND = 0x0042
GMEM_FIXED = 0x0000
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040
GPTR = 0x0040

CF_TEXT = 1
NULL = 0
TRUE = 1
FALSE = 0
PNULL = c_void_p(NULL)

#######################
# Structures & Unions #
#######################

class COORD(Structure):
	_fields_ = [('X', c_short),
				('Y', c_short)]


class SMALL_RECT(Structure):
	_fields_ = [('Left', c_short),
				('Top', c_short),
				('Right', c_short),
				('Bottom', c_short)]


class CONSOLE_CURSOR_INFO(Structure):
	_fields_ = [('size', c_int),
				('visible', c_int)]


class CONSOLE_SCREEN_BUFFER_INFO(Structure):
	_fields_ = [('size', COORD),
				('cursorPosition', COORD),
				('attributes', WORD),
				('window', SMALL_RECT),
				('maxWindowSize', COORD)]


class CHAR_UNION(Union):
	_fields_ = [("uChar", c_wchar),
				("Char", c_char)]


class CHAR_INFO(Structure):
	_anonymous_ = ("cu",)
	_fields_ = [('cu', CHAR_UNION),
				('Attributes', c_short)]


class KEY_EVENT_RECORD(Structure):
	_anonymous_ = ('CU',)
	_fields_ = [('KeyDown', BOOL),
				('RepeatCount', WORD),
				('VirtualKeyCode', WORD),
				('VirtualScanCode', WORD),
				('CU', CHAR_UNION),
				('ControlKeyState', DWORD)]


class MOUSE_EVENT_RECORD(Structure):
	_fields_ = [("dwMousePosition", COORD),
				("dwButtonState", c_int),
				("dwControlKeyState", c_int),
				("dwEventFlags", c_int)]


class WINDOW_BUFFER_SIZE_RECORD(Structure):
	_fields_ = [("dwSize", COORD)]


class MENU_EVENT_RECORD(Structure):
	_fields_ = [("dwCommandId", c_uint)]


class FOCUS_EVENT_RECORD(Structure):
	_fields_ = [("bSetFocus", c_byte)]


class INPUT_UNION(Union):
	_fields_ = [("KeyEvent", KEY_EVENT_RECORD),
				("MouseEvent", MOUSE_EVENT_RECORD),
				("WindowBufferSizeEvent", WINDOW_BUFFER_SIZE_RECORD),
				("MenuEvent", MENU_EVENT_RECORD),
				("FocusEvent", FOCUS_EVENT_RECORD)]


class INPUT_RECORD(Structure):
	_anonymous_ = ("EU",)
	_fields_ = [("EventType", c_short),
				("EU", INPUT_UNION)]


class CONSOLE_CURSOR_INFO(Structure):
	_fields_ = [("dwSize", c_int),
				("bVisible", c_byte)]


class FLASHWINFO(Structure):
	_fields_ = [("cbSize", UINT),
				("hwnd", HWND),
				("dwFlags", DWORD),
				("uCount", UINT),
				("dwTimeout", DWORD)]

CHAR = c_char
UCHAR = c_ubyte

LPOVERLAPPED = c_void_p
LPSECURITY_ATTRIBUTES = c_void_p

PHANDLE = POINTER(HANDLE)
LPHANDLE = PHANDLE

PWORD = POINTER(WORD)
LPWORD = PWORD
PDWORD = POINTER(DWORD)
LPDWORD = PDWORD
PINPUT_RECORD = POINTER(INPUT_RECORD)
PFLASHWINFO = POINTER(FLASHWINFO)
PCONSOLE_SCREEN_BUFFER_INFO = POINTER(CONSOLE_SCREEN_BUFFER_INFO)

#noinspection PyTypeChecker
ONE_INPUT_RECORD = (1 * INPUT_RECORD)
HGLOBAL = HANDLE

#################
# Utility Stuff #
#################

class _BitwiseResult(object):
	def __init__(self, **kw):
		for k in kw.keys():
			setattr(self, k, kw[k])
		self.__kw__ = kw

	def __unicode__(self): return unicode(self.__str__())

	def __repr__(self): return self.__str__()

	def __str__(self):
		keys = self.__kw__
		fmtval = lambda k: '%s: %s' % (k, 'True' if keys[k] else 'False')
		return '\n'.join([fmtval(k) for k in keys.keys()])


def _test_bitwise_and(target, **flags):
	hasflags = {}
	for k in flags.keys():
		v = flags[k]
		if (target & v) != 0:
			hasflags[k] = True
		else:
			hasflags[k] = False
	return _BitwiseResult(**hasflags)


def _test_bitwise_or(target, **flags):
	hasflags = {}
	for k in flags.keys():
		v = flags[k]
		if (target | v) != 0:
			hasflags[k] = True
		else:
			hasflags[k] = False
	return _BitwiseResult(**hasflags)


class Enum(object):
	__doc__ = """ Create an enum of values. """
	__vals__ = {}

	def __init__(self, **kwargs):
		self.__vals__ = kwargs

	def keys(self): return self.__vals__.keys()

	def has_key(self, key): return self.__vals__.has_key(key)

	def test_and(self, target): return _test_bitwise_and(target, **self.__vals__)

	def test_or(self, target): return _test_bitwise_or(target, **self.__vals__)

	def __getitem__(self, item):
		titem = type(item)
		if titem in [long, int]:
			keys = self.__vals__.keys()
			item = int(item)
			if item < 0 or item > len(keys): raise KeyError()
			key = keys[item]
		else:
			key = item
		return self.__vals__[key]

	def __getattr__(self, item):
		if item in ['keys', 'has_key'] or not self.has_key(item):
			return super(Enum, self).__getattribute__(item)
		else:
			return self.__getitem__(item)

	def __unicode__(self): return unicode(self.__str__())

	def __repr__(self): return self.__str__()

	def __str__(self):
		def val2str(v):
			tv = type(v)
			if tv == long: return '0x%xL' % v
			elif tv == float: return '%f' % v
			elif tv == int: return '0x%x' % v
			else: return str(v)

		fmtval = lambda k: k + ' = ' + val2str(getattr(self, k))
		keys = self.keys()
		keys.sort()
		return '\n'.join([fmtval(k) for k in keys])

enum = Enum

#############
# Functions #
#############
SetFileAttributesW = kernel32.SetFileAttributesW
SetFileAttributesW.restype = BOOL
SetFileAttributesW.argtypes = [LPCWSTR, DWORD]

GetFileAttributesW = kernel32.GetFileAttributesW
GetFileAttributesW.restype = DWORD
GetFileAttributesW.argtypes = [LPCWSTR]

def _build_fileattrs():
	class FileAttributes(Enum):
		__doc__ = """ Values used for calls to SetFileAttributes and results from GetFileAttributes """

	return FileAttributes(
		archive = 0x0020,
		hidden = 0x0002,
		normal = 0x0080,
		noindex_content = 0x2000,
		offline = 0x1000,
		readonly = 0x0001,
		system = 0x0004,
		temp = 0x0100,
		temporary = 0x0100,
		compressed = 0x0800,
		device = 0x0040,
		directory = 0x0010,
		encrypted = 0x4000,
		reparse_point = 0x0400,
		sparse_file = 0x0200,
		virtual = 0x10000,
		noscrub_data = 0x20000,
		integrity_stream = 0x8000
	)

fileattrs = _build_fileattrs()
del _build_fileattrs

def _abspath(fpath):
	return '\\\\?\\%s' % _os.path.abspath(fpath) if _os.path.exists(fpath) else fpath


def SetFileAttributes(fpath, *attrs):
	""" Sets the attributes for a file or directory.
	:rtype : bool
	"""
	if len(attrs) == 0: return
	attrval = attrs[0]
	if len(attrs) > 1:
		for attr in attrs[1:]:
			attrval = attrval | attr
	fpath = _abspath(fpath)
	return bool(SetFileAttributesW(fpath, attrval))


def GetFileAttributes(fpath):
	""" Retrieves file system attributes for a specified file or directory.
	:rtype : _BitwiseResult
	"""
	fpath = _abspath(fpath)
	flags = GetFileAttributesW(fpath)
	if flags == -1: raise WindowsError(FormatError())
	return fileattrs.test_and(flags)

ExpandEnvironmentStringsW = kernel32.ExpandEnvironmentStringsW
ExpandEnvironmentStringsW.restype = DWORD
ExpandEnvironmentStringsW.argtypes = [LPCWSTR, LPWSTR, DWORD]

def ExpandEnvironmentStrings(sinput):
	if len(sinput) == 0 or '%' not in str(sinput): return sinput
	sz = ExpandEnvironmentStringsW(sinput, cast(PNULL, LPWSTR), 0L)
	if sz == 0L: return sinput
	sz += 1
	buf = create_unicode_buffer(sz)
	sznew = ExpandEnvironmentStringsW(sinput, buf, sz)
	assert(sznew > 0)
	return buf.value

GetStdHandle = kernel32.GetStdHandle
GetStdHandle.restype = HANDLE
GetStdHandle.argtypes = [DWORD]
GetStdHandle.__doc__ = """
Retrieves a handle to the specified standard device (standard input, standard output, or standard error).
	HANDLE WINAPI GetStdHandle(_In_  DWORD nStdHandle);
	nStdHandle[in] - The standard device.
"""

GetConsoleScreenBufferInfo = kernel32.GetConsoleScreenBufferInfo
GetConsoleScreenBufferInfo.restype = BOOL
GetConsoleScreenBufferInfo.argtypes = [HANDLE, PCONSOLE_SCREEN_BUFFER_INFO]

SetConsoleCursorPosition = kernel32.SetConsoleCursorPosition
SetConsoleCursorPosition.restype = BOOL
SetConsoleCursorPosition.argtypes = [HANDLE, COORD]

SetConsoleCursorInfo = kernel32.SetConsoleCursorInfo
SetConsoleCursorInfo.restype = BOOL
SetConsoleCursorInfo.argtypes = [HANDLE, POINTER(CONSOLE_CURSOR_INFO)]

SetConsoleTextAttribute = kernel32.SetConsoleTextAttribute
SetConsoleTextAttribute.restype = BOOL
SetConsoleTextAttribute.argtypes = [HANDLE, WORD]

SetConsoleTitleA = kernel32.SetConsoleTitleA
SetConsoleTitleW = kernel32.SetConsoleTitleW
SetConsoleTitleA.restype = SetConsoleTitleW.restype = BOOL
SetConsoleTitleA.argtypes = [LPCSTR]
SetConsoleTitleW.argtypes = [LPCWSTR]

SetConsoleWindowInfo = kernel32.SetConsoleWindowInfo
SetConsoleWindowInfo.restype = BOOL
SetConsoleWindowInfo.argtypes = [HANDLE, BOOL, POINTER(SMALL_RECT)]
SetConsoleWindowInfo.__doc__ = """
Sets the current size and position of a console screen buffer's window.

	BOOL WINAPI SetConsoleWindowInfo(
	  _In_  HANDLE hConsoleOutput,
	  _In_  BOOL bAbsolute,
	  _In_  const SMALL_RECT *lpConsoleWindow
	);

hConsoleOutput [in]
	A handle to the console screen buffer. The handle must have the GENERIC_READ access right. For more information, see Console Buffer Security and Access Rights.
bAbsolute [in]
	If this parameter is TRUE, the coordinates specify the new upper-left and lower-right corners of the window. If it is FALSE, the coordinates are relative to the current window-corner coordinates.
lpConsoleWindow [in]
	A pointer to a SMALL_RECT structure that specifies the new upper-left and lower-right corners of the window.
"""

ReadConsoleInput = kernel32.ReadConsoleInputW
ReadConsoleInput.restype = BOOL
ReadConsoleInput.argtypes = [HANDLE, PINPUT_RECORD, DWORD, LPDWORD]
ReadConsoleInput.__doc__ = """
Reads data from a console input buffer and removes it from the buffer.

	BOOL WINAPI ReadConsoleInput(
		HANDLE hConsoleInput,
		PINPUT_RECORD lpBuffer,
		DWORD nLength,
		LPDWORD lpNumberOfEventsRead
	);

hConsoleInput [in]
	A handle to the console input buffer. The handle must have the GENERIC_READ access right. For more information, see Console Buffer Security and Access Rights.
lpBuffer [out]
	A pointer to an array of INPUT_RECORD structures that receives the input buffer data.
	The storage for this buffer is allocated from a shared heap for the process that is 64 KB in size. The maximum size of the buffer will depend on heap usage.
nLength [in]
	The size of the array pointed to by the lpBuffer parameter, in array elements.
lpNumberOfEventsRead [out]
	A pointer to a variable that receives the number of input records read.
"""

WriteConsoleInput = kernel32.WriteConsoleInputW
WriteConsoleInput.restype = BOOL
WriteConsoleInput.argtypes = [HANDLE, PINPUT_RECORD, DWORD, LPDWORD]
WriteConsoleInput.__doc__ = """
Writes data directly to the console input buffer.

	BOOL WINAPI WriteConsoleInput(
		_In_   HANDLE hConsoleInput,
		_In_   const INPUT_RECORD *lpBuffer,
		_In_   DWORD nLength,
		_Out_  LPDWORD lpNumberOfEventsWritten
	);

hConsoleInput [in]
	A handle to the console input buffer. The handle must have the GENERIC_WRITE access right. For more information, see Console Buffer Security and Access Rights.
lpBuffer [in]
	A pointer to an array of INPUT_RECORD structures that contain data to be written to the input buffer.
	The storage for this buffer is allocated from a shared heap for the process that is 64 KB in size. The maximum size of the buffer will depend on heap usage.
nLength [in]
	The number of input records to be written.
lpNumberOfEventsWritten [out]
	A pointer to a variable that receives the number of input records actually written.
Return value
	If the function succeeds, the return value is nonzero.
	If the function fails, the return value is zero. To get extended error information, call GetLastError.
"""

GetConsoleWindow = kernel32.GetConsoleWindow
GetForegroundWindow = user32.GetForegroundWindow
GetForegroundWindow.restype = GetConsoleWindow.restype = HWND
GetForegroundWindow.argtypes = GetConsoleWindow.argtypes = []
GetConsoleWindow.__doc__ = """ Retrieves the window handle used by the console associated with the calling process. """
GetForegroundWindow.__doc__ =\
""" Retrieves a handle to the foreground window (the window with which the user is currently working). The system
assigns a slightly higher priority to the thread that creates the foreground window than it does to other threads. """

FlashWindowEx = user32.FlashWindowEx
FlashWindowEx.restype = BOOL
FlashWindowEx.argtypes = [PFLASHWINFO]
FlashWindowEx.__doc__ =\
""" Flashes the specified window. It does not change the active state of the window. """

def FlashWindow(hwnd, dwflags, count, timeout):
	""" Wrapper around FlashWindowEx to make the API compatible with the real pywin32 calls. """
	flashwin = FLASHWINFO()
	flashwin.hwnd = hwnd
	flashwin.dwFlags = dwflags
	flashwin.uCount = count
	flashwin.dwTimeout = timeout
	flashwin.cbSize = sizeof(flashwin)
	return FlashWindowEx(byref(flashwin))

_OpenClipboard = user32.OpenClipboard
_OpenClipboard.restype = BOOL
_OpenClipboard.argtypes = [HWND]
_OpenClipboard.__doc__ = """ Opens the clipboard for reading/writing """

def OpenClipboard(hwnd = NULL):
	return _OpenClipboard(hwnd) != FALSE

EmptyClipboard = user32.EmptyClipboard
EmptyClipboard.restype = BOOL
EmptyClipboard.argtypes = []
EmptyClipboard.__doc__ = """ Empties the clipboard and frees handles to data in the clipboard. The function
then assigns ownership of the clipboard to the window that currently has the clipboard open."""

IsClipboardFormatAvailable = user32.IsClipboardFormatAvailable
IsClipboardFormatAvailable.restype = BOOL
IsClipboardFormatAvailable.argtypes = [UINT]
IsClipboardFormatAvailable.__doc__ = """ Determines whether the clipboard contains data in the specified format.  """

GetClipboardData = user32.GetClipboardData
GetClipboardData.restype = HANDLE
GetClipboardData.argtypes = [UINT]
GetClipboardData.__doc__ = """ Retrieves data from the clipboard in a specified format. The clipboard must
have been opened previously. """

SetClipboardData = user32.SetClipboardData
SetClipboardData.restype = HANDLE
SetClipboardData.argtypes = [UINT, HANDLE]
SetClipboardData.__doc__ = """ Places data on the clipboard in a specified clipboard format. The window must be
the current clipboard owner, and the application must have called the OpenClipboard function. (When responding to
the WM_RENDERFORMAT and WM_RENDERALLFORMATS messages, the clipboard owner must not call OpenClipboard before
calling SetClipboardData.) """

CloseClipboard = user32.CloseClipboard
CloseClipboard.restype = BOOL
CloseClipboard.argtypes = []
CloseClipboard.__doc__ = """ Closes the clipboard. """

GlobalAlloc = kernel32.GlobalAlloc
GlobalAlloc.restype = HGLOBAL
GlobalAlloc.argtypes = [UINT, c_size_t]
GlobalAlloc.__doc__ = """ Allocates the specified number of bytes from the heap. """

GlobalFree = kernel32.GlobalFree
GlobalFree.restype = HGLOBAL
GlobalFree.argtypes = [HGLOBAL]
GlobalFree.__doc__ = """ Frees the specified global memory object and invalidates its handle. """

GlobalLock = kernel32.GlobalLock
GlobalLock.restype = LPVOID
GlobalLock.argtypes = [HGLOBAL]
GlobalLock.__doc__ =\
""" Locks a global memory object and returns a pointer to the first byte of the object's memory block. """

GlobalUnlock = kernel32.GlobalUnlock
GlobalUnlock.restype = BOOL
GlobalUnlock.argtypes = [HGLOBAL]
GlobalUnlock.__doc__ =\
""" Decrements the lock count associated with a memory object that was allocated with GMEM_MOVEABLE. This function
has no effect on memory objects allocated with GMEM_FIXED. """


#####################
# Function Wrappers #
#####################

def ReadOneConsoleInput(handle):
	buf = ONE_INPUT_RECORD()
	dw = DWORD(0)
	if ReadConsoleInput(handle, cast(buf, PINPUT_RECORD), 1, byref(dw)) and dw.value == 1:
		return buf[0]
	else:
		raise WindowsError('Could not read one input event.')

def WriteOneConsoleInput(handle, record):
	dw = DWORD(0)
	assert(WriteConsoleInput(handle, cast(record, PINPUT_RECORD), 1, byref(dw)) == 1)

class Clipboard(object):

	def __init__(self, hwnd = NULL):
		self._hwnd_ = hwnd

	#noinspection PyUnusedLocal
	def __enter__(self):
		if not OpenClipboard(self._hwnd_):
			raise WindowsError('Could not open the windows clipboard.')
		return self

	#noinspection PyUnusedLocal
	def __exit__(self, typ, value, traceback):
		if not CloseClipboard():
			raise WindowsError('Could not close the windows clipboard.')

	@property
	def text(self): return self.__get_text__()

	@text.setter
	def text(self, value): self.__set_text__(value)

	def __get_text__(self):
		if not IsClipboardFormatAvailable(CF_TEXT):
			return False
		result = cast(GetClipboardData(CF_TEXT), c_void_p)
		if not bool(result):
			raise WindowsError(FormatError())
		resultptr = GlobalLock(result)
		if not bool(resultptr):
			raise WindowsError(FormatError())
		resultstr = cast(resultptr, c_char_p).value
		GlobalUnlock(result)
		return resultstr

	def __set_text__(self, text):
		textbuf = create_unicode_buffer(text, len(text) + 1)
		bufsize = sizeof(textbuf)
		hMem = GlobalAlloc(GHND, bufsize)
		if not bool(hMem):
			raise WindowsError('Could not allocate our buffer.')
		hMemPtr = GlobalLock(hMem)
		if not bool(hMemPtr):
			raise WindowsError('Could not lock our buffer.')
		memmove(hMemPtr, textbuf, bufsize)
		GlobalUnlock(hMemPtr)
		if not EmptyClipboard() or not SetClipboardData(CF_TEXT, hMemPtr):
			raise WindowsError('Could not set the clipboard text.')

	def __str__(self): return self.text

	def __unicode__(self): return unicode(self.text)
