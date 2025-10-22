#!/usr/bin/env pwsh
# Minimal training scaffold runner for Windows

param(
    [int]$Epochs = 5,
    [float]$Lr = 0.1,
    [int]$BatchSize = 16,
    [int]$Seed = 42,
    [string]$Dataset = "",
    [string]$Checkpoint = "./ml/checkpoints/minimal.json"
)

Write-Host "[ML] Starting minimal training..." -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Please install from https://www.python.org/" -ForegroundColor Red
    exit 1
}

$env:PYTHONUNBUFFERED = "1"

# Call the Python entrypoint with standard flags
$argsList = @(
    "./ml/run_training_entry.py",
    "--epochs=$Epochs",
    "--lr=$Lr",
    "--batch-size=$BatchSize",
    "--seed=$Seed",
    "--dataset=$Dataset",
    "--checkpoint=$Checkpoint"
)
& python @argsList

Write-Host "[ML] Training finished." -ForegroundColor Green
