"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  XCircle, 
  CheckCircle, 
  AlertTriangle, 
  FileText, 
  Image as ImageIcon,
  Code,
  Tag,
  Calendar,
  Clock,
  Copy,
  ExternalLink,
  Brain,
  Loader2
} from "lucide-react";
import { RCAResults } from "./RCAResults";
import { api } from "@/lib/api-client";

interface TestDetailsDialogProps {
  test: any | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TestDetailsDialog({ test, open, onOpenChange }: TestDetailsDialogProps) {
  const [copied, setCopied] = useState(false);
  const [rcaAnalysis, setRcaAnalysis] = useState<any | null>(null);
  const [rcaLoading, setRcaLoading] = useState(false);
  const [rcaError, setRcaError] = useState<string | null>(null);
  const [showRCA, setShowRCA] = useState(false);

  // Reset RCA state when dialog closes or test changes
  useEffect(() => {
    if (!open) {
      setRcaAnalysis(null);
      setRcaError(null);
      setShowRCA(false);
    }
  }, [open]);

  if (!test) return null;

  const status = test.status || 'unknown';
  const statusDetails = test.statusDetails || {};
  const labels = test.labels || [];
  const parameters = test.parameters || [];
  const attachments = test.attachments || [];
  const steps = test.steps || [];

  const isFailed = status === 'failed' || status === 'broken';
  const StatusIcon = isFailed ? XCircle : status === 'passed' ? CheckCircle : AlertTriangle;
  const statusColor = isFailed ? 'text-red-500' : status === 'passed' ? 'text-green-500' : 'text-yellow-500';

  const formatDate = (timestamp: number) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  const formatDuration = (start: number, stop: number) => {
    if (!start || !stop) return 'N/A';
    const duration = stop - start;
    if (duration < 1000) return `${duration}ms`;
    return `${(duration / 1000).toFixed(2)}s`;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Analyze Root Cause
  const handleAnalyzeRCA = async () => {
    if (!test || !isFailed) return;

    setRcaLoading(true);
    setRcaError(null);
    setShowRCA(true);

    try {
      // Since we're working with JSON data without backend, we'll use a mock analysis
      // In production, uncomment the API call below
      
      // Option 1: Real API call (when backend is available)
      // const response = await api.performRCA(test.uuid);
      // setRcaAnalysis(response.data.result);

      // Option 2: Mock analysis for demo (current implementation)
      const mockAnalysis = generateMockRCA(test, statusDetails);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setRcaAnalysis(mockAnalysis);
    } catch (error: any) {
      console.error('RCA Analysis error:', error);
      setRcaError(error.response?.data?.detail || 'Failed to analyze root cause. Please try again.');
    } finally {
      setRcaLoading(false);
    }
  };

  // Generate mock RCA analysis based on test data
  const generateMockRCA = (testData: any, statusDetails: any): any => {
    const errorMessage = statusDetails.message || '';
    const stackTrace = statusDetails.trace || '';
    
    // Simple pattern matching to determine category and root cause
    let category = 'Code Bug';
    let rootCause = 'Unable to determine root cause from available information.';
    let confidence = 60;
    const recommendedActions: string[] = [];
    const similarPatterns: string[] = [];

    // Analyze error message patterns
    if (errorMessage.toLowerCase().includes('timeout') || errorMessage.toLowerCase().includes('connection')) {
      category = 'Infrastructure';
      rootCause = 'Connection timeout indicates an infrastructure issue. The test failed to establish or maintain a connection, likely due to network problems, server unavailability, or resource exhaustion.';
      confidence = 85;
      recommendedActions.push('Check network connectivity');
      recommendedActions.push('Verify server status and availability');
      recommendedActions.push('Review connection pool configuration');
      recommendedActions.push('Check firewall and security settings');
    } else if (errorMessage.toLowerCase().includes('404') || errorMessage.toLowerCase().includes('not found')) {
      category = 'Code Bug';
      rootCause = 'Resource not found (404) error suggests the endpoint or resource being tested does not exist or has been moved. This could indicate a routing issue, missing API endpoint, or incorrect URL configuration.';
      confidence = 90;
      recommendedActions.push('Verify the endpoint URL is correct');
      recommendedActions.push('Check API routing configuration');
      recommendedActions.push('Ensure the resource exists in the system');
      recommendedActions.push('Review recent code changes that might have affected routing');
    } else if (errorMessage.toLowerCase().includes('assertion') || errorMessage.toLowerCase().includes('expected')) {
      category = 'Code Bug';
      rootCause = 'Assertion failure indicates the actual result does not match the expected result. This typically points to a logic error in the code being tested, incorrect test data, or a change in expected behavior.';
      confidence = 80;
      recommendedActions.push('Review the assertion logic');
      recommendedActions.push('Verify test data is correct');
      recommendedActions.push('Check if recent code changes affected the expected behavior');
      recommendedActions.push('Compare with previous successful test runs');
    } else if (errorMessage.toLowerCase().includes('permission') || errorMessage.toLowerCase().includes('unauthorized')) {
      category = 'Configuration';
      rootCause = 'Permission or authorization error suggests a configuration issue with access controls, authentication, or authorization settings.';
      confidence = 85;
      recommendedActions.push('Verify user permissions and roles');
      recommendedActions.push('Check authentication configuration');
      recommendedActions.push('Review access control policies');
      recommendedActions.push('Ensure test credentials are valid');
    } else {
      category = 'Code Bug';
      rootCause = `The test failure appears to be caused by: ${errorMessage.substring(0, 200)}. Further investigation is needed to determine the exact root cause.`;
      confidence = 65;
      recommendedActions.push('Review the error message and stack trace');
      recommendedActions.push('Check recent code changes');
      recommendedActions.push('Verify test environment configuration');
      recommendedActions.push('Compare with similar test failures');
    }

    // Add stack trace analysis if available
    if (stackTrace) {
      if (stackTrace.includes('NullPointerException') || stackTrace.includes('undefined')) {
        rootCause += ' The stack trace indicates a null reference error, suggesting missing null checks or uninitialized variables.';
        recommendedActions.push('Add null checks in the code');
        recommendedActions.push('Verify all variables are properly initialized');
      }
    }

    return {
      root_cause: rootCause,
      confidence: confidence,
      category: category,
      similar_patterns: similarPatterns,
      recommended_actions: recommendedActions,
      technical_details: `Error Message: ${errorMessage}\n\nStack Trace:\n${stackTrace || 'No stack trace available'}`,
      analysis_model: 'mock-analysis-v1',
      tokens_used: 0
    };
  };

  // Extract attachments by type
  const screenshots = attachments.filter((a: any) => 
    a.type?.includes('image') || a.name?.toLowerCase().includes('screenshot') || a.source?.includes('.png') || a.source?.includes('.jpg')
  );
  const logs = attachments.filter((a: any) => 
    a.type?.includes('text') || a.name?.toLowerCase().includes('log') || a.source?.includes('.txt') || a.source?.includes('.log')
  );
  const otherAttachments = attachments.filter((a: any) => 
    !screenshots.includes(a) && !logs.includes(a)
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-qualify-dark-lighter border-gray-700">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <StatusIcon className={`h-6 w-6 ${statusColor}`} />
            <div className="flex-1">
              <DialogTitle className="text-white text-left">{test.name || 'Unknown Test'}</DialogTitle>
              <DialogDescription className="text-gray-400 text-left mt-1">
                {test.fullName || test.name || 'No full name available'}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Status & Basic Info */}
          <Card className="border-gray-700 bg-qualify-dark">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-gray-400">Test Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Status:</span>
                  <span className={`ml-2 font-medium ${statusColor}`}>
                    {status.toUpperCase()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Duration:</span>
                  <span className="ml-2 text-white">
                    {formatDuration(test.time?.start || test.start || 0, test.time?.stop || test.stop || 0)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Run Date:</span>
                  <span className="ml-2 text-white">
                    {test.runDate || test.runStartedAt 
                      ? formatDate(new Date(test.runDate || test.runStartedAt).getTime())
                      : formatDate(test.time?.start || test.start || 0)}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Run Started:</span>
                  <span className="ml-2 text-white">
                    {test.runStartedAt 
                      ? formatDate(new Date(test.runStartedAt).getTime())
                      : formatDate(test.time?.start || test.start || 0)}
                  </span>
                </div>
                {test.runFinishedAt && (
                  <div>
                    <span className="text-gray-500">Run Finished:</span>
                    <span className="ml-2 text-white">
                      {formatDate(new Date(test.runFinishedAt).getTime())}
                    </span>
                  </div>
                )}
                <div>
                  <span className="text-gray-500">UUID (Allure - từ JSON file):</span>
                  <span className="ml-2 text-white font-mono text-xs break-all">
                    {(() => {
                      // Always prefer allureUuid (from JSON file)
                      // Backend returns allureUuid from database (may be empty if not set)
                      if (test.allureUuid && test.allureUuid !== '') {
                        return test.allureUuid;
                      }
                      // If allureUuid is empty/missing, show warning
                      // This means database doesn't have Allure UUID (needs migration/backfill)
                      return (
                        <span className="text-yellow-500">
                          {test.uuid ? `⚠️ Not available (DB UUID: ${test.uuid.substring(0, 8)}...)` : 'N/A'}
                        </span>
                      );
                    })()}
                  </span>
                  {(!test.allureUuid || test.allureUuid === '') && (
                    <div className="mt-1 text-xs text-yellow-500">
                      💡 Database chưa có Allure UUID. Cần chạy migration và re-import data.
                    </div>
                  )}
                </div>
                {/* Only show Database UUID if it's different from Allure UUID */}
                {test.uuid && test.allureUuid && test.uuid !== test.allureUuid && (
                  <div>
                    <span className="text-gray-500">Database UUID:</span>
                    <span className="ml-2 text-white font-mono text-xs text-gray-500 break-all">
                      {test.uuid}
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Root Cause Analysis Section */}
          {isFailed && (
            <Card className="border-gray-700 bg-qualify-dark">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                    <Brain className="h-4 w-4 text-qualify-teal" />
                    AI Root Cause Analysis
                  </CardTitle>
                  {!showRCA && (
                    <Button
                      variant="default"
                      size="sm"
                      onClick={handleAnalyzeRCA}
                      disabled={rcaLoading}
                      className="bg-qualify-teal hover:bg-qualify-teal/90 text-white h-8 text-xs"
                    >
                      {rcaLoading ? (
                        <>
                          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Brain className="h-3 w-3 mr-1" />
                          Analyze Root Cause
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </CardHeader>
              {showRCA && (
                <CardContent>
                  <RCAResults 
                    analysis={rcaAnalysis || {}}
                    loading={rcaLoading}
                    error={rcaError}
                  />
                </CardContent>
              )}
            </Card>
          )}

          {/* Error Message & Trace */}
          {isFailed && statusDetails.message && (
            <Card className="border-gray-700 bg-qualify-dark">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    Error Message
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(statusDetails.message || '')}
                    className="h-7 text-xs"
                  >
                    <Copy className="h-3 w-3 mr-1" />
                    {copied ? 'Copied!' : 'Copy'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="text-sm text-red-300 bg-gray-900 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap font-mono">
                  {statusDetails.message}
                </pre>
              </CardContent>
            </Card>
          )}

          {/* Stack Trace */}
          {isFailed && statusDetails.trace && (
            <Card className="border-gray-700 bg-qualify-dark">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                    <Code className="h-4 w-4 text-orange-500" />
                    Stack Trace
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(statusDetails.trace || '')}
                    className="h-7 text-xs"
                  >
                    <Copy className="h-3 w-3 mr-1" />
                    {copied ? 'Copied!' : 'Copy'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="text-xs text-gray-300 bg-gray-900 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap font-mono max-h-96 overflow-y-auto">
                  {statusDetails.trace}
                </pre>
              </CardContent>
            </Card>
          )}

          {/* Labels/Metadata */}
          {labels.length > 0 && (
            <Card className="border-gray-700 bg-qualify-dark">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                  <Tag className="h-4 w-4 text-blue-500" />
                  Labels & Metadata
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {labels.map((label: any, idx: number) => (
                    <div
                      key={idx}
                      className="px-3 py-1 rounded-md bg-gray-800 border border-gray-700"
                    >
                      <span className="text-xs text-gray-400">{label.name}:</span>
                      <span className="text-xs text-white ml-1">{label.value}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Parameters */}
          {parameters.length > 0 && (
            <Card className="border-gray-700 bg-qualify-dark">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-purple-500" />
                  Test Parameters
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {parameters.map((param: any, idx: number) => (
                    <div key={idx} className="flex gap-4 text-sm">
                      <span className="text-gray-500 w-32">{param.name || 'Parameter'}:</span>
                      <span className="text-white font-mono">{String(param.value || 'N/A')}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Screenshots */}
          {screenshots.length > 0 && (
            <Card className="border-gray-700 bg-qualify-dark">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                  <ImageIcon className="h-4 w-4 text-green-500" />
                  Screenshots ({screenshots.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {screenshots.map((attachment: any, idx: number) => (
                    <div key={idx} className="border border-gray-700 rounded-lg overflow-hidden">
                      <div className="p-2 bg-gray-800 text-xs text-gray-400">
                        {attachment.name || `Screenshot ${idx + 1}`}
                      </div>
                      {attachment.source && (
                        <div className="bg-gray-900 p-2">
                          <img
                            src={`/attachments/${attachment.source}`}
                            alt={attachment.name || 'Screenshot'}
                            className="w-full h-auto rounded"
                            onError={(e) => {
                              // Fallback if image not found
                              (e.target as HTMLImageElement).style.display = 'none';
                            }}
                          />
                          <div className="mt-2 text-xs text-gray-500">
                            Source: {attachment.source}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Logs */}
          {logs.length > 0 && (
            <Card className="border-gray-700 bg-qualify-dark">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-yellow-500" />
                  Logs ({logs.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {logs.map((attachment: any, idx: number) => (
                    <div key={idx} className="border border-gray-700 rounded-lg p-3 bg-gray-900">
                      <div className="text-xs text-gray-400 mb-2">
                        {attachment.name || `Log ${idx + 1}`}
                      </div>
                      {attachment.source && (
                        <a
                          href={`/attachments/${attachment.source}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-qualify-teal hover:underline flex items-center gap-1"
                        >
                          <ExternalLink className="h-3 w-3" />
                          {attachment.source}
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Other Attachments */}
          {otherAttachments.length > 0 && (
            <Card className="border-gray-700 bg-qualify-dark">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-500" />
                  Other Attachments ({otherAttachments.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {otherAttachments.map((attachment: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between p-2 border border-gray-700 rounded-lg bg-gray-900">
                      <span className="text-sm text-white">{attachment.name || `Attachment ${idx + 1}`}</span>
                      {attachment.source && (
                        <a
                          href={`/attachments/${attachment.source}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-qualify-teal hover:underline flex items-center gap-1"
                        >
                          <ExternalLink className="h-3 w-3" />
                          View
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Test Steps (if available) */}
          {steps.length > 0 && (
            <Card className="border-gray-700 bg-qualify-dark">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-cyan-500" />
                  Test Steps ({steps.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {steps.slice(0, 10).map((step: any, idx: number) => (
                    <div key={idx} className="flex items-center gap-3 p-2 border border-gray-700 rounded-lg bg-gray-900">
                      {step.status === 'passed' ? (
                        <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                      ) : step.status === 'failed' ? (
                        <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                      ) : (
                        <AlertTriangle className="h-4 w-4 text-yellow-500 flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <div className="text-sm text-white">{step.name || `Step ${idx + 1}`}</div>
                        {step.statusDetails?.message && (
                          <div className="text-xs text-gray-400 mt-1">{step.statusDetails.message}</div>
                        )}
                      </div>
                    </div>
                  ))}
                  {steps.length > 10 && (
                    <div className="text-xs text-gray-500 text-center py-2">
                      ... and {steps.length - 10} more steps
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

