# =============================================================================
# ORFEAS AI 2Dâ†’3D Studio - Generate Self-Signed SSL Certificates
# =============================================================================
# THERION AI Project
#
# Generates self-signed SSL certificates for development/testing
# For production, use Let's Encrypt or proper CA-signed certificates
# =============================================================================

Write-Host "=" * 80
Write-Host "ORFEAS AI 2Dâ†’3D Studio - SSL Certificate Generation"
Write-Host "=" * 80
Write-Host ""

# Create SSL directory
$sslDir = "ssl"
if (-not (Test-Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir | Out-Null
    Write-Host "[OK] Created SSL directory: $sslDir"
}
else {
    Write-Host "[OK] SSL directory already exists: $sslDir"
}

# Check if certificates already exist
if ((Test-Path "$sslDir\cert.pem") -and (Test-Path "$sslDir\key.pem")) {
    Write-Host ""
    Write-Host "[WARNING] SSL certificates already exist!"
    $response = Read-Host "Do you want to regenerate them? (yes/no)"

    if ($response -ne "yes") {
        Write-Host "[SKIP] Using existing certificates"
        Write-Host ""
        Write-Host "=" * 80
        exit 0
    }
}

Write-Host ""
Write-Host "[INFO] Generating self-signed SSL certificate..."
Write-Host "[INFO] This certificate is for DEVELOPMENT/TESTING only!"
Write-Host ""

# Generate private key and certificate using OpenSSL
# Note: Requires OpenSSL to be installed
try {
    # Check if OpenSSL is available
    $opensslPath = Get-Command openssl -ErrorAction Stop
    Write-Host "[OK] OpenSSL found: $($opensslPath.Source)"

    # Generate certificate
    $command = "openssl req -x509 -newkey rsa:4096 -nodes -out $sslDir\cert.pem -keyout $sslDir\key.pem -days 365 -subj '/CN=localhost/O=ORFEAS AI/C=US'"

    Write-Host "[RUN] $command"
    Write-Host ""

    Invoke-Expression $command

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] SSL certificate generated successfully!"
        Write-Host ""
        Write-Host "Certificate Details:"
        Write-Host "  - Certificate: $sslDir\cert.pem"
        Write-Host "  - Private Key: $sslDir\key.pem"
        Write-Host "  - Valid for: 365 days"
        Write-Host "  - Common Name: localhost"
        Write-Host ""
        Write-Host "[WARNING] This is a SELF-SIGNED certificate!"
        Write-Host "[WARNING] Browsers will show security warnings."
        Write-Host "[WARNING] For production, use Let's Encrypt or proper CA-signed certs."
        Write-Host ""

        # Display certificate info
        Write-Host "Verifying certificate..."
        openssl x509 -in $sslDir\cert.pem -text -noout | Select-String "Subject:|Issuer:|Not Before|Not After"

    }
    else {
        Write-Host "[ERROR] Failed to generate SSL certificate (exit code: $LASTEXITCODE)"
        exit 1
    }

}
catch {
    Write-Host ""
    Write-Host "[ERROR] OpenSSL not found!"
    Write-Host ""
    Write-Host "Please install OpenSSL:"
    Write-Host "  - Windows: https://slproweb.com/products/Win32OpenSSL.html"
    Write-Host "  - Or use Git Bash (includes OpenSSL)"
    Write-Host "  - Or use Windows Subsystem for Linux (WSL)"
    Write-Host ""
    Write-Host "Alternative: Use Docker to generate certificates:"
    Write-Host '  docker run --rm -v ${PWD}/ssl:/ssl alpine/openssl req -x509 -newkey rsa:4096 -nodes -out /ssl/cert.pem -keyout /ssl/key.pem -days 365 -subj "/CN=localhost/O=ORFEAS AI/C=US"'
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "=" * 80
Write-Host "[OK] SSL setup complete!"
Write-Host "=" * 80
