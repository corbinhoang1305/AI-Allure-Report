"use client";

import { CheckCircle, XCircle, Clock } from "lucide-react";
import { formatDate } from "@/lib/utils";

interface TestRun {
  suite: string;
  date: string;
  passed: number;
  failed: number;
  status: string;
}

interface RecentTestRunsProps {
  runs?: TestRun[];
}

export function RecentTestRuns({ runs = [] }: RecentTestRunsProps) {
  if (runs.length === 0) {
    return (
      <div className="flex items-center justify-center py-8 text-gray-500">
        <p className="text-sm">No recent test runs available</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-3">
      {runs.map((run, index) => {
        const isPass = run.failed === 0;
        const Icon = isPass ? CheckCircle : XCircle;
        const statusColor = isPass ? "text-qualify-teal" : "text-red-500";
        const statusText = isPass ? "Passed" : `${run.failed} Failed`;
        
        return (
          <div
            key={index}
            className="flex items-center gap-3 rounded-lg border border-gray-700 bg-qualify-dark px-4 py-3"
          >
            <Icon className={`h-4 w-4 ${statusColor}`} />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-white">{run.suite}</span>
              </div>
              <span className="text-xs text-gray-500">{run.date}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{run.passed + run.failed} tests</span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColor}`}>
                {statusText}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

