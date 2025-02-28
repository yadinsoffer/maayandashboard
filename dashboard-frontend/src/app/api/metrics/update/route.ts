import { NextResponse } from 'next/server';
import { updateMetrics, updateDailyMetrics } from '@/lib/db';
import { headers } from 'next/headers';

const API_KEY = process.env.API_KEY;

export async function POST(request: Request) {
    try {
        // Verify API key
        const headersList = await headers();
        const authHeader = headersList.get('authorization') || '';
        
        if (!authHeader || !API_KEY || authHeader !== `Bearer ${API_KEY}`) {
            return NextResponse.json(
                { error: 'Unauthorized' },
                { status: 401 }
            );
        }

        const updates = await request.json();
        
        // Handle metrics updates
        if (updates.metrics) {
            await updateMetrics(updates.metrics);
        }
        
        // Handle daily metrics updates
        if (updates.dailyMetrics) {
            for (const dailyMetric of updates.dailyMetrics) {
                await updateDailyMetrics(dailyMetric);
            }
        }

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('Error processing update:', error);
        return NextResponse.json(
            { error: 'Failed to process update' },
            { status: 500 }
        );
    }
} 