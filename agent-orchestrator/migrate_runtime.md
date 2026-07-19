# Runtime Directory Migration

## Overview

The agent-orchestrator `.runtime` directory has been moved **outside OneDrive** to avoid sync performance issues caused by:
- Large number of files (24,000+ runtime artifacts)
- Long directory names with timestamps and hashes
- High file churn from continuous job execution

## Changes Made

### 1. Configuration via Environment Variable

Added support for `AGENT_ORCHESTRATOR_RUNTIME` environment variable in:
- `src/agent_orchestrator/cli.py`
- `src/agent_orchestrator/runner.py`

### 2. New Default Location

**Before:** `%REPO_ROOT%/agent-orchestrator/.runtime/` (inside OneDrive)
**After:** `%LOCALAPPDATA%/agent-orchestrator/.runtime/` (outside OneDrive)

### 3. Updated Documentation

- Updated `README.md` with new default location and configuration instructions
- Updated `.gitignore` with clarifying comments

## Migration

### Automatic Migration

Run the migration script from the agent-orchestrator directory:

```powershell
# Dry run - shows what would be moved
.\migrate_runtime.ps1 -WhatIf

# Perform migration
.\migrate_runtime.ps1

# Force migration (overwrites existing destination)
.\migrate_runtime.ps1 -Force
```

### Manual Migration

1. Stop any running agent-orchestrator processes
2. Move the directory:
   ```powershell
   Move-Item "$REPO\agent-orchestrator\.runtime" "$env:LOCALAPPDATA\agent-orchestrator\.runtime"
   ```
3. Set the environment variable (optional):
   ```powershell
   $env:AGENT_ORCHESTRATOR_RUNTIME = "$env:LOCALAPPDATA\agent-orchestrator\.runtime"
   ```

## Configuration Options

### Option 1: Environment Variable (Recommended)

```powershell
# Set temporarily for current session
$env:AGENT_ORCHESTRATOR_RUNTIME = "C:\path\to\runtime"

# Set permanently (Windows)
[System.Environment]::SetEnvironmentVariable("AGENT_ORCHESTRATOR_RUNTIME", "C:\path\to\runtime", "User")
```

### Option 2: Use Default Location

No configuration needed. The system will automatically use:
- Windows: `%LOCALAPPDATA%\agent-orchestrator\.runtime`
- Other OS: `~/.local/share/agent-orchestrator/.runtime`

## Backwards Compatibility

- The old location (`agent-orchestrator/.runtime/`) is still supported
- Existing files in the old location will continue to work
- `.gitignore` still ignores both locations
- Migration is optional but recommended for OneDrive users

## Verification

After migration, verify with:

```powershell
# Check the doctor command uses the new location
.\orchestrate.py doctor

# Run a test job
.\orchestrate.py run .\examples\route-local.json
```

## Cleanup (Optional)

After successful migration, you can remove the old `.runtime` directory from the repository:

```powershell
Remove-Item "$REPO\agent-orchestrator\.runtime" -Recurse -Force
```

## Technical Details

### Modified Files

1. `src/agent_orchestrator/cli.py`
   - Added `get_runtime_root()` function
   - Updated all hardcoded `.runtime` paths to use the function

2. `src/agent_orchestrator/runner.py`
   - Added `get_runtime_root()` function
   - Updated `JobRunner.__init__()` to use dynamic runtime path

3. `tests/test_runner.py`
   - Updated test to set `AGENT_ORCHESTRATOR_RUNTIME` for isolated testing

4. `.gitignore`
   - Added clarifying comments about runtime location

5. `README.md`
   - Updated runtime directory documentation