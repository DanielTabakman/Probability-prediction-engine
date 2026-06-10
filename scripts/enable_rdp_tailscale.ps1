# Enable Windows Remote Desktop for Tailscale-only access (run as Administrator).
# After this: connect from phone with Microsoft Remote Desktop to desktop-ge39o15

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

function Test-RdpListening {
    $conn = Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
    return [bool]$conn
}

function Restart-RdpServices {
    Write-Host "Restarting Remote Desktop Services..."
    $services = @("UmRdpService", "SessionEnv", "TermService")
    foreach ($name in $services) {
        $svc = Get-Service -Name $name -ErrorAction SilentlyContinue
        if ($svc -and $svc.Status -eq "Running") {
            Stop-Service -Name $name -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
    & net.exe stop TermService /y 2>$null | Out-Null
    Start-Sleep -Seconds 2
    & net.exe start TermService 2>$null | Out-Null
    Start-Sleep -Seconds 3
    Start-Service SessionEnv -ErrorAction SilentlyContinue
    Start-Service UmRdpService -ErrorAction SilentlyContinue
}

Write-Host "Enabling Remote Desktop (registry + Terminal Services API)..."
Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0

try {
    $ts = Get-CimInstance -Namespace root/cimv2/TerminalServices -ClassName Win32_TerminalServiceSetting -ErrorAction Stop
    $result = Invoke-CimMethod -InputObject $ts -MethodName SetAllowTsConnections -Arguments @{ AllowTsConnections = 1; ModifyFirewallSetting = 1 }
    if ($result.ReturnValue -ne 0) {
        Write-Warning "SetAllowTsConnections returned $($result.ReturnValue); continuing with manual firewall setup."
    }
} catch {
    Write-Warning "Terminal Services API unavailable; continuing with registry + manual firewall setup."
}

Write-Host "Ensuring Remote Desktop firewall rules..."
$rdpRules = @(Get-NetFirewallRule -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match "Remote Desktop" })
if ($rdpRules.Count -gt 0) {
    $rdpRules | Enable-NetFirewallRule -ErrorAction SilentlyContinue | Out-Null
} else {
    Write-Host "No built-in RDP firewall rules found; creating Tailscale-only rule..."
    $existing = Get-NetFirewallRule -DisplayName "PPE RDP Tailscale Inbound" -ErrorAction SilentlyContinue
    if (-not $existing) {
        New-NetFirewallRule `
            -DisplayName "PPE RDP Tailscale Inbound" `
            -Direction Inbound `
            -Action Allow `
            -Protocol TCP `
            -LocalPort 3389 `
            -InterfaceAlias "Tailscale" `
            -Enabled True | Out-Null
    } else {
        Enable-NetFirewallRule -DisplayName "PPE RDP Tailscale Inbound" | Out-Null
    }
}

Write-Host "Adding current user to Remote Desktop Users (if needed)..."
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$rdpMembers = @(Get-LocalGroupMember -Group "Remote Desktop Users" -ErrorAction SilentlyContinue)
if ($rdpMembers.Name -notcontains $currentUser) {
    Add-LocalGroupMember -Group "Remote Desktop Users" -Member $currentUser
}

try {
    Restart-RdpServices
} catch {
    Write-Warning "Could not restart TermService while you are logged in: $($_.Exception.Message)"
}

if (-not (Test-RdpListening)) {
    Write-Warning "Port 3389 is not listening yet. A reboot usually fixes this after first enable."
    Write-Host "Reboot now? (Y/N): " -NoNewline
    $answer = Read-Host
    if ($answer -match '^[Yy]') {
        Write-Host "Rebooting in 10 seconds (Ctrl+C to cancel)..."
        shutdown /r /t 10 /c "Enable Remote Desktop for Tailscale"
        exit 0
    }
}

$tsIp = $null
$tsExe = "${env:ProgramFiles}\Tailscale\tailscale.exe"
if (Test-Path -LiteralPath $tsExe) {
    $statusJson = & $tsExe status --json 2>$null
    if ($statusJson) {
        $status = $statusJson | ConvertFrom-Json
        if ($status.Self.Online -eq $true -and $status.Self.TailscaleIPs.Count -gt 0) {
            $tsIp = $status.Self.TailscaleIPs[0]
        }
    }
}

$listening = Test-RdpListening
Write-Host ""
if ($listening) {
    Write-Host "Remote Desktop is enabled and listening on port 3389."
} else {
    Write-Host "WARNING: Settings applied but port 3389 is not listening."
    Write-Host "Reboot the desktop, then try connecting from your phone."
}
Write-Host ""
Write-Host "Phone app: Microsoft Remote Desktop (NOT Termius). No gateway needed."
Write-Host "  PC name: 100.79.195.7 (or desktop-ge39o15)"
Write-Host "  Gateway: leave blank / off"
Write-Host "  User: add under PC settings -> User account, OR enter when prompted at connect"
Write-Host "  Password: Windows sign-in password (PIN does not work over RDP)"
Write-Host ""
Write-Host "Security: Tailscale only. Do not port-forward 3389 on your router."

if (-not $listening) {
    exit 1
}
