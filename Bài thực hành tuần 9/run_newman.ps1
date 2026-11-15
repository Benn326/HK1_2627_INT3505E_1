Write-Host "=== Step 1: Starting Books API Server ===" -ForegroundColor Cyan
$apiProcess = Start-Process -FilePath "python" -ArgumentList "-m", "app", "--port", "5000" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 2

try {
    Write-Host "=== Step 2: Running Newman Test Suite ===" -ForegroundColor Cyan
    newman run books-api.postman_collection.json `
        -e postman/local.postman_environment.json `
        -r cli,junit `
        --reporter-junit-export reports/junit.xml
} finally {
    Write-Host "=== Step 3: Stopping API Server ===" -ForegroundColor Cyan
    Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
}
Write-Host "Done! Report generated at reports/junit.xml" -ForegroundColor Green
