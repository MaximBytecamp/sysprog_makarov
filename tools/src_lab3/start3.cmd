@echo off
rem Запуск VS Code для съёмки ЛР 3: окружение MSVC x64, порт отладки 9365, проброс 0.0.0.0:9366 -> 127.0.0.1:9365.
taskkill /im Code.exe /f >nul 2>&1
timeout /t 3 /nobreak >nul
set W=%USERPROFILE%\Documents\sysprog-start\labs\03-libraries
if not exist "%W%" mkdir "%W%"
rmdir /s /q C:\vsc\data\Backups C:\vsc\data\User\workspaceStorage 2>nul
if not exist C:\vsc\data\User mkdir C:\vsc\data\User
curl.exe --noproxy * -s -o C:\vsc\data\User\settings.json http://10.0.2.2:8811/settings.json
curl.exe --noproxy * -s -o "%W%\libs.c" http://10.0.2.2:8811/lab3/libs.c
del /q "%W%\libs.exe" "%W%\*.obj" 2>nul
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=9366 connectaddress=127.0.0.1 connectport=9365 >nul
netsh advfirewall firewall add rule name=cdp9366 dir=in action=allow protocol=TCP localport=9366 >nul
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
cd /d "%W%"
start "" "%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe" --user-data-dir C:\vsc\data --remote-debugging-port=9365 --disable-renderer-backgrounding --disable-backgrounding-occluded-windows --folder-uri file:///C:/Users/user/Documents/sysprog-start/labs/03-libraries

