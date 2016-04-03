From the official ReadMe.txt:

> 1. What is PyCmd?  
> -----------------
> PyCmd is a 'smart' command prompt extension for Windows' cmd.exe; its purpose is to emulate a few power features of UNIX shells (decent Tab-completion, persistent history, etc.)

The [no-pywin32 branch][no-pywin32] contains only two changes to the original PyCmd:

 * Removes PyCmd's dependency on the pywin32 extensions.
 * Provides an additional setup script for building a script executable using [py2exe].

For details on what I changed and why, see [Changes.md]. I will try to remember to maintain this and keep it up to date with the official sources, but no guarantees.

[Changes.md]: Changes.md
[py2exe]: http://www.py2exe.org
[no-pywin32]: https://github.com/juntalis/pycmd-fork/tree/no-pywin32
