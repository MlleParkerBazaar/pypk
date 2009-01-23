@rem # build.bat
@rem # Compile python scripts in Windows stand-alone executables
@rem # and create a Windows installer by using NSIS. 


set NAME=pypk
set VER=v0.2
set EXE_BUILDER="win32compile.py"
set INST_BUILDER="installer.nsi"
set INSTALLER="C:\Programmi\NSIS\makensis.exe "

@goto main

:main
    @echo ------------------------------------------------------------------------------
    @echo py2exe: compiling to exe...
    @echo ------------------------------------------------------------------------------     
    %EXE_BUILDER% py2exe
    @if errorlevel 1 goto error
    cd ..
    cd "[w32-bin]-%NAME%_%VER%"
    dir
    @if errorlevel 1 goto error
    @echo ------------------------------------------------------------------------------
    @echo NSIS: building installer...
    @echo ------------------------------------------------------------------------------     
    %INSTALLER% %INST_BUILDER%
    @if errorlevel 1 goto error
    move "[w32-setup]-%NAME%_%VER%.exe" ..
    @if errorlevel 1 goto error
    @goto done

:done
    @echo ------------------------------------------------------------------------------
    @echo Build finished.
    @echo ------------------------------------------------------------------------------     
    @pause
    @exit


:error
    @echo ------------------------------------------------------------------------------
    @echo Build failed.
    @echo ------------------------------------------------------------------------------     
    @pause

