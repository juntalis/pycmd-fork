# encoding: utf-8
"""
setup-py2exe.py
Alternative setup script using py2exe instead of cx_Freeze.
"""
from distutils.core import setup
# noinspection PyPackageRequirements
import py2exe, sys, os, copy, platform

arch = platform.architecture()[0]
is_x64 = arch.startswith('64')
loose_files = ['example-init.py', 'pycmd_public.py']
noext = lambda filepath: os.path.splitext(filepath)[0]

info = {
    'name' : 'PyCmd',
    'version' : '0.8',
    'author' : 'Horea Haitonic',
    'author_email' : 'horeah@gmail.com',
    'maintainer' : 'Charles Grunwald (Juntalis)',
    'maintainer_email' : 'ch@rls.rocks',
    'description' : 'Smart windows shell',
    'url' : 'http://sourceforge.net/projects/pycmd/',
    'license' : 'GNU GPL',
    'classifiers' : (
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Operating System :: Microsoft :: Windows',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: System Shells',
        'Topic :: Terminals',
    )
}

# See http://www.py2exe.org/index.cgi/ListOfOptions for
# information on the following options.
info.update({
    'zipfile': 'PyCmd.zip' if is_x64 else None,
    'console': [ {
        'script': 'bootstrap.py',
        'dest_base': 'PyCmd',
        'icon_resources': [ (0, 'PyCmd.ico') ]
    } ],
    'data_files': [('', loose_files)],
    'options': {
        'py2exe': {
            #'xref': 1,
            'optimize': 2,
            'unbuffered': 1,
            'compressed': 1,
            'bundle_files': 1,
            # 'skip_archive': 0,
            # 'custom_boot_script': '',
            'excludes': map(noext, loose_files),
            'includes': [ 'code' ],
            'dll_excludes': [
                'w9xpopen.exe',
                'API-MS-Win-Core-LocalRegistry-L1-1-0.dll',
                'API-MS-Win-Core-ProcessThreads-L1-1-0.dll',
                'POWRPROF.dll',
                'KERNELBASE.dll',
                'API-MS-Win-Security-Base-L1-1-0.dll'
            ],
        }
    }
})

# Ensure the py2exe command is run - either
# by replacing existing 'build' commands or
# by just inserting the command line ourselves.
has_py2exe = False
argvcopy = copy.copy(sys.argv)
for idx,arg in enumerate(argvcopy):
    if arg == 'build':
        sys.argv[idx] = 'py2exe'
        has_py2exe = True
    elif arg == 'py2exe':
        has_py2exe = True

if not has_py2exe:
    sys.argv.insert(1, 'py2exe')

setup(**info)

