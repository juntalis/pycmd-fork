"""
win32con.py
Minimal fill-in for pywin32's win32con module. Defines only the constants used by PyCmd.
"""

## Win32 Error Codes
ERROR_SUCCESS = 0

## File Access Flags
GENERIC_READ = 0x80000000L
GENERIC_WRITE = 0x40000000

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

## FlashWindowEx Flags
FLASHW_STOP      = 0x00000000
FLASHW_CAPTION   = 0x00000001
FLASHW_TRAY      = 0x00000002
FLASHW_ALL       = 0x00000003
FLASHW_TIMER     = 0x00000004
FLASHW_TIMERNOFG = 0x0000000C
