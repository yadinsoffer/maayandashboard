'use client';

import React from 'react';
import { MetricCardProps } from '@/types/dashboard';

const MetricCard: React.FC<MetricCardProps> = ({ data, className = '' }) => {
  const formattedValue = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(data.value);

  return (
    <div className={`bg-blue-600 p-4 rounded-lg text-white ${className}`}>
      <div className="text-3xl font-bold mb-2">
        {data.prefix && <span>{data.prefix}</span>}
        {formattedValue}
        {data.suffix && <span>{data.suffix}</span>}
      </div>
      <div className="text-sm text-blue-200">{data.label}</div>
    </div>
  );
};

export default MetricCard; 