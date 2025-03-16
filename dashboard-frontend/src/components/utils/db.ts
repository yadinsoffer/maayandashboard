import { sql } from '@vercel/postgres';
import { DashboardData, Metrics, DailyMetric } from '../../types/dashboard';

export async function getLatestMetrics(): Promise<DashboardData> {
    // Get the latest metrics
    const metricsResult = await sql`
        SELECT * FROM metrics 
        ORDER BY timestamp DESC 
        LIMIT 1
    `;

    // Get all available daily metrics, ordered by date
    const dailyMetricsResult = await sql`
        SELECT * FROM daily_metrics 
        ORDER BY date ASC
    `;

    const metrics = metricsResult.rows[0] || {};
    const dailyMetrics = dailyMetricsResult.rows || [];

    // Enhanced debug logging
    console.log('=== DATABASE DEBUG ===');
    console.log('Raw metrics query result:', metricsResult);
    console.log('Raw metrics from database:', metrics);
    console.log('All metrics fields:', Object.keys(metrics));
    console.log('Operational expenses from database:', metrics.operational_expenses);
    console.log('Operational expenses type:', typeof metrics.operational_expenses);
    
    // Create the response object
    const response = {
        metrics: {
            totalMarketingSpend: { 
                value: Number(metrics.total_marketing_spend) || 0, 
                label: 'Total Marketing Spend', 
                prefix: '$' 
            },
            influencerSpend: { 
                value: Number(metrics.influencer_spend) || 0, 
                label: 'Influencer Spend', 
                prefix: '$' 
            },
            paidAdsSpend: { 
                value: Number(metrics.paid_ads_spend) || 0, 
                label: 'Paid Ads Spend', 
                prefix: '$' 
            },
            netRevenue: { 
                value: Number(metrics.net_revenue) || 0, 
                label: 'Net Revenue', 
                prefix: '$' 
            },
            revenueSpentOnAds: { 
                value: Number(metrics.revenue_spent_on_ads) || 0, 
                label: 'Revenue Spent on Ads', 
                suffix: '%' 
            },
            customerLifetimeValue: { 
                value: Number(metrics.customer_lifetime_value) || 0, 
                label: 'Customer Lifetime Value', 
                prefix: '$' 
            },
            customerAcquisitionCost: { 
                value: Number(metrics.customer_acquisition_cost) || 0, 
                label: 'Customer Acquisition Cost', 
                prefix: '$' 
            },
            tickets: { 
                value: Number(metrics.tickets) || 0, 
                label: 'Tickets' 
            },
            revenue: { 
                value: Number(metrics.revenue) || 0, 
                label: 'Revenue', 
                prefix: '$' 
            },
            operationalExpenses: {
                value: Number(metrics.operational_expenses) || 0,
                label: 'Operational Expenses',
                prefix: '$'
            },
            yadinExpenses: {
                value: 40,
                label: 'Yadin Expenses',
                prefix: '$'
            }
        },
        charts: {
            barChart: dailyMetrics.map(dm => ({
                date: dm.date,
                value: dm.daily_guests
            })),
            lineChart: dailyMetrics.map(dm => ({
                date: dm.date,
                value: dm.gross_revenue
            }))
        }
    };
    
    // Log the final response
    console.log('=== RESPONSE DEBUG ===');
    console.log('Final response metrics:', response.metrics);
    console.log('Operational expenses in response:', response.metrics.operationalExpenses);
    
    return response;
}

export async function updateMetrics(metrics: Metrics): Promise<void> {
    await sql`
        INSERT INTO metrics (
            total_marketing_spend,
            influencer_spend,
            paid_ads_spend,
            net_revenue,
            revenue_spent_on_ads,
            customer_lifetime_value,
            customer_acquisition_cost,
            tickets,
            revenue,
            operational_expenses
        ) VALUES (
            ${metrics.totalMarketingSpend.value},
            ${metrics.influencerSpend.value},
            ${metrics.paidAdsSpend.value},
            ${metrics.netRevenue.value},
            ${metrics.revenueSpentOnAds.value},
            ${metrics.customerLifetimeValue.value},
            ${metrics.customerAcquisitionCost.value},
            ${metrics.tickets.value},
            ${metrics.revenue.value},
            ${metrics.operationalExpenses.value}
        )
    `;
}

export async function updateDailyMetrics(dailyMetric: DailyMetric): Promise<void> {
    await sql`
        INSERT INTO daily_metrics (
            date,
            gross_revenue,
            net_revenue,
            daily_guests,
            accumulated_guests
        ) VALUES (
            ${dailyMetric.date},
            ${dailyMetric.grossRevenue},
            ${dailyMetric.netRevenue},
            ${dailyMetric.dailyGuests},
            ${dailyMetric.accumulatedGuests}
        )
        ON CONFLICT (date) DO UPDATE SET
            gross_revenue = EXCLUDED.gross_revenue,
            net_revenue = EXCLUDED.net_revenue,
            daily_guests = EXCLUDED.daily_guests,
            accumulated_guests = EXCLUDED.accumulated_guests
    `;
} 