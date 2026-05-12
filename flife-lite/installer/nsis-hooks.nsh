!macro NSIS_HOOK_POSTINSTALL
  WriteRegStr HKCU "Software\FLIFE\FLIFE Lite" "InstallDir" "$INSTDIR"
!macroend

!macro NSIS_HOOK_POSTUNINSTALL
  DeleteRegKey HKCU "Software\FLIFE\FLIFE Lite"
!macroend
