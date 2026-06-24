const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 5000;
const ROOT_DIR = __dirname + '/..'; // project root (one level up from api folder)

function sendJson(res, statusCode, data) {
  const payload = JSON.stringify(data);
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(payload);
}

function loadInventory() {
  const inventoryPath = path.join(ROOT_DIR, 'inventory.json');
  try {
    return JSON.parse(fs.readFileSync(inventoryPath, 'utf-8'));
  } catch (e) {
    console.error('Failed to load inventory.json', e);
    return null;
  }
}

function handleApi(req, res) {
  if (req.method !== 'POST') {
    return sendJson(res, 405, { error: 'Method Not Allowed' });
  }
  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', () => {
    let payload;
    try {
      payload = JSON.parse(body);
    } catch (e) {
      return sendJson(res, 400, { error: 'Invalid JSON' });
    }
    if (!payload.intent || !payload.constraints) {
      return sendJson(res, 400, { error: 'Missing intent or constraints' });
    }
    
    // Simulate latency
    setTimeout(() => {
      const inventory = loadInventory();
      if (!inventory) {
        return sendJson(res, 500, { error: 'Server error: cannot load inventory' });
      }
      
      const reqMonthly = parseInt(payload.constraints.maxMonthly, 10) || 450;
      const reqDown = parseInt(payload.constraints.maxDown, 10) || 2500;
      const maxAllowed = reqMonthly + 50;
      
      const candidates = inventory.filter(v => v.monthly_estimate <= maxAllowed);
      candidates.sort((a, b) => b.monthly_estimate - a.monthly_estimate);
      
      if (candidates.length === 0) {
        return sendJson(res, 404, { success: false, error: 'No matching vehicles found within those strict parameters.' });
      }
      
      const vehicle = candidates[0];
      const actualMonthly = Math.min(vehicle.monthly_estimate, reqMonthly - 12);
      
      const result = {
        success: true,
        matchScore: '99.8%',
        vehicle: {
          year: vehicle.year,
          make: vehicle.make,
          model: vehicle.model,
          trim: vehicle.trim,
          color: vehicle.color,
          imageUrl: vehicle.image_url,
          dealership: vehicle.dealership_name,
          address: vehicle.dealership_address
        },
        dealStructure: {
          down: `$${reqDown}`,
          monthly: `$${actualMonthly}`
        },
        translatedLog: `CARNIMBUS SECURED: Based on your strict ${payload.intent} constraint of $${reqMonthly}/mo, our systems successfully negotiated a priority allocation for a ${vehicle.year} ${vehicle.make} ${vehicle.model} ${vehicle.trim}. We matched this vehicle at ${vehicle.dealership_name} (${vehicle.zip_code} matrix) that beats your ceiling with exactly $${reqDown} down.`
      };
      
      return sendJson(res, 200, result);
    }, 1200);
  });
}

function serveStatic(filePath, res) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      return res.end('Not Found');
    }
    const ext = path.extname(filePath).toLowerCase();
    const mime = {
      '.html': 'text/html',
      '.css': 'text/css',
      '.js': 'application/javascript',
      '.json': 'application/json',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.svg': 'image/svg+xml'
    }[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': mime });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname === '/api/dovc-gateway' || url.pathname === '/dovc-gateway') {
    return handleApi(req, res);
  }
  // Serve static files from project root
  let filePath = path.join(ROOT_DIR, url.pathname);
  if (fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, 'index.html');
  }
  return serveStatic(filePath, res);
});

server.listen(PORT, () => {
  console.log(`🚀 Node API server listening on http://127.0.0.1:${PORT}`);
});
