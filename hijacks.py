# encoding: utf-8
"""
hijacks.py
TODO: Description

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
"""
import sys
import codeutil

PyCmd = None

def handle_motd(color, appearance, behavior):
    if hasattr(appearance, 'motd') and not behavior.quiet_mode:
        behavior.quiet_mode = True
        sys.stdout.write(appearance.motd)
        sys.stdout.write('\r' + color.Fore.DEFAULT + color.Back.DEFAULT)

def apply_hijacks(module):
    global PyCmd
    PyCmd = module
    codeutil.add_hijack('motd', handle_motd)
