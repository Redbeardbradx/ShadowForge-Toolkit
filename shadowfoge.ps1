# ShadowForge - Ethical Pentesting Framework by Redbeardbradx
Clear-Host
Write-Host "[AXE] ShadowForge loaded - By Redbeardbradx" -ForegroundColor Red
Write-Host ""

# Load all modules
Import-Module .\Modules\Recon.psm1 -Force
Import-Module .\Modules\Privesc.psm1 -Force

# Run both
Invoke-ShadowRecon
Write-Host "`n`n"
Invoke-ShadowPrivesc