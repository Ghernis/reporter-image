# Run the reporter image with local app/templates/static mounted.
# Edit code on your machine, run this script to get HTML + PDF in ./output (no rebuild).
# Prereq: build once with:  docker build -t reporter .

$out = Join-Path $PSScriptRoot "output"
if (-not (Test-Path $out)) { New-Item -ItemType Directory -Path $out | Out-Null }

docker run --rm `
  -v "${PSScriptRoot}\app:/app/app" `
  -v "${PSScriptRoot}\templates:/app/templates" `
  -v "${PSScriptRoot}\static:/app/static" `
  -v "${PSScriptRoot}\output:/output" `
  reporter `
  @args

Write-Host "Output in: $out"
