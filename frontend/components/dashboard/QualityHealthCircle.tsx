"use client";

interface QualityHealthCircleProps {
  passRate: number;
}

export function QualityHealthCircle({ passRate }: QualityHealthCircleProps) {
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (passRate / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center">
      <svg width="200" height="200" className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          stroke="#2A2A2A"
          strokeWidth="16"
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx="100"
          cy="100"
          r={radius}
          stroke="#00D9B5"
          strokeWidth="16"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      
      <div className="absolute flex flex-col items-center">
        <div className="text-5xl font-bold text-white">{passRate}%</div>
        <div className="text-xs font-medium text-qualify-teal">Pass Rate</div>
      </div>
    </div>
  );
}

