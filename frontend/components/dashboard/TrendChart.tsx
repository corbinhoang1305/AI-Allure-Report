"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface TrendChartProps {
  data: Array<{
    date: string;
    passed: number;
    failed: number;
  }>;
}

export function TrendChart({ data }: TrendChartProps) {
  // Filter out null data points for cleaner visualization
  const filteredData = data.map(item => ({
    ...item,
    passed: item.passed ?? 0,
    failed: item.failed ?? 0,
  }));
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={filteredData}>
        <defs>
          <linearGradient id="colorPassed" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#00D9B5" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#00D9B5" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorFailed" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#FF6B6B" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#FF6B6B" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#2A2A2A" />
        <XAxis 
          dataKey="date" 
          stroke="#666"
          style={{ fontSize: '11px' }}
          interval="preserveStartEnd"
          tick={{ fill: '#888' }}
          tickFormatter={(value) => {
            // Format date from YYYY-MM-DD to DD/MM
            if (value && typeof value === 'string') {
              const date = new Date(value);
              if (!isNaN(date.getTime())) {
                return `${date.getDate()}/${date.getMonth() + 1}`;
              }
            }
            return value;
          }}
        />
        <YAxis 
          stroke="#666"
          style={{ fontSize: '11px' }}
          tick={{ fill: '#888' }}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: '#1E1E1E',
            border: '1px solid #2A2A2A',
            borderRadius: '8px',
            color: '#fff'
          }}
          formatter={(value: any, name: string) => {
            const displayName = name === 'passed' ? 'Passed (Thành công)' : 'Failed (Thất bại)';
            return [value, displayName];
          }}
          labelFormatter={(label) => `Ngày: ${label}`}
        />
        <Legend 
          wrapperStyle={{
            paddingTop: '20px'
          }}
          formatter={(value) => {
            return value === 'passed' ? 'Tests Passed' : 'Tests Failed';
          }}
        />
        <Area
          type="monotone"
          dataKey="passed"
          stroke="#00D9B5"
          strokeWidth={3}
          fillOpacity={1}
          fill="url(#colorPassed)"
          name="passed"
          connectNulls={false}
          dot={{ fill: '#00D9B5', r: 4 }}
          activeDot={{ r: 6 }}
        />
        <Area
          type="monotone"
          dataKey="failed"
          stroke="#FF6B6B"
          strokeWidth={3}
          fillOpacity={1}
          fill="url(#colorFailed)"
          name="failed"
          connectNulls={false}
          dot={{ fill: '#FF6B6B', r: 4 }}
          activeDot={{ r: 6 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

