# cleanup.ps1 - Standard user edition (non-admin)
# Lab-only, personal systems you control

Write-Host "[*] ShadowForge Lab Cleanup (Non-Admin) - Starting" -ForegroundColor Cyan

# Clear PowerShell history (user-level)
try {
    Clear-History -ErrorAction SilentlyContinue
    $historyPath = (Get-PSReadLineOption).HistorySavePath
    if (Test-Path $historyPath) {
        Remove-Item $historyPath -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[+] PowerShell history cleared" -ForegroundColor Green
} catch { Write-Host "[-] History clear issue: $_" -ForegroundColor Yellow }

# Flush DNS cache (works without admin on modern Windows)
try {
    Clear-DnsClientCache
    Write-Host "[+] DNS cache flushed" -ForegroundColor Green
} catch { Write-Host "[-] DNS flush failed (may require admin): $_" -ForegroundColor Yellow }

# Clear user temp files and recent items
try {
    Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:APPDATA\Microsoft\Windows\Recent\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\ThumbCacheToDelete\*" -Force -ErrorAction SilentlyContinue 2>$null
    Write-Host "[+] User TEMP and Recent files cleared" -ForegroundColor Green
} catch { Write-Host "[-] File cleanup partial: $_" -ForegroundColor Yellow }

# Optional: Clear browser artifacts if you targeted those (example for Edge/Chrome)
# Uncomment and adjust paths as needed
# Remove-Item "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\History" -Force -ErrorAction SilentlyContinue
# Remove-Item "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\History" -Force -ErrorAction SilentlyContinue

Write-Host "[*] Non-admin cleanup complete. Visible user tracks reduced." -ForegroundColor Cyan
Write-Host "[!] Event logs and system-level traces remain - require elevation." -ForegroundColor Red