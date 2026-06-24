param(
    [int]$Port = 5000
)

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://*:$Port/")
$listener.Start()
Write-Host "⚡ PowerShell API listening on http://localhost:$Port"

function Load-Inventory {
    $path = Join-Path $PSScriptRoot 'inventory.json'
    if (Test-Path $path) {
        return Get-Content $path -Raw | ConvertFrom-Json
    }
    else {
        Write-Error "inventory.json not found"
        return @()
    }
}

while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response
    try {
        if ($request.HttpMethod -ne 'POST' -or $request.Url.AbsolutePath -ne '/dovc-gateway') {
            $response.StatusCode = 404
            $msg = '{"error":"Not found"}'
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($msg)
            $response.OutputStream.Write($bytes,0,$bytes.Length)
            continue
        }
        # Read body
        $reader = New-Object System.IO.StreamReader($request.InputStream)
        $payloadJson = $reader.ReadToEnd()
        $payload = $payloadJson | ConvertFrom-Json -ErrorAction Stop
        # Validate
        if (-not $payload.intent -or -not $payload.constraints) {
            $response.StatusCode = 400
            $msg = '{"error":"Missing DOV-C constraints"}'
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($msg)
            $response.OutputStream.Write($bytes,0,$bytes.Length)
            continue
        }
        # Simulate latency
        Start-Sleep -Milliseconds 1200
        $inventory = Load-Inventory
        $reqMonthly = [int]($payload.constraints.maxMonthly -as [int])
        if (-not $reqMonthly) { $reqMonthly = 450 }
        $reqDown = [int]($payload.constraints.maxDown -as [int])
        if (-not $reqDown) { $reqDown = 2500 }
        $maxAllowed = $reqMonthly + 50
        $candidates = $inventory | Where-Object { $_.monthly_estimate -le $maxAllowed } |
                      Sort-Object -Property monthly_estimate -Descending
        if (-not $candidates) {
            $response.StatusCode = 404
            $msg = '{"success":false,"error":"No matching vehicles found within those strict parameters."}'
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($msg)
            $response.OutputStream.Write($bytes,0,$bytes.Length)
            continue
        }
        $vehicle = $candidates[0]
        $actualMonthly = [math]::Min($vehicle.monthly_estimate, $reqMonthly - 12)
        $result = @{ 
            success = $true
            matchScore = '99.8%'
            vehicle = @{ 
                year = $vehicle.year
                make = $vehicle.make
                model = $vehicle.model
                trim = $vehicle.trim
                color = $vehicle.color
                imageUrl = $vehicle.image_url
                dealership = $vehicle.dealership_name
                address = $vehicle.dealership_address
            }
            dealStructure = @{ down = "`$$reqDown"; monthly = "`$$actualMonthly" }
            translatedLog = "CARNIMBUS SECURED: Based on your strict $($payload.intent) constraint of `$${reqMonthly}/mo, our systems successfully negotiated a priority allocation for a $($vehicle.year) $($vehicle.make) $($vehicle.model) $($vehicle.trim). We matched this vehicle at $($vehicle.dealership_name) ($($vehicle.zip_code) matrix) that beats your ceiling with exactly `$${reqDown} down."
        }
        $json = $result | ConvertTo-Json -Depth 5
        $response.StatusCode = 200
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        $response.OutputStream.Write($bytes,0,$bytes.Length)
    }
    catch {
        $response.StatusCode = 500
        $msg = '{"error":"Internal Server Error"}'
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($msg)
        $response.OutputStream.Write($bytes,0,$bytes.Length)
    }
    finally {
        $response.OutputStream.Close()
    }
}
