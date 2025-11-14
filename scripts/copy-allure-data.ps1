# Copy Allure data to today's folder
$sourceFolder = "D:\allure-reports\run-2025-11-11_13-45-40"
$today = Get-Date -Format "dd-MM-yyyy"
$targetFolder = "D:\allure-reports\$today"

Write-Host "Copying Allure files..."
Write-Host "From: $sourceFolder"
Write-Host "To: $targetFolder"

# Get result files
$files = Get-ChildItem -Path $sourceFolder -Filter "*-result.json" | Select-Object -First 30

Write-Host "Found $($files.Count) result files"

# Copy files
foreach ($file in $files) {
    Copy-Item -Path $file.FullName -Destination $targetFolder -Force
}

Write-Host "Copied $($files.Count) files successfully!"
Write-Host ""
Write-Host "Folder ready for Report Watcher: $targetFolder"

