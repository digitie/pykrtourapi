$envFile = Join-Path (Get-Location) ".env.local"

if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*KTO_SERVICE_KEY\s*=\s*(.+?)\s*$') {
      $env:KTO_SERVICE_KEY = $Matches[1].Trim('"').Trim("'")
    }
  }
}

if (-not $env:KTO_SERVICE_KEY) {
  throw "KTO_SERVICE_KEY is not set. Create .env.local with KTO_SERVICE_KEY=..."
}

python -m pytest -m live tests/test_live.py @args
