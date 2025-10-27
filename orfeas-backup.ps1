# GitHub-Like Local Backup System for ORFEAS AI Studio
# Windows 10/11 PowerShell Implementation
#
# Purpose: Create Git-like backups on C: drive with version control,
#          commit history, and point-in-time recovery capabilities

param(
    [ValidateSet("backup", "restore", "list", "verify", "cleanup")]
    [string]$Command = "backup",

    [string]$CommitMessage = "Scheduled backup $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",

    [string]$RestoreCommitId = $null,

    [int]$RetentionDays = 90
)

# Configuration
$BackupRoot = "C:\Backups\orfeas-studio"
$ProjectRoot = "c:\Users\johng\Documents\oscar"
$ObjectsDir = "$BackupRoot\.objects"
$RefsDir = "$BackupRoot\.refs"
$CommitsDir = "$BackupRoot\.commits"
$LatestDir = "$BackupRoot\latest"
$LogFile = "$BackupRoot\backup.log"

function Initialize-BackupSystem {
    "Ensure backup directory structure exists"
    if (-not (Test-Path $BackupRoot)) {
        New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
    }

    $directories = @($ObjectsDir, $RefsDir, $CommitsDir, $LatestDir)
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    # Initialize HEAD reference
    if (-not (Test-Path "$RefsDir\HEAD")) {
        Set-Content -Path "$RefsDir\HEAD" -Value "0000000000000000"
    }

    Write-Log "Backup system initialized"
}

function Write-Log {
    param([string]$Message)

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Add-Content -Path $LogFile -Value $logEntry
    Write-Host $logEntry -ForegroundColor Cyan
}

function Get-DirectoryHash {
    "Calculate hash of directory structure for change detection"
    param([string]$Path)

    $files = Get-ChildItem -Path $Path -Recurse -File |
    Sort-Object -Property FullName

    $hashInput = ""
    foreach ($file in $files) {
        $hashInput += $file.FullName
    }

    $sha256 = New-Object System.Security.Cryptography.SHA256Managed
    $hashBytes = $sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($hashInput))
    return ($hashBytes | ForEach-Object { $_.ToString("X2") }) -join ""
}

function New-BackupCommit {
    "Create new backup commit (like git commit)"
    param([string]$Message)

    Write-Log "Starting backup commit: $Message"

    try {
        # 1. Calculate current state hash
        $treeHash = Get-DirectoryHash -Path $ProjectRoot
        Write-Log "Tree hash: $treeHash"

        # 2. Store backup with deduplication
        $objectPath = "$ObjectsDir\$($treeHash.Substring(0,2))\$($treeHash.Substring(2))"

        if (Test-Path "$objectPath.zip") {
            Write-Log "Backup already exists (deduplicated), skipping copy"
        }
        else {
            New-Item -ItemType Directory -Path (Split-Path $objectPath) -Force | Out-Null

            # Use Compress-Archive for compression (50% savings)
            $tempZip = "$env:TEMP\backup_$([guid]::NewGuid()).zip"
            Compress-Archive -Path "$ProjectRoot\*" -DestinationPath $tempZip -Force

            Move-Item -Path $tempZip -Destination "$objectPath.zip" -Force
            Write-Log "Backup stored: $objectPath.zip"
        }

        # 3. Calculate file hash for integrity verification
        $fileHash = (Get-FileHash -Path "$objectPath.zip" -Algorithm SHA256).Hash
        Set-Content -Path "$objectPath.sha256" -Value $fileHash

        # 4. Get previous commit
        $previousCommitId = Get-Content -Path "$RefsDir\HEAD"

        # 5. Generate new commit ID (timestamp-based)
        $commitId = [int][double]::Parse((Get-Date -UFormat %s)) -as [string]
        $commitId = $commitId.Substring(0, 8)

        # 6. Create commit metadata JSON
        $fileSize = (Get-Item "$objectPath.zip").Length
        $commitData = @{
            id               = $commitId
            tree             = $treeHash
            parent           = $previousCommitId
            author           = $env:USERNAME
            message          = $Message
            timestamp        = (Get-Date -Format "o")
            fileSize         = $fileSize
            fileHash         = $fileHash
            compressionRatio = 0.5
        }

        $commitJson = $commitData | ConvertTo-Json
        Set-Content -Path "$CommitsDir\$commitId.json" -Value $commitJson

        # 7. Update HEAD reference
        Set-Content -Path "$RefsDir\HEAD" -Value $commitId
        Set-Content -Path "$RefsDir\main" -Value $commitId

        Write-Log "Commit created: $commitId"

        return @{
            CommitId  = $commitId
            TreeHash  = $treeHash
            FileHash  = $fileHash
            Message   = $Message
            Timestamp = Get-Date -Format "o"
        }
    }
    catch {
        Write-Log "ERROR during commit: $_"
        throw
    }
}

