const handler = require('./api/dovc-gateway.js').default;

// Mock request and response objects
function mockReq(body) {
  return {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body)
  };
}

function mockRes() {
  const res = {};
  res.statusCode = 200;
  res._status = 200;
  res._json = null;
  res.status = (code) => { res._status = code; return res; };
  res.json = (obj) => { res._json = obj; console.log('Response:', JSON.stringify(obj, null, 2)); };
  return res;
}

(async () => {
  const req = mockReq({ intent: 'Honda', constraints: {} });
  const res = mockRes();
  await handler(req, res);
})();
