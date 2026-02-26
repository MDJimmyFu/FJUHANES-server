$ErrorActionPreference = "Stop"

# Use existing generic credentials found in previous context
$Username = "A03772"
$Password = "Qwer12345"

$LoginUrl = "http://10.10.246.80/Ipo/HISLogin"
# Potential Home URL after login?
$BaseUrl = "http://10.10.246.80/Ipo/"

Write-Host "Attempting to log in to $LoginUrl as $Username..."

# 1. Initialize Session
$Session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
try {
    $r1 = Invoke-WebRequest -Uri $LoginUrl -SessionVariable Session -UseBasicParsing
}
catch {
    Write-Error "Failed to reach login page: $_"
    exit
}

# 2. Construct Payload
# Based on HTML field names: SignOnID, SignOnPassword
$Body = @{
    "SignOnID"                   = $Username
    "SignOnPassword"             = $Password
    "loginType"                  = ""
    # "LoginButton" is the button, usually not sent in POST unless it has a name/value
    # Hidden fields might be required matching the HTML
    "SystemUserIDHidden"         = "Login"
    "SystemSystemIDHidden"       = "HIS"
    "SystemControllerNameHidden" = "HisLogin"
    "SystemProgramNoHidden"      = "HISLOGIN"
}

# 3. Post Login
try {
    # Note: Sometimes login forms POST to a specific action like /Login?Length=... 
    # But usually posting to the page itself works for ASP.NET WebForms/MVC if logic is there.
    # If the JS `hislogin.login` does something complex, this simple POST might fail.
    
    $r2 = Invoke-WebRequest -Uri $LoginUrl -Method Post -Body $Body -WebSession $Session -UseBasicParsing
    
    Write-Host "Login POST returned status: $($r2.StatusCode)"
    Write-Host "Current URL: $($r2.BaseResponse.ResponseUri.AbsoluteUri)"
    
    # Check if we are still on login page
    if ($r2.Content -match "SignOnID") {
        Write-Warning "It seems we are still on the login page. Login might have failed or JS is required."
        # Dump content to see if there is an error message
        $r2.Content | Out-File "login_response.html"
        Write-Host "Saved response to login_response.html"
    }
    else {
        Write-Host "Login seems successful! (Or at least we moved pages)"
        
        # 4. Try to find links
        $links = $r2.Links | Where-Object { $_.href -like "*Surgery*" -or $_.href -like "*Operation*" -or $_.href -like "*List*" }
        if ($links) {
            Write-Host "Found potential surgery links:"
            $links | Format-Table href, innerText
        }
        else {
            Write-Host "No obvious 'Surgery' links found on landing page."
            Write-Host "Listing all links..."
            $r2.Links | Select-Object -First 20 | Format-Table href, innerText
        }
    }

}
catch {
    Write-Error "Login POST failed: $_"
}
