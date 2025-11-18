"use client";

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useState } from 'react';

interface TrendChartProps {
  data: Array<{
    date: string;
    passed: number;
    failed: number;
    flaky?: number;
    total?: number;
    pass_rate?: number;
  }>;
}

// Custom Tooltip Component
const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || !payload.length) return null;

  const total = payload.reduce((sum: number, entry: any) => sum + (entry.value || 0), 0);
  const passRate = total > 0 
    ? ((payload.find((p: any) => p.dataKey === 'passed')?.value || 0) / total * 100).toFixed(1)
    : '0.0';

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border border-gray-700 rounded-xl shadow-2xl p-4 backdrop-blur-sm">
      <div className="mb-3 pb-2 border-b border-gray-700">
        <p className="text-sm font-semibold text-gray-300">📅 {formatDate(label)}</p>
        <p className="text-xs text-gray-500 mt-1">
          Total: <span className="text-white font-medium">{total}</span> tests
          {' • '}
          Pass Rate: <span className="text-emerald-400 font-medium">{passRate}%</span>
        </p>
      </div>
      <div className="space-y-2">
        {payload.map((entry: any, index: number) => {
          const percentage = total > 0 ? ((entry.value / total) * 100).toFixed(1) : '0.0';
          const icons: Record<string, string> = {
            passed: '✅',
            flaky: '⚠️',
            failed: '❌'
          };
          return (
            <div key={index} className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <span>{icons[entry.dataKey]}</span>
                <span className="text-sm" style={{ color: entry.color }}>
                  {entry.name}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white">{entry.value}</span>
                <span className="text-xs text-gray-500">({percentage}%)</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Format date helper
const formatDate = (dateStr: string) => {
  if (!dateStr) return dateStr;
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;
  
  const day = date.getDate();
  const month = date.getMonth() + 1;
  const year = date.getFullYear();
  
  const dayName = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()];
  
  return `${dayName}, ${day}/${month}/${year}`;
};

export function TrendChart({ data }: TrendChartProps) {
  const [hiddenSeries, setHiddenSeries] = useState<Set<string>>(new Set());

  // Filter out null data points and prepare data
  const filteredData = data.map(item => ({
    ...item,
    passed: item.passed ?? 0,
    failed: item.failed ?? 0,
    flaky: item.flaky ?? 0,
    total: (item.passed ?? 0) + (item.failed ?? 0) + (item.flaky ?? 0),
  }));

  const handleLegendClick = (dataKey: string) => {
    setHiddenSeries(prev => {
      const newSet = new Set(prev);
      
      // Toggle: Nếu đang hidden thì show, nếu đang show thì hide
      if (newSet.has(dataKey)) {
        newSet.delete(dataKey); // Show lại
      } else {
        newSet.add(dataKey); // Hide đi
      }
      
      return newSet;
    });
  };

  // Custom Legend Component - Always show all 3 buttons regardless of payload
  const CustomLegend = ({ payload }: any) => {
    // Define all series statically so buttons never disappear
    const allSeries = [
      { dataKey: 'passed', name: 'Passed', color: '#10b981' },
      { dataKey: 'flaky', name: 'Flaky', color: '#f59e0b' },
      { dataKey: 'failed', name: 'Failed', color: '#ef4444' }
    ];
    
          const icons: Record<string, string> = {
            passed: '✅',
            flaky: '⚠️',
            failed: '❌'
          };
    
          const descriptions: Record<string, string> = {
            passed: 'Stable tests - passed on first run',
            flaky: 'Unstable tests - failed then passed',
            failed: 'Failed tests - needs attention'
          };
    
    return (
      <div className="flex flex-wrap justify-center gap-6 mt-6">
        {allSeries.map((series, index) => {
          const isHidden = hiddenSeries.has(series.dataKey);
          const tooltipText = descriptions[series.dataKey] + 
            (isHidden ? ' (Click to show)' : ' (Click to hide)');
          
          return (
            <button
              key={series.dataKey}
              onClick={() => handleLegendClick(series.dataKey)}
              className={`group flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300 cursor-pointer ${
                isHidden 
                  ? 'bg-gray-700/40 hover:bg-gray-700/60 border-2 border-gray-600' 
                  : 'bg-gray-800/50 hover:bg-gray-800/70 shadow-lg hover:scale-105 border-2 border-transparent'
              }`}
              title={tooltipText}
              style={{ 
                opacity: isHidden ? 0.6 : 1
              }}
            >
              <span className={`text-lg transition-all ${isHidden ? 'grayscale' : ''}`}>
                {icons[series.dataKey]}
              </span>
              <div className="flex flex-col items-start">
                <span 
                  className={`text-sm font-semibold transition-all ${
                    isHidden ? 'line-through' : ''
                  }`}
                  style={{ color: isHidden ? '#999' : series.color }}
                >
                  {series.name}
                </span>
                <span className="text-xs text-gray-500 hidden group-hover:block">
                  {descriptions[series.dataKey]}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    );
  };
  
  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={filteredData}>
          <defs>
            {/* Enhanced gradients with glow effect */}
            <linearGradient id="colorPassed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity={0.4}/>
              <stop offset="50%" stopColor="#10b981" stopOpacity={0.2}/>
              <stop offset="100%" stopColor="#10b981" stopOpacity={0.05}/>
            </linearGradient>
            <linearGradient id="colorFlaky" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.4}/>
              <stop offset="50%" stopColor="#f59e0b" stopOpacity={0.2}/>
              <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.05}/>
            </linearGradient>
            <linearGradient id="colorFailed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ef4444" stopOpacity={0.4}/>
              <stop offset="50%" stopColor="#ef4444" stopOpacity={0.2}/>
              <stop offset="100%" stopColor="#ef4444" stopOpacity={0.05}/>
            </linearGradient>
            
            {/* Glow filters */}
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#374151" 
            strokeOpacity={0.3}
            vertical={false}
          />
          
          <XAxis 
            dataKey="date" 
            stroke="#6b7280"
            style={{ fontSize: '12px', fontWeight: 500 }}
            tickLine={false}
            axisLine={{ stroke: '#374151' }}
            tick={{ fill: '#9ca3af' }}
            tickFormatter={(value) => {
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
            stroke="#6b7280"
            style={{ fontSize: '12px', fontWeight: 500 }}
            tickLine={false}
            axisLine={{ stroke: '#374151' }}
            tick={{ fill: '#9ca3af' }}
            label={{ 
              value: 'Tests Count', 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: '#9ca3af', fontSize: '12px' }
            }}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Legend content={<CustomLegend />} />
          
          {/* Passed Area */}
          {!hiddenSeries.has('passed') && (
            <Area
              type="monotone"
              dataKey="passed"
              stroke="#10b981"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorPassed)"
              name="Passed"
              animationDuration={1000}
              animationEasing="ease-in-out"
              dot={{ 
                fill: '#10b981', 
                strokeWidth: 2, 
                stroke: '#fff',
                r: 5,
                filter: 'url(#glow)'
              }}
              activeDot={{ 
                r: 7, 
                fill: '#10b981',
                stroke: '#fff',
                strokeWidth: 3,
                filter: 'url(#glow)'
              }}
            />
          )}
          
          {/* Flaky Area */}
          {!hiddenSeries.has('flaky') && (
            <Area
              type="monotone"
              dataKey="flaky"
              stroke="#f59e0b"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorFlaky)"
              name="Flaky"
              animationDuration={1000}
              animationEasing="ease-in-out"
              dot={{ 
                fill: '#f59e0b', 
                strokeWidth: 2, 
                stroke: '#fff',
                r: 5,
                filter: 'url(#glow)'
              }}
              activeDot={{ 
                r: 7, 
                fill: '#f59e0b',
                stroke: '#fff',
                strokeWidth: 3,
                filter: 'url(#glow)'
              }}
            />
          )}
          
          {/* Failed Area */}
          {!hiddenSeries.has('failed') && (
            <Area
              type="monotone"
              dataKey="failed"
              stroke="#ef4444"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorFailed)"
              name="Failed"
              animationDuration={1000}
              animationEasing="ease-in-out"
              dot={{ 
                fill: '#ef4444', 
                strokeWidth: 2, 
                stroke: '#fff',
                r: 5,
                filter: 'url(#glow)'
              }}
              activeDot={{ 
                r: 7, 
                fill: '#ef4444',
                stroke: '#fff',
                strokeWidth: 3,
                filter: 'url(#glow)'
              }}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

