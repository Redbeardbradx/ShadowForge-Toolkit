function Invoke-ShadowPrivesc {
    Write-Host "`n[AXE] ShadowForge Privesc Checker - Hunting for easy wins . . ." -ForegroundColor Red
    Write-Host "=================================================================`n" -ForegroundColor DarkRed

    # 1. Are we already SYSTEM?
    Write-Host "[+] Current User Check" -ForegroundColor Cyan
    if ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name -eq "NT AUTHORITY\SYSTEM") {
        Write-Host "    JACKPOT -> Already running as SYSTEM!" -ForegroundColor Yellow
    }

    # 2. Unattended install files (clear-text passwords sometimes)
    Write-Host "`n[+] Searching for unattended install files" -ForegroundColor Cyan
    $files = @("c:\unattend.xml","c:\Windows\Panther\unattend.xml","c:\Windows\Panther\Unattend\unattend.xml","c:\sysprep\sysprep.xml")
    foreach ($f in $files) { if (Test-Path $f) { Write-Host "    Found: $f" -ForegroundColor Green; Get-Content $f | Select-String "password" } }

    # 3. AlwaysInstallElevated registry key (classic gold)
    Write-Host "`n[+] AlwaysInstallElevated Check (MSI auto-elevate)" -ForegroundColor Cyan
    $keys = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer", "HKCU:\SOFTWARE\Policies\Microsoft\Windows\Installer"
    $found = $false
    foreach ($key in $keys) {
        if (Get-ItemProperty -Path $key -Name "AlwaysInstallElevated" -ErrorAction SilentlyContinue) {
            if ((Get-ItemProperty $key).AlwaysInstallElevated -eq 1) { Write-Host "    VULNERABLE -> AlwaysInstallElevated = 1 in $key" -ForegroundColor Yellow; $found=$true }
        }
    }
    if (-not $found) { Write-Host "    Not vulnerable" -ForegroundColor Gray }

    # 4. Weak service permissions / unquoted paths (quick scan of top 20 services)
    Write-Host "`n[+] Checking for Unquoted Service Paths & Weak Permissions (top 20)" -ForegroundColor Cyan
    Get-WmiObject win32_service | Select-Object Name,PathName,StartMode | Where-Object {$_.State -eq "Running"} | 
    Sort-Object Name | Select-Object -First 20 | ForEach-Object {
        $path = $_.PathName.Split(" ")[0]
        if ($path -notmatch '^"' -and $path -match " ") { Write-Host "    Unquoted Path -> $($_.Name): $path" -ForegroundColor Yellow }
    }

    # 5. Hotfix check – missing important patches (KB examples)
    Write-Host "`n[+] Missing Privilege Escalation Hotfixes (sample)" -ForegroundColor Cyan
    $badKBs = @("KB4592471","KB4535680","KB4578013")  # PrintNightmare, Zerologon fixes, etc.
    $installed = Get-HotFix | Select-Object -ExpandProperty HotFixID
    foreach ($kb in $badKBs) {
        if ($installed -notcontains $kb) { Write-Host "    Missing -> $kb" -ForegroundColor Yellow }
    }

    Write-Host "`n[Done] Privesc quick-check complete!" -ForegroundColor Red
}