# PropertyPilot Windows Setup Script
# Installs Docker Desktop and prepares environment for AgentCore deployment

Write-Host "🏠 PropertyPilot Windows Setup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script requires Administrator privileges" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check if Docker is already installed
if (Test-Command "docker") {
    Write-Host "✅ Docker is already installed" -ForegroundColor Green
    docker --version
} else {
    Write-Host "📦 Installing Docker Desktop..." -ForegroundColor Yellow
    
    # Download Docker Desktop installer
    $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    $dockerInstaller = "$env:TEMP\DockerDesktopInstaller.exe"
    
    Write-Host "   Downloading Docker Desktop installer..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $dockerUrl -OutFile $dockerInstaller -UseBasicParsing
        Write-Host "   ✅ Download completed" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Failed to download Docker Desktop: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
    
    # Install Docker Desktop
    Write-Host "   Installing Docker Desktop (this may take several minutes)..." -ForegroundColor Yellow
    try {
        Start-Process -FilePath $dockerInstaller -ArgumentList "install", "--quiet" -Wait
        Write-Host "   ✅ Docker Desktop installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Failed to install Docker Desktop: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
    
    # Clean up installer
    Remove-Item $dockerInstaller -ErrorAction SilentlyContinue
}

# Check if AWS CLI is installed
if (Test-Command "aws") {
    Write-Host "✅ AWS CLI is already installed" -ForegroundColor Green
    aws --version
} else {
    Write-Host "📦 Installing AWS CLI..." -ForegroundColor Yellow
    
    # Download AWS CLI installer
    $awsUrl = "https://awscli.amazonaws.com/AWSCLIV2.msi"
    $awsInstaller = "$env:TEMP\AWSCLIV2.msi"
    
    Write-Host "   Downloading AWS CLI installer..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $awsUrl -OutFile $awsInstaller -UseBasicParsing
        Write-Host "   ✅ Download completed" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Failed to download AWS CLI: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
    
    # Install AWS CLI
    Write-Host "   Installing AWS CLI..." -ForegroundColor Yellow
    try {
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i", $awsInstaller, "/quiet" -Wait
        Write-Host "   ✅ AWS CLI installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Failed to install AWS CLI: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
    
    # Clean up installer
    Remove-Item $awsInstaller -ErrorAction SilentlyContinue
}

# Check Python and pip
if (Test-Command "python") {
    Write-Host "✅ Python is available" -ForegroundColor Green
    python --version
} else {
    Write-Host "❌ Python not found. Please install Python 3.11+ from https://python.org" -ForegroundColor Red
}

# Install Python dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Some Python dependencies may have failed to install" -ForegroundColor Yellow
}

# Check .env file
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️ .env file not found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env from template" -ForegroundColor Green
        Write-Host "📝 Please edit .env file and add your API keys" -ForegroundColor Yellow
    } else {
        Write-Host "❌ .env.example not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your computer to complete Docker installation" -ForegroundColor White
Write-Host "2. Launch Docker Desktop and complete the initial setup" -ForegroundColor White
Write-Host "3. Configure AWS credentials: aws configure" -ForegroundColor White
Write-Host "4. Edit .env file with your API keys" -ForegroundColor White
Write-Host "5. Run deployment: python build_and_deploy.py" -ForegroundColor White
Write-Host ""
Write-Host "📖 See AGENTCORE_DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Cyan