#!/usr/bin/env python3
"""
Quick Start Script - Setup und Start aller Web APIs
"""

import subprocess
import time
import sys
import os

def run_cmd(cmd, desc):
    """Führe einen Befehl aus mit Fehlerbehandlung"""
    print(f"\n[*] {desc}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"    ✓ Erfolgreich")
            return True
        else:
            print(f"    ✗ Fehler: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    ✗ Timeout")
        return False
    except Exception as e:
        print(f"    ✗ Exception: {e}")
        return False

def check_installed(cmd, name):
    """Prüfe ob ein Programm installiert ist"""
    result = subprocess.run(f"{cmd} --version", shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"  ✓ {name} installiert")
        return True
    else:
        print(f"  ✗ {name} NICHT installiert")
        return False

def main():
    print("\n" + "="*80)
    print("WEB API TEST FRAMEWORK - QUICK START".center(80))
    print("="*80)

    # Prüfe Abhängigkeiten
    print("\n[1] Prüfe erforderliche Abhängigkeiten...")
    has_node = check_installed("node", "Node.js")
    has_python = check_installed("python", "Python")
    has_dotnet = check_installed("dotnet", "dotnet CLI")

    if not (has_node or has_python or has_dotnet):
        print("\n✗ Mindestens Node.js, Python oder dotnet erforderlich!")
        sys.exit(1)

    # Node.js Setup
    if has_node:
        print("\n[2] Setup Node.js/Express...")
        os.chdir("nodejs")
        if os.path.exists("package.json"):
            if run_cmd("npm install --silent", "npm dependencies installieren"):
                print("    Starten mit: npm start")
        os.chdir("..")

    # Python Setup
    if has_python:
        print("\n[3] Setup Python/FastAPI...")
        reqs = ["fastapi", "uvicorn", "aiohttp"]
        for req in reqs:
            run_cmd(f"{sys.executable} -m pip install {req} -q", f"{req} installieren")
        print("    Starten mit: python main.py")

    # C# Setup
    if has_dotnet:
        print("\n[4] Setup C#/.NET...")
        os.chdir("csharp")
        if os.path.exists("Api.csproj"):
            run_cmd("dotnet restore --nologo -q", ".NET dependencies restore")
            print("    Starten mit: dotnet run")
        os.chdir("..")

    print("\n" + "="*80)
    print("SETUP ABGESCHLOSSEN!".center(80))
    print("="*80)

    print("\n[*] Nächste Schritte:")
    print("    1. Starten Sie die APIs einzeln oder gemeinsam")
    print("    2. Führen Sie Tests aus:")
    print("       python test_orchestrator.py  (alle APIs automatisch)")
    print("    3. Oder starten Sie einzelne APIs manuell:")
    
    if has_node:
        print("       - Node.js:   cd nodejs && npm start")
    if has_python:
        print("       - Python:    cd python && python main.py")
    if has_dotnet:
        print("       - C#/.NET:   cd csharp && dotnet run")

    print("\n[*] Verfügbare Test-Skripte:")
    print("    - test_orchestrator.py   : Alle APIs + Tests")
    print("    - nodejs/tests/          : Node.js Tests")
    print("    - python/                : Python Tests")
    print("    - csharp/                : C# Tests")

    print("\n[*] Weitere Infos: Lesen Sie README.md\n")

if __name__ == "__main__":
    main()
