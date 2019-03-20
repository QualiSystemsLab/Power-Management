@echo off

echo.
echo Cleaning Local Pypi Folder
rd /S /Q "C:\Program Files (x86)\QualiSystems\CloudShell\Server\Config\Pypi Server Repository\cloudshell_power_lib\"

echo.
echo Cleaning Distribution Folder
rd /S /Q "dist"

echo.
echo Updating Dependencies
@py -2 -m pip install --upgrade setuptools wheel twine

echo.
echo Building Package
py -2 setup.py sdist bdist_wheel

echo.
echo Copying to local Pypi
xcopy /S "dist" "C:\Program Files (x86)\QualiSystems\CloudShell\Server\Config\Pypi Server Repository\cloudshell_power_lib\"


echo.
echo Complete!
pause
