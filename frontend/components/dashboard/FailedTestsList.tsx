"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { XCircle, ChevronRight, Calendar, Clock } from "lucide-react";
import { TestDetailsDialog } from "./TestDetailsDialog";

interface FailedTestsListProps {
  failedTests: any[];
  onClose?: () => void;
}

export function FailedTestsList({ failedTests, onClose }: FailedTestsListProps) {
  const [selectedTest, setSelectedTest] = useState<any | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  if (failedTests.length === 0) {
    return (
      <Card className="border-gray-700 bg-qualify-dark-lighter">
        <CardContent className="py-8 text-center text-gray-400">
          No failed tests to display
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className="border-gray-700 bg-qualify-dark-lighter">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2">
              <XCircle className="h-5 w-5 text-red-500" />
              Failed Tests ({failedTests.length})
            </CardTitle>
            {onClose && (
              <Button variant="ghost" size="sm" onClick={onClose} className="h-7 text-xs">
                Close
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {failedTests.map((test, index) => {
              const statusDetails = test.statusDetails || {};
              const errorMessage = statusDetails.message || 'No error message available';
              const truncatedMessage = errorMessage.length > 100 
                ? errorMessage.substring(0, 100) + '...' 
                : errorMessage;

              // Format run date/time
              const formatRunDateTime = (dateStr: string | null | undefined) => {
                if (!dateStr) return 'N/A';
                try {
                  const date = new Date(dateStr);
                  const dateStr_formatted = date.toLocaleDateString('en-GB', { 
                    day: '2-digit', 
                    month: '2-digit', 
                    year: 'numeric' 
                  });
                  const timeStr = date.toLocaleTimeString('en-GB', { 
                    hour: '2-digit', 
                    minute: '2-digit',
                    second: '2-digit'
                  });
                  return `${dateStr_formatted} ${timeStr}`;
                } catch {
                  return dateStr;
                }
              };

              const runDate = test.runDate || test.runStartedAt || test.createdAt;

              return (
                <div
                  key={test.uuid || index}
                  className="flex items-start gap-3 p-3 rounded-lg border border-gray-700 bg-qualify-dark hover:border-red-500/50 cursor-pointer transition-colors"
                  onClick={() => {
                    setSelectedTest(test);
                    setDialogOpen(true);
                  }}
                >
                  <XCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <div className="text-sm font-medium text-white flex-1">
                        {test.name || `Test ${index + 1}`}
                      </div>
                      {runDate && (
                        <div className="flex items-center gap-1 text-xs text-gray-500 flex-shrink-0">
                          <Calendar className="h-3 w-3" />
                          <span>{formatRunDateTime(runDate)}</span>
                        </div>
                      )}
                    </div>
                    <div className="text-xs text-gray-400 mb-2 line-clamp-2">
                      {test.fullName || test.name || 'No full name'}
                    </div>
                    <div className="text-xs text-red-300 font-mono line-clamp-2">
                      {truncatedMessage}
                    </div>
                    {test.labels && test.labels.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {test.labels.slice(0, 3).map((label: any, idx: number) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded text-xs bg-gray-800 text-gray-400 border border-gray-700"
                          >
                            {label.name}: {label.value}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <ChevronRight className="h-5 w-5 text-gray-500 flex-shrink-0" />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <TestDetailsDialog
        test={selectedTest}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />
    </>
  );
}

