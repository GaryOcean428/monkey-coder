import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Check if the app is running properly
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'monkey-coder-web',
      version: process.env.npm_package_version || '0.1.0',
      environment: process.env.NODE_ENV || 'development',
    };

    return NextResponse.json(health, { status: 200 });
  } catch {
    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        service: 'monkey-coder-web',
        error: 'Health check failed',
      },
      { status: 500 }
    );
  }
}