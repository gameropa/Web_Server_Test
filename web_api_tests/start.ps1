# Web API Test Framework - Start Script
# PowerShell Script zum Starten aller APIs und Tests

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "nodejs", "python", "csharp", "test", "orchestrator")]
    [string]$Mode = "all"
)

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     WEB API TEST FRAMEWORK - START SCRIPT                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

$RootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$WebApiPath = Join-Path $RootPath "web_api_tests"

function Start-NodeJsServer {
    Write-Host "[1/4] Starting Node.js/Express Server..." -ForegroundColor Green
    $NodePath = Join-Path $WebApiPath "nodejs"
    if (Test-Path "$NodePath\package.json") {
        Write-Host "     Installing npm packages..." -ForegroundColor Yellow
        Push-Location $NodePath
        npm install --silent
        Pop-Location
    }
    Push-Location $NodePath
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k node src\server.js" -NoNewWindow
    Pop-Location
    Start-Sleep -Seconds 2
    Write-Host "     ✓ Node.js running on port 3000" -ForegroundColor Green
}

function Start-PythonServer {
    Write-Host "[2/4] Starting Python/FastAPI Server..." -ForegroundColor Green
    $PythonPath = Join-Path $WebApiPath "python"
    
    # Install packages
    Write-Host "     Installing Python packages..." -ForegroundColor Yellow
    python -m pip install fastapi uvicorn aiohttp -q 2>$null
    
    Push-Location $PythonPath
    Start-Process -FilePath "python.exe" -ArgumentList "main.py" -NoNewWindow
    Pop-Location
    Start-Sleep -Seconds 3
    Write-Host "     ✓ Python/FastAPI running on port 3001" -ForegroundColor Green
}

function Start-CSharpServer {
    Write-Host "[3/4] Starting C#/.NET Server..." -ForegroundColor Green
    $CSharpPath = Join-Path $WebApiPath "csharp"
    
    Push-Location $CSharpPath
    Start-Process -FilePath "dotnet.exe" -ArgumentList "run", "-c", "Release" -NoNewWindow
    Pop-Location
    Start-Sleep -Seconds 3
    Write-Host "     ✓ C#/.NET running on port 3002" -ForegroundColor Green
}

function Start-RustServer {
    Write-Host "[4/4] Starting Rust/Actix Server..." -ForegroundColor Green
    $RustPath = Join-Path $WebApiPath "rust"
    
    Push-Location $RustPath
    Start-Process -FilePath "cargo.exe" -ArgumentList "run", "--release", "--bin", "server" -NoNewWindow
    Pop-Location
    Start-Sleep -Seconds 3
    Write-Host "     ✓ Rust/Actix running on port 3003" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "`n[*] Running tests in 10 seconds..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    
    Write-Host "`n" -ForegroundColor Cyan
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                  RUNNING GLOBAL TESTS                          ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "`n"
    
    Push-Location $WebApiPath
    python test_orchestrator.py
    Pop-Location
}

function Show-Menu {
    Write-Host "Available modes:" -ForegroundColor Cyan
    Write-Host "  all           - Start all 4 APIs" -ForegroundColor White
    Write-Host "  nodejs        - Start only Node.js/Express" -ForegroundColor White
    Write-Host "  python        - Start only Python/FastAPI" -ForegroundColor White
    Write-Host "  csharp        - Start only C#/.NET" -ForegroundColor White
    Write-Host "  test          - Run all 4 APIs + tests (orchestrator)" -ForegroundColor Green
    Write-Host "  orchestrator  - Same as 'test'" -ForegroundColor Green
    Write-Host "`nUsage: .\start.ps1 -Mode <mode>" -ForegroundColor Yellow
    Write-Host "Example: .\start.ps1 -Mode test`n" -ForegroundColor Yellow
}

# Main
switch ($Mode) {
    "all" {
        Write-Host "Starting all APIs..." -ForegroundColor Cyan
        Start-NodeJsServer
        Start-PythonServer
        Start-CSharpServer
        Start-RustServer
        Write-Host "`n✓ All servers started!" -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow
    }
    "nodejs" {
        Start-NodeJsServer
    }
    "python" {
        Start-PythonServer
    }
    "csharp" {
        Start-CSharpServer
    }
    "test" {
        Run-Tests
    }
    "orchestrator" {
        Run-Tests
    }
    default {
        Show-Menu
    }
}

Write-Host "`n"