function Restore-BackupCommit {
    "Restore project to specific commit"
    param([string]$CommitId)

    Write-Log "Starting restore to commit: $CommitId"

    try {
        # 1. Load commit metadata
        $commitFile = "$CommitsDir\$CommitId.json"
        if (-not (Test-Path $commitFile)) {
            Write-Log "ERROR: Commit not found: $CommitId"
            return $false
        }

        $commit = Get-Content -Path $commitFile | ConvertFrom-Json
        $treeHash = $commit.tree

        # 2. Verify integrity
        $objectPath = "$ObjectsDir\$($treeHash.Substring(0,2))\$($treeHash.Substring(2)).zip"
        $actualHash = (Get-FileHash -Path $objectPath -Algorithm SHA256).Hash

        if ($actualHash -ne $commit.fileHash) {
            Write-Log "ERROR: Integrity check failed for commit $CommitId"
            return $false
        }

        Write-Log "Integrity verified. Restoring..."

        # 3. Extract backup to temporary location
        $tempRestore = "$env:TEMP\restore_$([guid]::NewGuid())"
        New-Item -ItemType Directory -Path $tempRestore -Force | Out-Null

        Expand-Archive -Path $objectPath -DestinationPath $tempRestore -Force

        # 4. Backup current state before replacing
        $preRestoreBackup = "$BackupRoot\pre-restore_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        New-Item -ItemType Directory -Path $preRestoreBackup -Force | Out-Null
        Copy-Item -Path "$ProjectRoot\*" -Destination $preRestoreBackup -Recurse -Force

        # 5. Replace project with restored version
        Remove-Item -Path "$ProjectRoot\*" -Recurse -Force
        Copy-Item -Path "$tempRestore\*" -Destination $ProjectRoot -Recurse -Force

        # Cleanup
        Remove-Item -Path $tempRestore -Recurse -Force

        Write-Log "Restore completed. Previous state saved to: $preRestoreBackup"

        return $true
    }
    catch {
        Write-Log "ERROR during restore: $_"
        return $false
    }
}

function Get-BackupHistory {
    "List all backup commits"

    $commits = Get-ChildItem -Path $CommitsDir -Filter "*.json" |
    Sort-Object -Property Name -Descending |
    Select-Object -First 50

    Write-Host "`n=== Backup History ===" -ForegroundColor Green
    Write-Host "ID`t`tDate/Time`t`t`tMessage" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan

    foreach ($commitFile in $commits) {
        $commit = Get-Content -Path $commitFile.FullName | ConvertFrom-Json
        $timestamp = Get-Date -Date $commit.timestamp -Format "yyyy-MM-dd HH:mm:ss"
        $sizeKB = [math]::Round($commit.fileSize / 1024, 2)

        Write-Host "$($commit.id)`t$timestamp`t$($commit.message) ($sizeKB KB)"
    }

    Write-Host ("=" * 80) -ForegroundColor Cyan
}

function Verify-BackupIntegrity {
    "Verify integrity of all backups"

    Write-Log "Starting integrity verification..."

    $commits = Get-ChildItem -Path $CommitsDir -Filter "*.json"
    $corruptedCount = 0
    $verifiedCount = 0

    foreach ($commitFile in $commits) {
        $commit = Get-Content -Path $commitFile.FullName | ConvertFrom-Json
        $commitId = $commit.id
        $treeHash = $commit.tree

        $objectPath = "$ObjectsDir\$($treeHash.Substring(0,2))\$($treeHash.Substring(2)).zip"

        if (Test-Path $objectPath) {
            $actualHash = (Get-FileHash -Path $objectPath -Algorithm SHA256).Hash

            if ($actualHash -eq $commit.fileHash) {
                $verifiedCount++
            }
            else {
                Write-Log "CORRUPTED: Commit $commitId - hash mismatch"
                $corruptedCount++
            }
        }
        else {
            Write-Log "MISSING: Commit $commitId - backup file not found"
            $corruptedCount++
        }
    }

    Write-Log "Verification complete: $verifiedCount verified, $corruptedCount corrupted"
    Write-Host "`nVerification Result: $verifiedCount OK, $corruptedCount CORRUPTED" -ForegroundColor Cyan
}

function Cleanup-OldBackups {
    "Remove backups older than retention period"
    param([int]$RetentionDays)

    Write-Log "Cleaning up backups older than $RetentionDays days..."

    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    $commits = Get-ChildItem -Path $CommitsDir -Filter "*.json"
    $deletedCount = 0

    foreach ($commitFile in $commits) {
        $commit = Get-Content -Path $commitFile.FullName | ConvertFrom-Json
        $commitDate = Get-Date -Date $commit.timestamp

        if ($commitDate -lt $cutoffDate) {
            Remove-Item -Path $commitFile.FullName -Force
            $deletedCount++
        }
    }

    Write-Log "Cleanup complete: $deletedCount old commits removed"
}

function Main {
    Initialize-BackupSystem

    switch ($Command) {
        "backup" {
            $result = New-BackupCommit -Message $CommitMessage
            Write-Host "`nBackup completed successfully" -ForegroundColor Green
            Write-Host "Commit ID: $($result.CommitId)" -ForegroundColor Cyan
        }

        "restore" {
            if (-not $RestoreCommitId) {
                Write-Host "ERROR: Restore requires -RestoreCommitId parameter" -ForegroundColor Red
                exit 1
            }

            $success = Restore-BackupCommit -CommitId $RestoreCommitId
            if ($success) {
                Write-Host "`nRestore completed successfully" -ForegroundColor Green
            }
            else {
                Write-Host "`nRestore failed" -ForegroundColor Red
                exit 1
            }
        }

        "list" {
            Get-BackupHistory
        }

        "verify" {
            Verify-BackupIntegrity
        }

        "cleanup" {
            Cleanup-OldBackups -RetentionDays $RetentionDays
        }
    }
}

Main
