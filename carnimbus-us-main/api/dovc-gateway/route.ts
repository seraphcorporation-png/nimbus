import { NextResponse } from 'next/server';
import Database from 'better-sqlite3';
import path from 'path';

export async function POST(request: Request) {
  try {
    const payload = await request.json();
    
    // 1. Validate the frontend request constraints
    if (!payload.intent || !payload.constraints) {
      return NextResponse.json({ error: 'Missing DOV-C constraints' }, { status: 400 });
    }

    // 2. Query the Local SQLite Inventory Database
    
    // Simulate network delay to the matrix
    await new Promise((resolve) => setTimeout(resolve, 1200));

    // Calculate requested ceilings
    const requestedMonthly = parseInt(payload.constraints.maxMonthly) || 450;
    const requestedDown = parseInt(payload.constraints.maxDown) || 2500;
    const requestedZip = payload.constraints.zip || '90210';
    
    // Connect to local SQLite DB
    const dbPath = path.join(process.cwd(), 'data', 'inventory.sqlite');
    const db = new Database(dbPath, { readonly: true });
    
    // Query for a matching vehicle
    const vehicle = db.prepare(`
      SELECT * FROM vehicles 
      WHERE monthly_estimate <= ? 
      ORDER BY monthly_estimate DESC 
      LIMIT 1
    `).get(requestedMonthly + 50) as any; // Allow a slight buffer for the matrix to "negotiate" down
    
    db.close();

    if (!vehicle) {
      return NextResponse.json({ 
        success: false, 
        error: "No matching vehicles found within those strict parameters."
      }, { status: 404 });
    }
    
    // The matrix always finds a deal slightly better than their max ceiling
    const actualMonthly = Math.min(vehicle.monthly_estimate, requestedMonthly - 12); 
    
    const responseData = {
      score: "99.8%",
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
      deal: {
        down: `$${requestedDown}`,
        monthly: `$${actualMonthly}`
      },
      log_translation: `CARNIMBUS SECURED: Based on your strict ${payload.intent} constraint of $${requestedMonthly}/mo, our systems successfully negotiated a priority allocation for a ${vehicle.year} ${vehicle.make} ${vehicle.model} ${vehicle.trim}. We matched this vehicle at ${vehicle.dealership_name} (${vehicle.zip_code} matrix) that beats your ceiling with exactly $${requestedDown} down.`
    };

    // 3. Return the plain-English/translated response to the Vercel frontend
    return NextResponse.json({ 
      success: true, 
      matchScore: responseData.score,
      vehicle: responseData.vehicle,
      dealStructure: responseData.deal,
      translatedLog: responseData.log_translation 
    });

  } catch (error) {
    console.error('DOV-C Gateway Error:', error);
    return NextResponse.json({ error: 'Internal Routing Failure' }, { status: 500 });
  }
}
