"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Brain, 
  TrendingUp, 
  AlertCircle, 
  CheckCircle2, 
  Lightbulb,
  Copy,
  ExternalLink,
  Loader2
} from "lucide-react";
import { useState } from "react";

interface RCAResultsProps {
  analysis: {
    root_cause: string;
    confidence: number;
    category: string;
    similar_patterns?: string[];
    recommended_actions?: string[];
    technical_details?: string;
    analysis_model?: string;
    tokens_used?: number;
  };
  loading?: boolean;
  error?: string | null;
}

export function RCAResults({ analysis, loading, error }: RCAResultsProps) {
  const [copied, setCopied] = useState(false);

  if (loading) {
    return (
      <Card className="border-gray-700 bg-qualify-dark">
        <CardContent className="py-8 text-center">
          <Loader2 className="h-8 w-8 animate-spin text-qualify-teal mx-auto mb-4" />
          <p className="text-gray-400">Analyzing root cause...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-500/50 bg-qualify-dark">
        <CardContent className="py-8 text-center">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p className="text-red-300">{error}</p>
        </CardContent>
      </Card>
    );
  }

  const confidenceColor = analysis.confidence >= 80 
    ? 'text-green-500' 
    : analysis.confidence >= 60 
    ? 'text-yellow-500' 
    : 'text-red-500';

  const categoryColors: Record<string, string> = {
    'Code Bug': 'bg-red-500/20 text-red-400 border-red-500/50',
    'Infrastructure': 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    'Test Flakiness': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    'Configuration': 'bg-blue-500/20 text-blue-400 border-blue-500/50',
    'Data Issue': 'bg-purple-500/20 text-purple-400 border-purple-500/50',
  };

  const categoryColor = categoryColors[analysis.category] || 'bg-gray-500/20 text-gray-400 border-gray-500/50';

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4">
      {/* Header with Confidence */}
      <Card className="border-gray-700 bg-qualify-dark">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2">
              <Brain className="h-5 w-5 text-qualify-teal" />
              Root Cause Analysis
            </CardTitle>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">Confidence:</span>
              <span className={`text-sm font-bold ${confidenceColor}`}>
                {analysis.confidence}%
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs text-gray-400">Category:</span>
            <span className={`px-2 py-1 rounded text-xs font-medium border ${categoryColor}`}>
              {analysis.category}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Root Cause */}
      <Card className="border-gray-700 bg-qualify-dark">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              Root Cause
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(analysis.root_cause)}
              className="h-7 text-xs"
            >
              <Copy className="h-3 w-3 mr-1" />
              {copied ? 'Copied!' : 'Copy'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-white leading-relaxed">
            {analysis.root_cause}
          </p>
        </CardContent>
      </Card>

      {/* Recommended Actions */}
      {analysis.recommended_actions && analysis.recommended_actions.length > 0 && (
        <Card className="border-gray-700 bg-qualify-dark">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-yellow-500" />
              Recommended Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {analysis.recommended_actions.map((action, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-white">
                  <CheckCircle2 className="h-4 w-4 text-qualify-teal mt-0.5 flex-shrink-0" />
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Similar Patterns */}
      {analysis.similar_patterns && analysis.similar_patterns.length > 0 && (
        <Card className="border-gray-700 bg-qualify-dark">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-blue-500" />
              Similar Patterns
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {analysis.similar_patterns.map((pattern, index) => (
                <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                  <span className="text-qualify-teal mt-1">•</span>
                  <span>{pattern}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Technical Details */}
      {analysis.technical_details && (
        <Card className="border-gray-700 bg-qualify-dark">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm text-gray-400 flex items-center gap-2">
                <Brain className="h-4 w-4 text-purple-500" />
                Technical Details
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => copyToClipboard(analysis.technical_details || '')}
                className="h-7 text-xs"
              >
                <Copy className="h-3 w-3 mr-1" />
                {copied ? 'Copied!' : 'Copy'}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <pre className="text-xs text-gray-300 bg-gray-900 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap font-mono">
              {analysis.technical_details}
            </pre>
          </CardContent>
        </Card>
      )}

      {/* Metadata */}
      {(analysis.analysis_model || analysis.tokens_used) && (
        <div className="text-xs text-gray-500 text-right">
          {analysis.analysis_model && (
            <span>Model: {analysis.analysis_model}</span>
          )}
          {analysis.tokens_used && (
            <span className="ml-3">Tokens: {analysis.tokens_used}</span>
          )}
        </div>
      )}
    </div>
  );
}

