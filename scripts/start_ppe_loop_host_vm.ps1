# Host PC (Administrator): start the Hyper-V loop VM and make it start with Windows.
param(
    [string]$Name = "PPE-Loop-Host",
    [int]$StartDelaySeconds = 60
)

$ErrorActionPreference = "Stop"

$vms = @(Get-VM)
if (-not $vms) {
    throw "No Hyper-V VMs found on this host."
}

Write-Host "=== Hyper-V VMs ==="
$vms | Format-Table Name, State, AutomaticStartAction, AutomaticStartDelay, Uptime -AutoSize

$targets = @($vms | Where-Object { $_.Name -eq $Name })
if (-not $targets) {
    $targets = @($vms | Where-Object { $_.Name -match "ppe|loop-host|ppeloop" })
}
if (-not $targets) {
    throw "No VM named '$Name' (or matching ppe/loop-host). Start the right name from the table above."
}

foreach ($vm in $targets) {
    if ($vm.State -ne "Running") {
        Write-Host "Starting $($vm.Name)..."
        Start-VM -Name $vm.Name
    } else {
        Write-Host "$($vm.Name) is already Running."
    }
    Set-VM -Name $vm.Name -AutomaticStartAction Start -AutomaticStartDelay $StartDelaySeconds
    Write-Host "Set $($vm.Name) AutomaticStartAction=Start delay=${StartDelaySeconds}s"
}

Write-Host ""
Write-Host "=== After ==="
Get-VM | Format-Table Name, State, AutomaticStartAction, AutomaticStartDelay, Uptime -AutoSize
