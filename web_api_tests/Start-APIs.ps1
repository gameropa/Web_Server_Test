# Start-APIs.ps1 - Startet alle APIs in separaten Fenstern

param(
    [switch]$KeepOpen = $true
)

$RootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Resolve-Path (Join-Path $RootPath "..\.venv\Scripts\python.exe") -ErrorAction SilentlyContinue

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "         STARTING API SERVERS IN SEPARATE WINDOWS           " -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Node.js
Write-Host "[1/3] Starting Node.js/Express Server (Port 3000)..." -ForegroundColor Green
$NodePath = Join-Path $RootPath "nodejs"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$NodePath'; Write-Host 'Node.js/Express Server' -ForegroundColor Cyan; `$env:NODE_ENV='production'; npm install --silent; node src/server.js"

Start-Sleep -Seconds 2

# Python
Write-Host "[2/3] Starting Python/FastAPI Server (Port 3001)..." -ForegroundColor Green
$PythonPath = Join-Path $RootPath "python"
$PyExe = if ($VenvPython) { $VenvPython } else { 'python' }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PythonPath'; Write-Host 'Python/FastAPI Server (uvicorn)' -ForegroundColor Cyan; & '$PyExe' -m uvicorn main:app --host 0.0.0.0 --port 3001 --workers 4"

Start-Sleep -Seconds 2

# C#
Write-Host "[3/3] Starting C#/.NET Server (Port 3002)..." -ForegroundColor Green
$CSharpPath = Join-Path $RootPath "csharp"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$CSharpPath'; Write-Host 'C#/.NET Server' -ForegroundColor Cyan; dotnet run -c Release"

Write-Host "`nAll servers starting in separate windows!" -ForegroundColor Green
Write-Host "Wait 10 seconds for initialization..." -ForegroundColor Yellow
Write-Host "`nThen run tests with:" -ForegroundColor Cyan
Write-Host "  python simple_test.py 3000 'Node.js/Express'" -ForegroundColor White
Write-Host "  python simple_test.py 3001 'Python/FastAPI'" -ForegroundColor White
Write-Host "  python simple_test.py 3002 'C#/.NET'" -ForegroundColor White

Write-Host "`nOr run all tests:" -ForegroundColor Cyan
Write-Host "  python run_tests_manual.py" -ForegroundColor White
Write-Host ""
