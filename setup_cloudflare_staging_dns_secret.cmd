@echo off
REM One-time: store CLOUDFLARE_API_TOKEN in GitHub Actions for staging DNS.
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\setup_cloudflare_staging_dns_secret.ps1" %*
