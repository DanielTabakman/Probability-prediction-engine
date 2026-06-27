@echo off
REM Thin wrapper — canonical: scripts/setup_cloudflare_staging_dns_secret.ps1
powershell -ExecutionPolicy Bypass -File "%~dp0setup_cloudflare_staging_dns_secret.ps1" %*
