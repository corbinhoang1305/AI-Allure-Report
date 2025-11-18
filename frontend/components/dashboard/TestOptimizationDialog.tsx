"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Zap, Clock, TrendingUp, AlertCircle, CheckCircle } from "lucide-react";

interface TestOptimizationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  totalTests?: number;
}

export function TestOptimizationDialog({ 
  open, 
  onOpenChange,
  totalTests = 0 
}: TestOptimizationDialogProps) {
  // Mock optimization suggestions - in real app, this would come from backend/AI
  const suggestions = [
    {
      type: "performance",
      title: "Optimize Slow Tests",
      description: "Consider parallelizing tests that take longer than 5 seconds",
      impact: "High",
      icon: Clock,
      color: "text-yellow-500",
      details: [
        "10 tests exceed 5 second execution time",
        "Parallel execution could reduce total runtime by ~40%",
        "Consider using test sharding for CI/CD pipelines"
      ]
    },
    {
      type: "coverage",
      title: "Increase Test Coverage",
      description: "Add tests for critical user flows that lack coverage",
      impact: "Medium",
      icon: TrendingUp,
      color: "text-blue-500",
      details: [
        "3 critical user flows have < 50% test coverage",
        "Focus on authentication and payment flows",
        "Aim for 80%+ coverage on critical paths"
      ]
    },
    {
      type: "maintenance",
      title: "Remove Duplicate Tests",
      description: "Identify and consolidate duplicate test cases",
      impact: "Low",
      icon: AlertCircle,
      color: "text-orange-500",
      details: [
        "5 test cases appear to be duplicates",
        "Consolidating could reduce maintenance overhead",
        "Review test names and logic for similarities"
      ]
    },
    {
      type: "flakiness",
      title: "Stabilize Flaky Tests",
      description: "Address tests with inconsistent results",
      impact: "High",
      icon: CheckCircle,
      color: "text-green-500",
      details: [
        "4 flaky tests detected in recent runs",
        "Review timing dependencies and async operations",
        "Add proper waits and retries where needed"
      ]
    }
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-qualify-dark-lighter border-gray-700">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <Zap className="h-6 w-6 text-purple-500" />
            <DialogTitle className="text-white">Test Optimization Suggestions</DialogTitle>
          </div>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          <div className="rounded-lg bg-qualify-dark p-4 border border-gray-700">
            <p className="text-sm text-gray-400">
              Based on analysis of <span className="text-white font-semibold">{totalTests}</span> test executions, 
              here are optimization opportunities to improve test efficiency and reliability.
            </p>
          </div>

          {suggestions.map((suggestion, index) => {
            const Icon = suggestion.icon;
            return (
              <Card key={index} className="border-gray-700 bg-qualify-dark">
                <CardHeader className="pb-3">
                  <div className="flex items-start gap-3">
                    <div className={`rounded-lg bg-gray-800 p-2 ${suggestion.color}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-white text-sm">{suggestion.title}</CardTitle>
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          suggestion.impact === "High" 
                            ? "bg-red-500/20 text-red-400"
                            : suggestion.impact === "Medium"
                            ? "bg-yellow-500/20 text-yellow-400"
                            : "bg-gray-500/20 text-gray-400"
                        }`}>
                          {suggestion.impact} Impact
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 mt-1">{suggestion.description}</p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {suggestion.details.map((detail, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-start gap-2">
                        <span className="text-qualify-teal mt-1">•</span>
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            );
          })}

          <div className="flex justify-end gap-2 pt-4">
            <Button 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              className="border-gray-700 text-gray-400 hover:bg-gray-800"
            >
              Close
            </Button>
            <Button 
              variant="teal"
              onClick={() => {
                // In real app, this would trigger optimization actions
                console.log("Apply optimizations");
              }}
            >
              <Zap className="mr-2 h-4 w-4" />
              Apply Optimizations
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}




