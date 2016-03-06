from ctypes import *
from ctypes.wintypes import *
from functools import wraps as _wraps
from _ctypes import FUNCFLAG_USE_LASTERROR

# Shadow ctypes stuff
from win32tchar import *

###########
# Globals #
###########

## Platform Info
isx64 = sizeof(c_void_p) == sizeof(c_ulonglong)

# Type Aliases
## Window Naming Conventions
SIZE_T = c_size_t
QWORD = c_ulonglong
LPWORD = PWORD = POINTER(WORD)
LPDWORD = PDWORD = POINTER(DWORD)
PSMALL_RECT = POINTER(SMALL_RECT)
LPHANDLE = PHANDLE = POINTER(HANDLE)
LPOVERLAPPED = LPSECURITY_ATTRIBUTES = c_void_p
ULONG_PTR = QWORD if isx64 else DWORD

## DLLs
user32 = WinDLL('user32')
kernel32 = WinDLL('kernel32')

# Constants
NULL = 0
TRUE = 1
FALSE = 0
PNULL = c_void_p(NULL)
INVALID_HANDLE_VALUE = ULONG_PTR(-1).value

#######################
# Structures & Unions #
#######################

## Try to import _COORD from ctypes.wintypes or declare our own.
try:
    from ctypes.wintypes import _COORD as COORD
except ImportError:
    class COORD(Structure):
        _fields_ = [ ('X', c_short),
                     ('Y', c_short) ]

class SizedStructure32(Structure):
    """ Base class for all structures who's first field is a 32-bit integer
     expecting the structure's size. """
    _fields_ = [('cbSize', UINT),]

    def __init__(self, *args, **kwargs):
        args = list(args)
        args.insert(0, sizeof(self))
        super(SizedStructure32, self).__init__(*args, **kwargs)

####################
# Shared Utilities #
####################

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

################################
# Common Handlers for errcheck #
################################

_uses_last_error = lambda func: (func._flags_ & FUNCFLAG_USE_LASTERROR) == FUNCFLAG_USE_LASTERROR

def _errcheck_failure(result, func, args):
    if _uses_last_error(func):
        return ctypes.WinError(ctypes.get_last_error())
    else:
        return ctypes.WinError(
            descr='Failed call made to {0} (Result: {1}) with args: {2}'.format(func.__name__, result, repr(args))
        )

def errcheck_nonzero_failure(result, func, args):
    if bool(result):
        raise _errcheck_failure(result, func, args)
    return result

def errcheck_nonzero_success(result, func, args):
    if not bool(result):
        raise _errcheck_failure(result, func, args)
    return result

def errcheck_handle_result(result, func, args):
    if not bool(result) or result == INVALID_HANDLE_VALUE:
        raise _errcheck_failure(result, func, args)
    return result

def errcheck_bool_result(result, func, args):
    """ Use errcheck functionality to force a Python bool result """
    return bool(result)

def errcheck_bool_result_checked(result, func, args):
    """ Same as errcheck_bool_result, but will only return for True values. False values will be handled as a function
     failure and handled in errcheck_nonzero_success. """
    return bool(errcheck_nonzero_success(result, func, args))

###########################
# Ctypes Utility Wrappers #
###########################

def _build_function_decl(name, argtypes, kwargs, restype=None, errcheck=None, noerrcheck=None):
    """ Shared utility for building function declarations based on common patterns. """
    doc = kwargs.pop('doc', None)
    procpair = (name, kwargs.pop('dll', kernel32))
    kwargs.setdefault('use_last_error', True)
    funcptr = WINFUNCTYPE(restype, *argtypes, **kwargs)(procpair)
    if doc is not None:
        funcptr.__doc__ = doc

    if kwargs['use_last_error']:
        if errcheck is not None:
            funcptr.errcheck = errcheck
    else:
        if noerrcheck is not None:
            funcptr.errcheck = noerrcheck

    return funcptr

def BOOLFUNC(name, argtypes, **kwargs):
    """ Template for BOOL returning functions that set last error and return false on failure """
    return _build_function_decl(name, argtypes, kwargs, BOOL, errcheck_bool_result_checked, errcheck_bool_result)

def HANDLEFUNC(name, argtypes, **kwargs):
    """ Template for HANDLE returning function. Checks returns for INVALID_HANDLE_VALUE and NULL, and
        uses the value of GetLastError for determining error codes. """
    return _build_function_decl(name, argtypes, kwargs, HANDLE, errcheck_handle_result)

def PTRFUNC(name, argtypes, **kwargs):
    """ Template for pointer returning functions that set last error and return NULL on failure """
    return _build_function_decl(name, argtypes, kwargs, LPVOID, errcheck_nonzero_success)

#########################
# C Function Prototypes #
#########################
# SetFileAttributesW = kernel32.SetFileAttributesW
# SetFileAttributesW.restype = BOOL
# SetFileAttributesW.argtypes = [ LPCWSTR, DWORD ]
#
# GetFileAttributesW = kernel32.GetFileAttributesW
# GetFileAttributesW.restype = DWORD
# GetFileAttributesW.argtypes = [ LPCWSTR ]

_ExpandEnvironmentStrings = kernel32.ExpandEnvironmentStringsT
_ExpandEnvironmentStrings.restype = DWORD
_ExpandEnvironmentStrings.argtypes = [ LPCTSTR, LPTSTR, DWORD ]
_ExpandEnvironmentStrings._flags_ |= FUNCFLAG_USE_LASTERROR

#####################
# Function Wrappers #
#####################

def ExpandEnvironmentStrings(text):
    """ Opens the clipboard for reading/writing

    :param text: A
    :type text: basestring
    :return: The text with all inline environment variables expanded.
    :rtype: tchar.tstr
    """
    if text is None or not isinstance(text, basestring):
        return text

    text = _T(text)
    if len(text) == 0 or _T('%') not in text:
        return text

    # Call the expansion function with a 0-sized buffer to determine the necessary
    # buffer size
    bufsize = _ExpandEnvironmentStrings(text, cast(PNULL, LPTSTR), 0L)
    if not bufsize: return text
    bufsize += 1
    cbuffer = create_tstring_buffer(bufsize)
    expcount = _ExpandEnvironmentStrings(text, cbuffer, bufsize)
    assert (expcount > 0)
    return cbuffer.value
