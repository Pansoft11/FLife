# Portable Edition Guide

Extract `FLIFE-Lite-Portable.zip` to a writable folder or USB drive.

Set `FLIFE_PORTABLE_HOME` to force license and project state to remain beside the portable deployment:

```powershell
$env:FLIFE_PORTABLE_HOME="$PWD\data"
.\FLIFE-Lite.exe
```

Updater is disabled for portable RC1 builds.
