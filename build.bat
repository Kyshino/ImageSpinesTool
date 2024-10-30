@echo off
setlocal

rem Definir el nombre del ejecutable
set EXECUTABLE=main.exe


rem Elimina lo que no es necesario
call :RemovePycache components
call :RemovePycache translations
call :RemoveFile main.spec
call :RemoveFolder build
call :RemoveFolder dist


rem Crear el ejecutable
pyinstaller --onefile --windowed --distpath . main.py

rem Mover el ejecutable al directorio principal y eliminar el resto
if exist %EXECUTABLE% (
    echo El archivo ejecutable %EXECUTABLE% ha sido creado exitosamente.
    
    rem Mover el ejecutable a la carpeta principal si está en "dist"
    if exist dist\%EXECUTABLE% (
        move /Y dist\%EXECUTABLE% .
    )
    
    rem Limpiar carpetas y archivos generados por PyInstaller nuevamente
    if exist build rmdir /s /q build
    if exist dist rmdir /s /q dist
    if exist main.spec del main.spec

) else (
    echo Ha ocurrido un error al crear el ejecutable.
)

pause
exit /b

:RemovePycache
if "%~1"=="" (
    echo Por favor, proporciona el nombre de la carpeta como argumento.
    exit /b 1
)

set "folder=%~1"

rem Eliminar la carpeta __pycache__ dentro de la carpeta especificada
if exist "%folder%\__pycache__" (
    echo Eliminando %folder%\__pycache__...
    rmdir /s /q "%folder%\__pycache__"
    echo Carpeta %folder%\__pycache__ eliminada.
) else (
    echo La carpeta %folder%\__pycache__ no existe.
)

exit /b

:RemoveFile
if "%~1"=="" (
    echo Por favor, proporciona el nombre del archivo como argumento.
    exit /b 1
)

set "file=%~1"

rem Elimina arhcivo
if exist %file% del %file%

exit /b

:RemoveFolder
if "%~1"=="" (
    echo Por favor, proporciona el nombre de la carpeta como argumento.
    exit /b 1
)

set "folder=%~1"

rem Elimina carpeta
if exist %folder% rmdir /s /q %folder%

exit /b