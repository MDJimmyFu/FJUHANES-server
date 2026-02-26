$url = "http://auth.fjcuh.org.tw/UOF/cds/ws/SSOWS.asmx/VerifyUser"
$body = @{
    cry1 = "A03772"
    cry2 = "Qwer12345"
}

try {
    $response = Invoke-WebRequest -Uri $url -Method Post -Body $body -ErrorAction Stop
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Content: $($response.Content)"
    
    if ($response.Content -match "true") {
        Write-Host "Login SUCCESS!" -ForegroundColor Green
    } else {
        Write-Host "Login FAILED (Unexpected content)" -ForegroundColor Red
    }
} catch {
    Write-Host "Login FAILED: $_" -ForegroundColor Red
}
