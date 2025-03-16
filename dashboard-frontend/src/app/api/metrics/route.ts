import { NextResponse } from 'next/server';
import { getLatestMetrics } from '@/lib/db';

export async function GET() {
    try {
        const metrics = await getLatestMetrics();
        
        // Debug logging to see what's in the metrics object
        console.log('=== API ROUTE DEBUG ===');
        console.log('Metrics object from getLatestMetrics:', metrics);
        console.log('Operational expenses in metrics:', metrics.metrics.operationalExpenses);
        
        // Ensure all required metrics are explicitly included in the response
        const response = {
            metrics: {
                ...metrics.metrics,
                operationalExpenses: metrics.metrics.operationalExpenses || {
                    value: 0,
                    label: 'Operational Expenses',
                    prefix: '$'
                },
                yadinExpenses: {
                    value: 40,
                    label: 'Yadin Expenses',
                    prefix: '$'
                }
            },
            charts: metrics.charts
        };
        
        console.log('Final API response:', response);
        
        return NextResponse.json(response);
    } catch (error) {
        console.error('Error fetching metrics:', error);
        return NextResponse.json(
            { error: 'Failed to fetch metrics' },
            { status: 500 }
        );
    }
} 