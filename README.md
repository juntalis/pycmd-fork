From the official [ReadMe.txt]:

> 1. What is PyCmd?  
> -----------------
> PyCmd is a 'smart' command prompt extension for Windows' cmd.exe; its purpose is to emulate a few power features of UNIX shells (decent Tab-completion, persistent history, etc.)

This repository contains a number of my personal modifications to the [official PyCmd project][PyCmd] which - for good reasons - either weren't offered as a contribution to the official project or weren't accepted.

The [no-pywin32 branch][no-pywin32] contains a version of PyCmd with only my depedency-removing modifications. I will try to remember to keep the branches up to date with the official sources, but no guarantees.

For details on what I changed and why, see [Changes.md].

[ReadMe.txt]: ReadMe.txt
[Changes.md]: Changes.md
[py2exe]: http://www.py2exe.org
[pefile]: https://github.com/erocarrera/pefile
[PyCmd]: https://sourceforge.net/projects/pycmd/
[no-pywin32]: https://github.com/juntalis/pycmd-fork/tree/no-pywin32
