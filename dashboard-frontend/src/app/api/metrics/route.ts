import { NextResponse } from 'next/server';
import { getLatestMetrics } from '@/lib/db';

export async function GET() {
    try {
        const metrics = await getLatestMetrics();
        return NextResponse.json(metrics);
    } catch (error) {
        console.error('Error fetching metrics:', error);
        return NextResponse.json(
            { error: 'Failed to fetch metrics' },
            { status: 500 }
        );
    }
} 