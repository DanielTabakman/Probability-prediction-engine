# Enable Windows Remote Desktop for Tailscale-only access (run as Administrator).
# After this: connect from phone with Microsoft Remote Desktop to desktop-ge39o15

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

Write-Host "Enabling Remote Desktop..."
Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0

Write-Host "Enabling RDP firewall rules..."
Enable-NetFirewallRule -DisplayGroup "Remote Desktop" -ErrorAction SilentlyContinue

$tsIp = $null
$tsExe = "${env:ProgramFiles}\Tailscale\tailscale.exe"
if (Test-Path -LiteralPath $tsExe) {
    $status = & $tsExe status --json 2>$null | ConvertFrom-Json
    foreach ($peer in $status.Peer.PSObject.Properties) {
        $p = $peer.Value
        if ($p.HostName -and ($p.Online -eq $true) -and ($p.Active -eq $true)) {
            if ($p.TailscaleIPs -and $p.TailscaleIPs.Count -gt 0) {
                $tsIp = $p.TailscaleIPs[0]
                break
            }
        }
    }
}

Write-Host ""
Write-Host "Remote Desktop is enabled."
Write-Host "Connect from phone (Microsoft Remote Desktop app):"
Write-Host "  PC name: desktop-ge39o15   (Tailscale hostname)"
if ($tsIp) { Write-Host "  Tailscale IP (alt): $tsIp" }
Write-Host "  User:    $env:USERNAME"
Write-Host "  Password: your Windows login password"
Write-Host ""
Write-Host "Security: use Tailscale hostname only — do not port-forward 3389 on your router."
