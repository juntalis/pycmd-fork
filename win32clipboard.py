"""
win32clipboard.py
Minimal fill-in for pywin32's win32clipboard module.
"""
from win32common import *
from win32con import CF_TEXT, CF_OEMTEXT, CF_UNICODETEXT, GHND, ERROR_SUCCESS

#########################
# C Function Prototypes #
#########################

_OpenClipboard = BOOLFUNC('OpenClipboard',  [ HWND ], dll=user32)
CloseClipboard = BOOLFUNC('CloseClipboard', [ ],      dll=user32)
EmptyClipboard = BOOLFUNC('EmptyClipboard', [ ],      dll=user32, doc="""
Empties the clipboard and frees handles to data in the clipboard. The function
then assigns ownership of the clipboard to the window that currently has the clipboard open.
""")

IsClipboardFormatAvailable = BOOLFUNC('IsClipboardFormatAvailable', [ UINT ], dll=user32, use_last_error=False)

_GetClipboardData = PTRFUNC('GetClipboardData', [ UINT ],         dll=user32)
_SetClipboardData = PTRFUNC('SetClipboardData', [ UINT, HANDLE ], dll=user32)

_GlobalAlloc = kernel32.GlobalAlloc
_GlobalAlloc.restype = HGLOBAL
_GlobalAlloc.argtypes = [ UINT, SIZE_T ]

_GlobalFree = kernel32.GlobalFree
_GlobalFree.restype = HGLOBAL
_GlobalFree.argtypes = [ HGLOBAL ]

_GlobalSize = kernel32.GlobalSize
_GlobalSize.restype = SIZE_T
_GlobalSize.argtypes = [ HGLOBAL ]

_GlobalLock = kernel32.GlobalLock
_GlobalLock.restype = LPVOID
_GlobalLock.argtypes = [ HGLOBAL ]

_GlobalUnlock = kernel32.GlobalUnlock
_GlobalUnlock.restype = BOOL
_GlobalUnlock.argtypes = [ HGLOBAL ]

#####################
# Function Wrappers #
#####################

def OpenClipboard(hWnd=None):
    """
    The OpenClipboard function opens the clipboard for examination and prevents other applications from modifying th
    clipboard content.

    :param hWnd: Window handle
    :type hWnd: HWND|int
    :return: If the function fails, the standard WinError is raised.
    :rtype: bool
    """
    if hWnd is None: hWnd = PNULL
    return bool(_OpenClipboard(hWnd))

def GetClipboardData(cformat=CF_TEXT):
    """
    The GetClipboardData function retrieves data from the clipboard in a specified format.
    Currently only implemented for CF_TEXT, CF_OEMTEXT, & CF_UNICODETEXT.

    :param cformat: Specified clipboard format. (Default=CF_TEXT)
    :type cformat: int
    :return: If the function fails, the standard WinError is raised.
    :rtype: str
    """
    result = None
    cstr_at = lambda ptr, size: NotImplemented
    if cformat == CF_TEXT or cformat == CF_OEMTEXT:
        cstr_at = lambda ptr, size: string_at(ptr, size - 1)
    elif cformat == CF_UNICODETEXT:
        cstr_at = lambda ptr, size: wstring_at(ptr, (size / sizeof(WCHAR)) - 1)
    else:
        raise NotImplementedError('GetClipboardData is only implemented for CF_TEXT at the moment.')

    chandle = _GetClipboardData(cformat)
    if not bool(chandle):
        raise WinError()

    try:
        cdataptr = _GlobalLock(chandle)
        if not bool(cdataptr):
            # Wasn't sure if the _GlobalUnlock call would be made before or after WinError
            # grabbed the last Win32 error code, so I decided to go this route and grab it before
            # the error is thrown.
            last_error = get_last_error()
            raise WinError(last_error)

        csize = _GlobalSize(cdataptr)
        if csize <= 0:
            last_error = get_last_error()
            if last_error == ERROR_SUCCESS:
                raise WinError(descr='Specified clipboard format is not available.')
            else:
                raise WinError(last_error)

        result = cstr_at(cdataptr, csize)
    finally:
        _GlobalUnlock(chandle)

    return result

def SetClipboardText(text, cformat=CF_TEXT):
    """
    Convenience function to call SetClipboardData with text.

    :param text: The text to place on the clipboard.
    :type text: str|unicode
    :param cformat: The clipboard format to use - must be CF_TEXT or CF_UNICODETEXT (Default=CF_TEXT)
    :type cformat: int
    """
    create_cobj = None
    if cformat == CF_TEXT or cformat == CF_OEMTEXT:
        create_cobj = create_string_buffer
    elif cformat == CF_UNICODETEXT:
        create_cobj = create_unicode_buffer

    # The string creation functions automatically add the extra termination character.
    ctextobj = create_cobj(text)

    # Allocate our buffer
    csize = sizeof(ctextobj)
    chandle = _GlobalAlloc(GHND, csize)
    if not bool(chandle):
        raise WinError()

    # Setup some state-tracking flags so that we can cleanup properly if any errors occur.
    #   0 => No cleanup required.
    #   1 => GlobalFree required.
    #   2 => GlobalUnlock & GlobalFree required.
    cleanup_stage = 1

    try:
        cdataptr = _GlobalLock(chandle)
        cleanup_stage = 2
        if not bool(cdataptr):
            last_error = get_last_error()
            raise WinError(last_error)

        # Copy the text buffer to our memory handle, then unlock it.
        memmove(cdataptr, ctextobj, csize)
        _GlobalUnlock(chandle)
        cleanup_stage = 1

        # And finally, transfer ownership of the memory to the clipboard.
        if not _SetClipboardData(cformat, chandle):
            last_error = get_last_error()
            raise WinError(last_error)

        cleanup_stage = 0
    finally:
        # Handle any necessary cleanups
        if cleanup_stage >= 2:
            # Needs GlobalUnlock
            _GlobalUnlock(chandle)

        if cleanup_stage >= 1:
            # Needs GlobalFree
            _GlobalFree(chandle)

    del ctextobj
