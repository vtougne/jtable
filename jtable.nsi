OutFile ".\dist\jtable_setup.exe"
InstallDir "$LOCALAPPDATA\Microsoft\WindowsApps"
RequestExecutionLevel user

Section
    SetOutPath "$INSTDIR"
    File ".\dist\jtable.exe"
    CreateShortcut "$DESKTOP\jtable.lnk" "$INSTDIR\jtable.exe"
SectionEnd
