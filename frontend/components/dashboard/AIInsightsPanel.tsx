"use client";

import { useState } from "react";
import { AlertTriangle, TrendingUp, Target, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FailedTestsList } from "./FailedTestsList";
import { TestOptimizationDialog } from "./TestOptimizationDialog";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface AIInsightsPanelProps {
  failedTests?: number;
  totalTests?: number;
  failedTestNames?: string[];
  failedTestsData?: any[]; // Full test objects for failed tests
}

export function AIInsightsPanel({ 
  failedTests = 0, 
  totalTests = 0, 
  failedTestNames = [],
  failedTestsData = []
}: AIInsightsPanelProps) {
  const [listDialogOpen, setListDialogOpen] = useState(false);
  const [optimizationDialogOpen, setOptimizationDialogOpen] = useState(false);

  const handleViewFailedTests = () => {
    console.log("View Failed Tests clicked", { failedTestsData: failedTestsData.length });
    if (failedTestsData && failedTestsData.length > 0) {
      setListDialogOpen(true);
    } else {
      console.warn("No failed tests data available");
    }
  };

  const handleViewOptimization = () => {
    if (totalTests > 0) {
      setOptimizationDialogOpen(true);
    }
  };

  // Generate dynamic insights from real data
  const insights = [];
  
  // Insight 1: Failed Tests Analysis
  if (failedTests > 0) {
    insights.push({
      icon: AlertTriangle,
      title: "Failed Tests Detected:",
      description: `${failedTests} tests failed out of ${totalTests} total`,
      action: "View Details",
      color: "text-red-500",
      onClick: handleViewFailedTests,
      enabled: failedTestsData && failedTestsData.length > 0,
    });
  } else {
    insights.push({
      icon: Target,
      title: "All Tests Passed:",
      description: `${totalTests} tests executed successfully`,
      action: "View Report",
      color: "text-green-500",
      onClick: () => {},
      enabled: false,
    });
  }
  
  // Insight 2: Test Coverage
  const passRate = totalTests > 0 ? Math.round(((totalTests - failedTests) / totalTests) * 100) : 0;
  insights.push({
    icon: TrendingUp,
    title: "Test Coverage:",
    description: `${passRate}% pass rate across all suites`,
    action: "View Trends",
    color: passRate >= 90 ? "text-green-500" : passRate >= 70 ? "text-yellow-500" : "text-red-500",
    onClick: () => {},
    enabled: false,
  });
  
  // Insight 3: Failed Test Names (if any)
  if (failedTestNames && failedTestNames.length > 0) {
    insights.push({
      icon: Target,
      title: "Root Cause Analysis:",
      description: `Analyzing failures: ${failedTestNames.slice(0, 2).join(', ')}`,
      action: "View Details",
      color: "text-orange-500",
      onClick: handleViewFailedTests,
      enabled: failedTestsData && failedTestsData.length > 0,
    });
  }
  
  // Insight 4: Test Optimization
  insights.push({
    icon: Zap,
    title: "Test Optimization:",
    description: `${totalTests} tests executed. Check for optimization opportunities`,
    action: "View Suggestions",
    color: "text-purple-500",
    onClick: handleViewOptimization,
    enabled: totalTests > 0,
  });
  
  return (
    <>
      <div className="grid grid-cols-2 gap-4">
        {insights.slice(0, 4).map((insight, index) => (
          <div
            key={index}
            className="flex items-start gap-4 rounded-lg border border-gray-700 bg-qualify-dark p-4"
          >
            <div className={`rounded-lg bg-gray-800 p-2 ${insight.color}`}>
              <insight.icon className="h-5 w-5" />
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-medium text-white">{insight.title}</h4>
              <p className="mt-1 text-xs text-gray-400">{insight.description}</p>
              <Button
                variant="link"
                size="sm"
                onClick={insight.onClick}
                disabled={!insight.enabled}
                className={`mt-2 h-auto p-0 text-xs ${
                  insight.enabled 
                    ? 'text-qualify-teal hover:text-qualify-teal/80 cursor-pointer' 
                    : 'text-gray-600 cursor-not-allowed'
                }`}
              >
                {insight.action} →
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Failed Tests List Dialog */}
      <Dialog open={listDialogOpen} onOpenChange={setListDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto bg-qualify-dark-lighter border-gray-700">
          <DialogHeader>
            <DialogTitle className="text-white">Failed Tests Details</DialogTitle>
          </DialogHeader>
          <FailedTestsList 
            failedTests={failedTestsData || []} 
            onClose={() => setListDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Test Optimization Dialog */}
      <TestOptimizationDialog
        open={optimizationDialogOpen}
        onOpenChange={setOptimizationDialogOpen}
        totalTests={totalTests}
      />
    </>
  );
}

