# Настройка Win11-lab для съёмки ЛР 2: всё качается через прокси хоста 10.0.2.2:8899.
$ErrorActionPreference = 'Continue'
$P = 'http://10.0.2.2:8899'
$env:HTTP_PROXY = $P; $env:HTTPS_PROXY = $P
[Environment]::SetEnvironmentVariable('HTTPS_PROXY', $P, 'User')
[Environment]::SetEnvironmentVariable('HTTP_PROXY', $P, 'User')
$ProgressPreference = 'SilentlyContinue'
$D = "$env:USERPROFILE\Downloads"
function Get($url, $out) { "скачиваю $out"; Invoke-WebRequest $url -OutFile "$D\$out" -Proxy $P -UseBasicParsing }
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 0 /f
Get 'https://update.code.visualstudio.com/latest/win32-arm64-user/stable' 'vscode.exe'
Start-Process "$D\vscode.exe" -ArgumentList '/VERYSILENT', '/MERGETASKS=!runcode,addtopath' -Wait
Get 'https://www.python.org/ftp/python/3.14.0/python-3.14.0-arm64.exe' 'python.exe'
Start-Process "$D\python.exe" -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1' -Wait
Get 'https://download.sysinternals.com/files/ProcessExplorer.zip' 'pe.zip'
Expand-Archive "$D\pe.zip" "$env:USERPROFILE\ProcessExplorer" -Force
Get 'https://aka.ms/vs/17/release/vs_BuildTools.exe' 'vs_BuildTools.exe'
"ставлю Build Tools (долго)"
Start-Process "$D\vs_BuildTools.exe" -ArgumentList '--quiet', '--wait', '--norestart', '--add', 'Microsoft.VisualStudio.Workload.VCTools', '--includeRecommended', '--add', 'Microsoft.VisualStudio.Component.VC.Tools.ARM64' -Wait
$code = "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd"
& $code --install-extension ms-vscode.cpptools
New-Item -ItemType Directory -Force "$env:USERPROFILE\Documents\sysprog-start\labs\02-debugger\.vscode" | Out-Null
curl.exe --noproxy '*' -s -o "$env:USERPROFILE\Documents\sysprog-start\labs\02-debugger\debug.c" http://10.0.2.2:8811/debug.c
'ГОТОВО' | Out-File "$env:USERPROFILE\Desktop\setup-done.txt"
"ГОТОВО"
