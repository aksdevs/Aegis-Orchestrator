#!/usr/bin/env pwsh
# Simple and fast Docker build script for Aegis Orchestrator

Write-Host "🚀 Building Aegis Orchestrator Docker image..." -ForegroundColor Green

# Enable BuildKit for faster builds
$env:DOCKER_BUILDKIT = 1

# Record start time
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
    Write-Host "📦 Building optimized production image..." -ForegroundColor Yellow
    
    # Build with caching and optimization
    docker build `
        --platform linux/amd64 `
        --tag aegis-orchestrator:latest `
        --cache-from type=local,src=.docker-cache `
        --cache-to type=local,dest=.docker-cache,mode=max `
        .
    
    if ($LASTEXITCODE -eq 0) {
        $stopwatch.Stop()
        $elapsed = $stopwatch.Elapsed.TotalSeconds
        Write-Host "✅ Build completed successfully in $([math]::Round($elapsed, 2)) seconds!" -ForegroundColor Green
        
        # Show image info
        docker images aegis-orchestrator:latest --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
        
        Write-Host "`n🎯 Ready for deployment!" -ForegroundColor Magenta
        Write-Host "   Run: docker run -p 8080:8080 aegis-orchestrator:latest" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "💥 Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}