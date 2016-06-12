import os as _os, ctypes
from ctypes import *
from ctypes.wintypes import *
from functools import wraps as _wraps
from _ctypes import FUNCFLAG_USE_LASTERROR

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

###############
# TCHAR Stuff #
###############

# TODO: This is just a placeholder. Having trouble finding any concrete info on unicode filepath support across Windows versions.
TCHAR_UNICODE = _os.path.supports_unicode_filenames

# Set the appropriate handlers
if TCHAR_UNICODE:
    _T = unicode
    TCHAR_SUFFIX = 'W'
    tstring_at = wstring_at
    TCHAR = c_tchar = c_wchar
    LPCTSTR = LPTSTR = c_tchar_p = c_wchar_p
    create_tstring_buffer = create_unicode_buffer
else:
    _T = str
    TCHAR_SUFFIX = 'A'
    tstring_at = string_at
    TCHAR = c_tchar = c_char
    LPCTSTR = LPTSTR = c_tchar_p = c_char_p
    create_tstring_buffer = create_string_buffer

_TFUNC = lambda name: name + TCHAR_SUFFIX
_TPAIR = lambda name, dll: (_TFUNC(name), dll,)

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

_uses_last_error = lambda func: bool(func._flags_ & FUNCFLAG_USE_LASTERROR)

def _errcheck_failure(result, func, args):
    if _uses_last_error(func):
        return WinError(get_last_error())
    else:
        return WinError(
            descr='Failed call made to {0} (Result: {1}) with args: {2}'.format(
                func.__name__, result, repr(args)
            )
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

def WINFUNCDECL(name, argtypes, restype=None, **kwargs):
    """ Utility function to create fully-typed ctypes function prototypes
        in one call. """
    # Need to remove our custom keyword arguments before calling the prototype
    # factory.
    funcdoc = kwargs.pop('doc', None)
    errcheck = kwargs.pop('errcheck', None)
    paramflags = kwargs.pop('paramflags', None)
    func_spec = (name, kwargs.pop('dll', kernel32))
    FUNCTYPE = kwargs.pop('proto', WINFUNCTYPE)
    use_last_error = kwargs.setdefault('use_last_error', True)

    # Handle TCHAR naming if necessary
    if kwargs.pop('use_tchar', False):
        func_spec = _TPAIR(*func_spec)

    # Construct our prototype and apply it to the (name_or_ordinal, dll) pair
    funcptr = FUNCTYPE(restype, *argtypes, **kwargs)(func_spec, paramflags)

    # Apply any specified properties.
    if funcdoc is not None:
        funcptr.__doc__ = funcdoc
    if errcheck is not None:
        funcptr.errcheck = errcheck

    return funcptr

def BOOLFUNC(name, argtypes, checked=True, **kwargs):
    """ Template for BOOL returning functions that set last error and return
        false on failure. """
    kwargs.setdefault('errcheck', errcheck_bool_result_checked if checked \
                                  else errcheck_bool_result)
    return WINFUNCDECL(name, argtypes, restype=BOOL, **kwargs)

def HANDLEFUNC(name, argtypes, **kwargs):
    """ Template for HANDLE returning function. Checks returns for
        INVALID_HANDLE_VALUE and NULL, and uses the value of GetLastError for
        determining error codes. """
    kwargs.setdefault('errcheck', errcheck_handle_result)
    return WINFUNCDECL(name, argtypes, restype=HANDLE, **kwargs)

def PTRFUNC(name, argtypes, **kwargs):
    """ Template for pointer returning functions that set last error and return
        NULL on failure """
    kwargs.setdefault('errcheck', errcheck_nonzero_success)
    return WINFUNCDECL(name, argtypes, restype=LPVOID, **kwargs)

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

_ExpandEnvironmentStrings = WINFUNCDECL(
    'ExpandEnvironmentStrings', [ LPCTSTR, LPTSTR, DWORD ],
    restype=DWORD, use_tchar=True, use_last_error=True
)

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
