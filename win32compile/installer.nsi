
;--------------------------------
; pftpd.nsi
;-------------------------------- 

; This script works with NSIS, a framework that permits to easily create
; Windows installers. After we created a Windows stand alone executable
; with py2exe we can use NSIS to create an installer able to:
; - put all necessary files generated by py2exe in the system programs
;   directory (C:\Programs).
; - create all necessary shortcuts in the start menu.
; - uninstall the program with a third-party executable (the
;   UNinstaller).


;--------------------------------
; Main
;--------------------------------

; global variables
!define PROG_NAME "pypk"
!define PROG_NAME_LONG "Py-port knocking"
!define VERSION "v0.2"
!define INSTALLER_NAME "[w32-setup]-${PROG_NAME}_${VERSION}.exe"

; The name of the file to generate
OutFile "${INSTALLER_NAME}"

; The name of the installer (the one that appears on the top of the window)
Name "${PROG_NAME_LONG}"

; The default installation directory (C:\Programs\pftpd)
InstallDir "$PROGRAMFILES\${PROG_NAME_LONG}"

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\${PROG_NAME}" "Install_Dir"

; License
LicenseText "License page"
LicenseData "LICENSE"


;--------------------------------
; Pages
;--------------------------------

Page license 
Page components
Page directory 
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles


;--------------------------------
; The stuff to install
;--------------------------------

Section "${PROG_NAME_LONG} (required)"

  SectionIn RO
  
  ; Set output path to the installation directory.
  
  SetOutPath $INSTDIR

  ; Create dirs
  
  CreateDirectory $INSTDIR\doc
  CreateDirectory $INSTDIR\doc\images
  
  ; Put files there
  
  File /r "*.html"
  File /r "*.jpg"
;  File /r "*.ico"
  File /r "*.png"
  File "HISTORY"
  File "LICENSE"
  File "README"
  File "TODO"

  ; /x $name --> exclusion
  File /r /x "${INSTALLER_NAME}" "*.exe" 
  File /r "*.zip"
  File /r "*.dll"
  File /r "*.pyd"  
  File /r "*.conf"
  
  ; Write the installation path into the registry

  
  WriteRegStr HKLM SOFTWARE\${PROG_NAME} \
              "Install_Dir" \
              "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
              "DisplayName" \
              "${PROG_NAME_LONG}"
  
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
              "UninstallString" \
              '"$INSTDIR\uninstall.exe"'
  
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
                "NoModify" \
                1
  
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}" \
                "NoRepair" \
                1
  
  WriteUninstaller "uninstall.exe"  


  ; .conf files association
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.conf" \
                   "Application" \
                   "wordpad.exe"

SectionEnd



;--------------------------------
; Start menu shortcuts (it can be disabled by the user during installation process)
;--------------------------------

Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\${PROG_NAME_LONG}"

  CreateShortCut "$SMPROGRAMS\${PROG_NAME_LONG}\knockd.lnk"  \
                 "$INSTDIR\knockd.exe"      

  CreateShortCut "$SMPROGRAMS\${PROG_NAME_LONG}\Uninstall.lnk" \
                 "$INSTDIR\uninstall.exe" \
                 "" \
                 "$INSTDIR\uninstall.exe" \
                 0

  CreateShortCut "$SMPROGRAMS\${PROG_NAME_LONG}\knocker.lnk"  \
                  $INSTDIR\knocker.exe --interactive  

  CreateShortCut "$SMPROGRAMS\${PROG_NAME_LONG}\Py-port knocking project.lnk" \
                 "$INSTDIR\doc\Py-port-knocking-project.html"  
  
  CreateShortCut "$SMPROGRAMS\${PROG_NAME_LONG}\knockd.conf.lnk"  \
                 "$INSTDIR\knockd.conf"

  CreateShortCut "$SMPROGRAMS\${PROG_NAME_LONG}\knockd (background).lnk"  \
                 "$INSTDIR\knockdw.exe"  

SectionEnd


;--------------------------------
; Uninstaller
;--------------------------------

Section "Uninstall"

  ; Remove registry keys

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PROG_NAME}"
  DeleteRegKey HKLM SOFTWARE\${PROG_NAME}

  ; Remove shortcuts and shortcut directories

  Delete "$SMPROGRAMS\${PROG_NAME_LONG}\*.*"
  RMDir "$SMPROGRAMS\${PROG_NAME_LONG}"
  RMDir "$INSTDIR"

  ; Remove files and uninstaller
 
  Delete "$INSTDIR\*"
  Delete "$INSTDIR\doc\*"
  Delete "$INSTDIR\doc\pftpd_files\**"
  Delete "$INSTDIR\images\*"
  
  ; Remove program directories
  RMDir $INSTDIR\doc\pftpd_files
  RMDir $INSTDIR\doc
  RMDir $INSTDIR\images
  RMDir "$INSTDIR"
  
SectionEnd


;--------------------------------
; Notes
;--------------------------------

;; execute on startup
; Function .onInit
;  Call
; FunctionEnd

;; pop-up a message box
; Function some_fun
;    MessageBox MB_OK "Bla"
; FunctionEnd

