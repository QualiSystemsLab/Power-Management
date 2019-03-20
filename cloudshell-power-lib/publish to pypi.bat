@echo off

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
echo Uploading to Pypi
py -2 -m twine upload dist/*


echo.
echo Complete!
pause