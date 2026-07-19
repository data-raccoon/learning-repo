#!/usr/bin/env powershell
# Agent Orchestrator Runtime Migration Script
# 
# Moves the .runtime directory from inside the repository (OneDrive) to outside OneDrive
# to avoid OneDrive sync issues with large numbers of files.

param(
    [switch]$Force,
    [string]$SourcePath,
    [string]$DestinationPath
)

# Default paths
$repoRoot = $PSScriptRoot | Split-Path -Parent
$defaultSource = Join-Path $repoRoot ".runtime"
$localAppData = $env:LOCALAPPDATA
$defaultDestination = Join-Path $localAppData "agent-orchestrator\.runtime"

$source = if ($SourcePath) { $SourcePath } else { $defaultSource }
$destination = if ($DestinationPath) { $DestinationPath } else { $defaultDestination }

function Write-Message {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

try {
    # Check if source exists
    if (-not (Test-Path $source)) {
        Write-Message "Source runtime directory does not exist: $source" "INFO"
        Write-Message "Nothing to migrate. The runtime directory may already be in the new location." "SUCCESS"
        exit 0
    }
    
    Write-Message "Starting runtime directory migration..." "INFO"
    Write-Message "Source: $source" "INFO"
    Write-Message "Destination: $destination" "INFO"
    
    # Check if destination already exists
    if (Test-Path $destination) {
        if (-not $Force) {
            Write-Message "Destination already exists: $destination" "WARNING"
            Write-Message "Use -Force to overwrite or manually clean up the destination." "ERROR"
            exit 1
        }
        Write-Message "Removing existing destination due to -Force flag..." "WARNING"
        Remove-Item $destination -Recurse -Force -ErrorAction Stop
    }
    
    # Create parent directory if it doesn't exist
    $destParent = Split-Path $destination -Parent
    if (-not (Test-Path $destParent)) {
        New-Item -ItemType Directory -Path $destParent -Force | Out-Null
        Write-Message "Created parent directory: $destParent" "INFO"
    }
    
    # Move the directory
    Write-Message "Moving runtime directory..." "INFO"
    Move-Item -Path $source -Destination $destination -Force -ErrorAction Stop
    
    # Verify the move
    if (Test-Path $destination -PathType Container) {
        Write-Message "Migration completed successfully!" "SUCCESS"
        Write-Message "Runtime directory is now at: $destination" "SUCCESS"
        Write-Message "Set AGENT_ORCHESTRATOR_RUNTIME=$destination to use the new location." "INFO"
        exit 0
    } else {
        Write-Message "Migration failed - destination not found after move." "ERROR"
        exit 1
    }
    
} catch {
    Write-Message "Migration failed: $_" "ERROR"
    Write-Message "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
}