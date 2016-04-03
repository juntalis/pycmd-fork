import sys, os, time, traceback
from console import read_input

def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""
    return hasattr(sys, 'frozen')

def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

def bootstrap():
    """ Bootstraps the PyCmd.py script """
    # Resolve script dir & setup python path.
    scriptdir = module_path()
    sys.path.insert(0, scriptdir)

    # Import the PyCmd script and alter its
    # internal dict to fool it into thinking
    # it was run as the main script.
    import PyCmd
    PyCmd.__dict__['__name__'] = '__main__'
    PyCmd.__dict__['__file__'] = os.path.join(scriptdir, 'PyCmd.py')
    return PyCmd

if __name__=='__main__':
    PyCmd = bootstrap()
    try:
        PyCmd.init()
        PyCmd.main()
    except Exception, e:
        report_file_name = (PyCmd.pycmd_data_dir
                            + '\\crash-'
                            + time.strftime('%Y%m%d_%H%M%S')
                            + '.log')
        print '\n'
        print '************************************'
        print 'PyCmd has encountered a fatal error!'
        print
        report_file = open(report_file_name, 'w')
        traceback.print_exc(file=report_file)
        report_file.close()
        traceback.print_exc()
        print
        print 'Crash report written to:\n  ' + report_file_name
        print
        print 'Press any key to exit... '
        print '************************************'
        read_input()
