@echo off
setlocal enabledelayedexpansion

for /l %%i in (1, 1, 16) do (
    set dir=dump_3\split_%%i
    echo Running traverse.exe in !dir!
    start "" /D "!dir!" traverse.exe
)

endlocal