#
# Basic mechanism for customizing PyCmd
#
import traceback

import os

from pycmd_public import appearance, behavior
from hooks import *


def apply_settings(settings_file, pycmd_dirs):
    """
    Execute a configuration file (if it exists), overriding values from the
    global configuration objects (created when this module is loaded)
    """
    (pycmd_install_dir, pycmd_data_dir) = pycmd_dirs
    if os.path.exists(settings_file):
        try:
            # We initialize the dictionary to readily contain the settings
            # structures; anything else needs to be explicitly imported
            execfile(settings_file, {'appearance': appearance,
                                     'behavior': behavior,
                                     'pycmd_install_dir': pycmd_install_dir,
                                     'pycmd_data_dir': pycmd_data_dir,
                                     'register_hook': register_hook,
                                     'unregister_hook': unregister_hook,
                                     'INIT_HOOK': hook_types[0],
                                     'MAIN_HOOK': hook_types[1],
                                     'TAB_HOOK': hook_types[2],
                                     'userconfig': __import__('userconfig'),
                                     'run_in_cmd': __import__('__main__').run_in_cmd
            })
        except Exception:
            print 'Error encountered when loading ' + settings_file
            print 'Subsequent settings will NOT be applied!'
            traceback.print_exc()


def sanitize():
    """Sanitize all the configuration instances"""
    appearance.sanitize()
    behavior.sanitize()

# Initialize global configuration instances with default values
#
# These objects are directly manipulated by the settings.py files, executed via
# apply_settings(). Then, they are directly used by PyCmd.py to get the current
# configuration settings

