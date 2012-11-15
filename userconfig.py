from PyCmdDB import get_db_backend

__all__ = ['init_user', 'install_dir', 'data_dir', 'pycmddb', 'get_custom_command', 'get_custom_commands']

_pycmddb = None
_install_dir = None
_data_dir = None
_initialized = False

def init_user(datadir, installdir):
    global _initialized, _install_dir, _data_dir, _pycmddb
    if not _initialized:
        _initialized = True
        _install_dir = installdir
        _data_dir = datadir
        _pycmddb = get_db_backend(_data_dir, 'pycmd', 'leveldb')


def pycmddb(): return _pycmddb


def install_dir(): return _install_dir


def data_dir(): return _data_dir

#noinspection PyUnresolvedReferences
def get_custom_commands():
    try:
        import custom_commands
    except ImportError:
        return None
    reload(custom_commands)
    cmds = {}
    for cmd in dir(custom_commands):
        if str(cmd).startswith('cmd_'):
            cmds[cmd[4:].lower()] = getattr(custom_commands, cmd)
    return cmds


def get_custom_command(cmdname):
    try:
        import custom_commands as cmds

        reload(cmds)
    except ImportError:
        cmds = object
    try: return getattr(cmds, 'cmd_' + str(cmdname))
    except: return None