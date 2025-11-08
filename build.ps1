#!/usr/bin/env pwsh
# Fast Docker build script for Aegis Orchestrator
# Uses BuildKit for improved performance and caching

param(
    [string]$Tag = "aegis-orchestrator:latest",
    [switch]$NoCache = $false,
    [switch]$Push = $false,
    [string]$Registry = ""
)

Write-Host "🚀 Building Aegis Orchestrator Docker image..." -ForegroundColor Green

# Enable BuildKit for faster builds
$env:DOCKER_BUILDKIT = 1

# Build arguments
$buildArgs = @(
    "build"
    "--platform", "linux/amd64"
    "--tag", $Tag
)

# Add cache options for faster rebuilds
if (-not $NoCache) {
    $buildArgs += @(
        "--cache-from", "type=local,src=.docker-cache"
        "--cache-to", "type=local,dest=.docker-cache,mode=max"
    )
} else {
    $buildArgs += "--no-cache"
}

# Add current directory as build context
$buildArgs += "."

try {
    Write-Host "📦 Building image: $Tag" -ForegroundColor Yellow
    Write-Host "💡 Using BuildKit for optimized builds" -ForegroundColor Cyan
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Execute Docker build
    & docker @buildArgs
    
    if ($LASTEXITCODE -eq 0) {
        $stopwatch.Stop()
        $elapsed = $stopwatch.Elapsed.TotalSeconds
        Write-Host "✅ Build completed successfully in $([math]::Round($elapsed, 2)) seconds" -ForegroundColor Green
        
        # Show image size
        $imageInfo = docker images $Tag --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
        Write-Host "📊 Image info:" -ForegroundColor Cyan
        Write-Host $imageInfo -ForegroundColor White
        
        # Optional push to registry
        if ($Push -and $Registry) {
            Write-Host "🚀 Pushing to registry: $Registry" -ForegroundColor Yellow
            $pushTag = "$Registry/$Tag"
            docker tag $Tag $pushTag
            docker push $pushTag
            Write-Host "✅ Push completed" -ForegroundColor Green
        }
        
    } else {
        Write-Host "❌ Build failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    
} catch {
    Write-Host "💥 Build error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Show build summary
Write-Host "`n📋 Build Summary:" -ForegroundColor Magenta
Write-Host "   Image: $Tag" -ForegroundColor White
Write-Host "   Build time: $([math]::Round($stopwatch.Elapsed.TotalSeconds, 2))s" -ForegroundColor White
Write-Host "   BuildKit: Enabled" -ForegroundColor White
Write-Host "   Cache: $(if ($NoCache) { 'Disabled' } else { 'Enabled' })" -ForegroundColor White