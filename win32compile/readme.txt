How to build executables and installer
======================================


Requirements
============

- python
- pywin32 extension
- pcapy extension
- libpcap / Winpcap 3.1
- nsis (to build installer)


win32compile.py
===============

  Compiler script. 
  Run as: "win32compile.py py2exe install" to build windows executable.


installer.nsi
=============

  NSIS installer script. 
  After building executable binaries through win32compile.py move into
  executable directory and run it through NSIS. For example:
  >>> C:\> C:\Programs\NSIS\makensis.exe "C:\builded_exe\installer.nsi"


build.bat
=========

  Build executables and installer automatically.