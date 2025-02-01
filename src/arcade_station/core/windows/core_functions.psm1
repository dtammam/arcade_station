function Update-RegistryKey {
    <#
    .SYNOPSIS
        Updates a registry key with a specified value.
    .PARAMETER Path
        The registry path.
    .PARAMETER Name
        The name of the registry key.
    .PARAMETER Value
        The value to set.
    #>
    param (
        [string]$Path,
        [string]$Name,
        [string]$Value
    )

    try {
        New-ItemProperty -Path $Path -Name $Name -Value $Value -PropertyType String -Force
        Write-Information "Modified [$Name] to [$Value] at [$Path]."
    } catch {
        Write-Information "Failed to update registry key: [$($_.Exception.Message)]"
    }
}

function Restart-ComputerSafely {
    <#
    .SYNOPSIS
        Restarts the computer safely.
    #>
    try {
        Write-Information "Restarting computer now..."
        Restart-ComputerSafely
    } catch {
        Write-Information "Failed to restart computer: [$($_.Exception.Message)]"
    }
}