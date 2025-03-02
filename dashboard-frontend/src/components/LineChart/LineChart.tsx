'use client';

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { format } from 'date-fns';
import type { ChartProps } from '@/types/dashboard';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const options: ChartOptions<'line'> = {
  responsive: true,
  plugins: {
    legend: {
      display: false,
    },
    title: {
      display: false,
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        color: 'var(--foreground)',
      },
    },
    y: {
      grid: {
        color: 'rgba(0, 0, 0, 0.1)',
      },
      ticks: {
        color: 'var(--foreground)',
        callback: function(value) {
          return `$${value.toLocaleString()}`;
        },
      },
    },
  },
  maintainAspectRatio: false,
};

const LineChart: React.FC<ChartProps> = ({ data, className = '' }) => {
  const chartData = {
    labels: data.map(item => format(new Date(item.date), 'dd MMM')),
    datasets: [
      {
        data: data.map(item => item.value),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        tension: 0.3,
      },
    ],
  };

  return (
    <div className={`h-[300px] ${className}`}>
      <Line options={options} data={chartData} />
    </div>
  );
};

export default LineChart; 