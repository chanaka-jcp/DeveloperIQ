Write-Host "Running tests..."

try {
    Invoke-WebRequest -Uri http://20.121.169.239:802/ -UseBasicParsing -TimeoutSec 30
    Write-Host "Tests passed."
}
catch {
    Write-Host "Tests failed: $_"
    exit 1
}
