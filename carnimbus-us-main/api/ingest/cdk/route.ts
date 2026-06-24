import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    // Catch incoming DMS sync payload
    const dmsPayload = await request.json();

    // Verify origin via headers (ensure it's a validated dealer integration)
    const dealerId = request.headers.get('X-Dealer-ID');
    
    if (!dealerId) {
      return NextResponse.json({ error: 'Missing X-Dealer-ID header' }, { status: 401 });
    }

    // Dispatch async job to internal processing queue
    // Local agent handles image compression, VIN standardization, and DB updates
    fetch(`${process.env.BRAYLO_INTERNAL_INGESTION_URL}/process`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.BRAYLO_GATEWAY_SECRET}`
      },
      body: JSON.stringify({ dealerId, rawData: dmsPayload }),
    }).catch(err => console.error('Background agent ingestion failed:', err));

    // Instantly return 202 Accepted to the DMS provider to maintain API parity
    return NextResponse.json({ status: 'Processing initiated via CarNimbus Data Waterfall' }, { status: 202 });

  } catch (error) {
    console.error('Ingestion Webhook Error:', error);
    return NextResponse.json({ error: 'Ingestion payload malformed' }, { status: 400 });
  }
}
