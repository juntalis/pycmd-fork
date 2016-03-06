"""
win32con.py
Minimal fill-in for pywin32's win32con module. Defines only the constants used by PyCmd.
"""

## Win32 Error Codes
ERROR_SUCCESS = 0

## Console Key Stuff
RIGHT_ALT_PRESSED = 0x0001  # the right alt key is pressed.
LEFT_ALT_PRESSED = 0x0002  # the left alt key is pressed.
RIGHT_CTRL_PRESSED = 0x0004  # the right ctrl key is pressed.
LEFT_CTRL_PRESSED = 0x0008  # the left ctrl key is pressed.
SHIFT_PRESSED = 0x0010  # the shift key is pressed.

## Clipboard Formats
CF_TEXT = 1
CF_OEMTEXT = 7
CF_UNICODETEXT = 13

## HGLOBAL Management
GHND = 0x0042
GPTR = 0x0040
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040
