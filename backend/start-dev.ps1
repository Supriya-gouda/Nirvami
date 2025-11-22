# Start Backend Development Server (Without Background Workers)

Write-Host "Starting Nirvami Backend Server..." -ForegroundColor Green
Write-Host "Note: Background workers disabled (requires Redis)" -ForegroundColor Yellow
Write-Host ""

# Set environment
$env:PYTHONPATH = "$PWD"

# Start FastAPI server
Write-Host "Starting API server on http://localhost:8000" -ForegroundColor Cyan
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
