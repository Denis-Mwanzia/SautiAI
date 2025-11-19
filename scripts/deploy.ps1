# Sauti AI Deployment Script for Windows PowerShell
# This script builds and deploys the application using Docker Compose

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info {
    Write-Host "[INFO] $args" -ForegroundColor Green
}

function Write-Warn {
    Write-Host "[WARN] $args" -ForegroundColor Yellow
}

function Write-Error {
    Write-Host "[ERROR] $args" -ForegroundColor Red
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Error ".env file not found!"
    Write-Info "Please create a .env file based on backend/.env.example and frontend/.env.example"
    exit 1
}

# Load environment variables
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Check required environment variables
$requiredVars = @("SUPABASE_URL", "SUPABASE_KEY", "DATABASE_URL", "VITE_SUPABASE_URL", "VITE_SUPABASE_ANON_KEY")
$missingVars = @()

foreach ($var in $requiredVars) {
    if (-not [Environment]::GetEnvironmentVariable($var, "Process")) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Error "Missing required environment variables:"
    foreach ($var in $missingVars) {
        Write-Host "  - $var"
    }
    exit 1
}

Write-Info "Starting deployment..."

# Stop existing containers
Write-Info "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build images
Write-Info "Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
Write-Info "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
Write-Info "Waiting for services to be healthy..."
Start-Sleep -Seconds 10

# Check health
Write-Info "Checking service health..."
try {
    $backendHealth = (Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue).StatusCode
    if ($backendHealth -eq 200) {
        Write-Info "Backend is healthy ✓"
    }
} catch {
    Write-Warn "Backend health check failed"
}

try {
    $frontendHealth = (Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -ErrorAction SilentlyContinue).StatusCode
    if ($frontendHealth -eq 200) {
        Write-Info "Frontend is healthy ✓"
    }
} catch {
    Write-Warn "Frontend health check failed"
}

# Show logs
Write-Info "Showing service logs (Ctrl+C to exit)..."
docker-compose -f docker-compose.prod.yml logs -f

