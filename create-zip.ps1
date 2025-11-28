# PowerShell script to create project zip excluding unnecessary files
# Usage: .\create-zip.ps1

$projectName = "Matrimony_HR_AI"
$zipFileName = "$projectName.zip"

# Folders and patterns to exclude
$excludePatterns = @(
    "node_modules",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".hypothesis",
    ".git",
    ".vscode",
    ".kiro",
    "dist",
    "build",
    ".env"
)

# File extensions to exclude
$excludeExtensions = @(
    "*.db",
    "*.pyc",
    "*.pyo",
    "*.log"
)

Write-Host "Creating zip file: $zipFileName" -ForegroundColor Green
Write-Host "Excluding patterns: $($excludePatterns -join ', ')" -ForegroundColor Yellow

# Get all files recursively, excluding specified patterns
$files = Get-ChildItem -Path . -Recurse -File | Where-Object {
    $file = $_
    $shouldInclude = $true
    
    # Check if file path contains any excluded pattern
    foreach ($pattern in $excludePatterns) {
        if ($file.FullName -like "*\$pattern\*" -or $file.FullName -like "*/$pattern/*") {
            $shouldInclude = $false
            break
        }
    }
    
    # Check if file matches excluded extensions
    if ($shouldInclude) {
        foreach ($ext in $excludeExtensions) {
            if ($file.Name -like $ext) {
                $shouldInclude = $false
                break
            }
        }
    }
    
    $shouldInclude
}

Write-Host "Found $($files.Count) files to include" -ForegroundColor Cyan

# Remove existing zip if it exists
if (Test-Path $zipFileName) {
    Remove-Item $zipFileName -Force
    Write-Host "Removed existing zip file" -ForegroundColor Yellow
}

# Create zip file
$files | Compress-Archive -DestinationPath $zipFileName -CompressionLevel Optimal

Write-Host "`nZip file created successfully: $zipFileName" -ForegroundColor Green
Write-Host "Size: $([math]::Round((Get-Item $zipFileName).Length / 1MB, 2)) MB" -ForegroundColor Cyan
