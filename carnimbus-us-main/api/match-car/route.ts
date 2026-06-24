import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

/**
 * Simple car‑matching endpoint.
 *
 * POST /api/match-car
 * Body: { "query": "Honda" }
 *
 * Returns the first car in matrix.json whose model contains the query string
 * (case‑insensitive). If no car matches, returns a 404 with a helpful message.
 */
export async function POST(request: Request) {
  try {
    const { query } = await request.json();
    if (!query || typeof query !== 'string') {
      return NextResponse.json({ error: 'Missing or invalid "query" field' }, { status: 400 });
    }

    const matrixPath = path.join(process.cwd(), 'matrix.json');
    const raw = await fs.readFile(matrixPath, 'utf-8');
    const matrix = JSON.parse(raw);

    // Simple substring match on the model field
    const match = matrix.find((car: any) =>
      typeof car.model === 'string' && car.model.toLowerCase().includes(query.toLowerCase())
    );

    if (!match) {
      return NextResponse.json({ error: 'No matching vehicle found' }, { status: 404 });
    }

    return NextResponse.json({ success: true, car: match });
  } catch (err: any) {
    console.error('match‑car error:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
