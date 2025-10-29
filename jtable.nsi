OutFile ".\dist\jtable_setup.exe"
InstallDir "$LOCALAPPDATA\Microsoft\WindowsApps"
RequestExecutionLevel user

Section
    SetOutPath "$INSTDIR"
    File ".\dist\jtable.exe"
    File ".\dist\jtable-template.exe"
    File ".\dist\jtable-play.exe"
    File ".\dist\jtable-filter.exe"
    CreateShortcut "$DESKTOP\jtable.lnk" "$INSTDIR\jtable.exe"

SectionEnd
