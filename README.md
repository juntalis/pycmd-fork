From the official ReadMe.txt:

> 1. What is PyCmd?  
> -----------------
> PyCmd is a 'smart' command prompt extension for Windows' cmd.exe; its purpose is to emulate a few power features of UNIX shells (decent Tab-completion, persistent history, etc.)

This repository contains a number of my personal modifications to the [official PyCmd project](https://sourceforge.net/projects/pycmd/) which, for good reasons, either weren't offered as a contribution to the official project or weren't accepted.

I learned early on that Horea's (The project's author) philosophy for the project is to improve usability of Command Prompt without sacrificing compatibility with it. In other words, any command that is executed in PyCmd should also be able to be executed in Command Prompt with the same results. (A completely understandable philosophy. I just happen to take a different approach with my modifications) As a result, some of the changes in this repository weren't offered as a contribution, due to the fact that they break that compatibility.

Additionally, my local copy of the PyCmd's source has more or less become a sandbox for me to play around and test out other things, so some of the additions I made to the code weren't offered as contributions, simply because they weren't intended to add any additional usefulness - but instead a way for me to try out something.

A number of the modifications made in this repository were, at one point or another, offered as a contribution to the official project. The ones that aren't in the official tree were rejected, usually due to the fact that they either made the project harder to maintain or they were pointless for the average end user.

Lastly, I unfortunately didn't start tracking my changes to the project until about a year after I started making them, so maintain the ability to fetch changes from the official tree, I had to pull the latest version, and go through my changes one by one to reimplment them. As a result, the first few commits will most likely consist of quite a large number of changes, with no real versioning history.