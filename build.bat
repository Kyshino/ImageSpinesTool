@echo off
setlocal enabledelayedexpansion

:: Color configuration (0=Black background, A=Light green text)
color 0A

:: Window title
title Building Image Spines Tool

:: Banner
echo ===================================
echo    Building Image Spines Tool
echo ===================================
echo.

:: Set executable name
set EXECUTABLE=ImagesSpinesTool.exe

:: Remove all __pycache__ folders recursively
echo [INFO] Removing all __pycache__ folders...
for /d /r %%d in (*__pycache__*) do (
    echo [INFO] Removing %%d
    rmdir /s /q "%%d"
)

:: Remove unnecessary files
call :RemoveFile ImagesSpinesTool.spec
call :RemoveFolder build
call :RemoveFolder dist

:: Prepare PyInstaller base command
set PYINSTALLER_CMD=pyinstaller --onefile --windowed --noconsole --name "ImagesSpinesTool" --distpath .

:: Add icon if exists, but don't include it in the resources
if exist "images/favicon.ico" (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --icon="images/favicon.ico"
    echo [INFO] Adding favicon to executable
) else (
    echo [WARN] favicon.ico not found, continuing without icon
)

:: Create executable
echo [INFO] Creating executable...
%PYINSTALLER_CMD% --add-data "images;images" --add-data "translations;translations" main.py

:: Move executable to root directory and clean up
if exist %EXECUTABLE% (
    echo [SUCCESS] Executable %EXECUTABLE% has been created successfully.
    
    :: Move executable to root if it's in dist
    if exist dist\%EXECUTABLE% (
        echo [INFO] Moving executable to root folder...
        move /Y dist\%EXECUTABLE% .
    )
    
    :: Clean up PyInstaller generated files
    echo [INFO] Cleaning temporary files...
    if exist build rmdir /s /q build
    if exist dist rmdir /s /q dist
    if exist ImagesSpinesTool.spec del ImagesSpinesTool.spec
    
    :: Remove all __pycache__ folders after build
    echo [INFO] Final cleanup of __pycache__ folders...
    for /d /r %%d in (*__pycache__*) do (
        echo [INFO] Removing %%d
        rmdir /s /q "%%d"
    )

) else (
    echo [ERROR] Failed to create executable.
)

exit /b

:RemoveFile
if "%~1"=="" (
    echo [ERROR] Please provide a file name as argument.
    exit /b 1
)

set "file=%~1"

:: Remove file
if exist %file% (
    echo [INFO] Removing file %file%...
    del %file%
)

exit /b

:RemoveFolder
if "%~1"=="" (
    echo [ERROR] Please provide a folder name as argument.
    exit /b 1
)

set "folder=%~1"

:: Remove folder
if exist %folder% (
    echo [INFO] Removing folder %folder%...
    rmdir /s /q %folder%
)

exit /b