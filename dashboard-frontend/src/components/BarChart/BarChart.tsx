'use client';

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { format } from 'date-fns';
import type { ChartProps } from '@/types/dashboard';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const options = {
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
      },
    },
  },
  maintainAspectRatio: false,
};

const BarChart: React.FC<ChartProps> = ({ data, className = '' }) => {
  const chartData = {
    labels: data.map(item => format(new Date(item.date), 'dd MMM')),
    datasets: [
      {
        data: data.map(item => item.value),
        backgroundColor: 'rgba(53, 162, 235, 0.8)',
        borderWidth: 0,
        borderRadius: 4,
      },
    ],
  };

  return (
    <div className={`h-[300px] ${className}`}>
      <Bar options={options} data={chartData} />
    </div>
  );
};

export default BarChart; 