"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Activity, TrendingUp, AlertCircle, CheckCircle, FileText, Zap } from "lucide-react";
import { QualityHealthCircle } from "@/components/dashboard/QualityHealthCircle";
import { TrendChart } from "@/components/dashboard/TrendChart";
import { ProjectGrid } from "@/components/dashboard/ProjectGrid";
import { AIInsightsPanel } from "@/components/dashboard/AIInsightsPanel";
import { RecentTestRuns } from "@/components/dashboard/RecentTestRuns";
import { Sidebar } from "@/components/layout/Sidebar";
import { api } from "@/lib/api-client";

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load data from backend API
    async function loadData() {
      try {
        setError(null);
        
        // Try to load from backend API first
        const dashboardResponse = await api.getDashboard();
        
        if (dashboardResponse.data) {
          // Backend returned dashboard data
          const backendData = dashboardResponse.data;
          
          // Transform backend trends data to match frontend format
          const transformedTrends = (backendData.recent_trends || []).map((trend: any) => ({
            date: trend.date,
            passed: trend.passed || 0,
            failed: trend.failed || 0,
          }));
          
          // Transform failed_tests_data to ensure allureUuid is properly set
          const transformedFailedTests = (backendData.failed_tests_data || []).map((test: any) => ({
            ...test,
            // Backend should return allureUuid (Allure UUID from JSON file)
            // If backend has allureUuid, use it (even if empty string means not set)
            // DO NOT use uuid as fallback for allureUuid - uuid is Database UUID!
            allureUuid: test.allureUuid || '',
            // Keep uuid as database UUID (separate from Allure UUID)
            uuid: test.uuid || ''
          }));

          // Transform backend data to match frontend format
          setDashboardData({
            overall_health: backendData.overall_health || {
              pass_rate: 0,
              total_tests: 0,
              passed: 0,
              failed: 0,
              avg_duration_ms: 0,
            },
            recent_trends: transformedTrends,
            projects: backendData.projects || [],
            flaky_tests: backendData.flaky_tests || [],
            failed_test_names: backendData.failed_test_names || [],
            failed_tests_data: transformedFailedTests,
            recent_runs: backendData.recent_runs || [],
          });
          
          setLoading(false);
          return;
        }
        
        // Fallback: Load from local files if backend doesn't have data yet
        const response = await fetch('/real-data/all-results.json');
        
        if (!response.ok) {
          throw new Error('Failed to load data');
        }
        
        const results = await response.json();
        
        // Aggregate data
        const total = results.length;
        const passed = results.filter((r: any) => r.status === 'passed').length;
        const failed = results.filter((r: any) => r.status === 'failed' || r.status === 'broken').length;
        const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
        
        // Group by suite
        const suites: Record<string, { total: number; passed: number }> = {};
        results.forEach((r: any) => {
          const suiteLabel = r.labels?.find((l: any) => l.name === 'suite');
          const suiteName = suiteLabel?.value || 'Unknown Suite';
          
          if (!suites[suiteName]) {
            suites[suiteName] = { total: 0, passed: 0 };
          }
          suites[suiteName].total++;
          if (r.status === 'passed') {
            suites[suiteName].passed++;
          }
        });
        
        // Convert to projects
        const projects = Object.entries(suites).map(([name, stats]) => ({
          name: name.split('\\').pop() || name,
          pass_rate: Math.round((stats.passed / stats.total) * 100),
          trend: stats.passed > stats.total / 2 ? 'up' : 'down',
        }));
        
        // Load REAL trend data from file
        let trends = [];
        try {
          const trendResponse = await fetch('/real-data/trend-data.json');
          if (trendResponse.ok) {
            const trendData = await trendResponse.json();
            
            // Create full 30-day range
            const today = new Date();
            const trendMap = new Map(trendData.map((t: any) => [t.date, t]));
            
            for (let i = 29; i >= 0; i--) {
              const date = new Date(today);
              date.setDate(date.getDate() - i);
              const dateStr = `${date.getDate()}/${date.getMonth() + 1}`;
              
              // Check if we have data for this date
              const dayData = trendMap.get(dateStr) as { passed: number; failed: number } | undefined;
              
              if (dayData) {
                // Có data thật
                trends.push({
                  date: dateStr,
                  passed: dayData.passed,
                  failed: dayData.failed,
                });
              } else {
                // Không có data - để 0
                trends.push({
                  date: dateStr,
                  passed: 0,
                  failed: 0,
                });
              }
            }
            
            console.log(`✅ Loaded REAL trend data: ${trendData.length} days with data`);
          } else {
            throw new Error('Trend file not found');
          }
        } catch (error) {
          console.error('⚠️ Could not load trend data:', error);
          // Fallback to empty trend
          trends = [];
        }
        
        // Extract failed test data (full objects) for AI insights
        const failedTestsData = results
          .filter((r: any) => r.status === 'failed' || r.status === 'broken')
          .slice(0, 10) // Keep up to 10 failed tests for details view
          .map((r: any) => ({
            ...r,
            // UUID from JSON file IS the Allure UUID - map it correctly
            allureUuid: r.uuid || r.allureUuid || '',
            // For local files, uuid is the Allure UUID (not database UUID)
            // So we set both to the same value
            uuid: r.uuid || ''
          }));
        
        const failedTestNames = failedTestsData
          .map((r: any) => r.name)
          .slice(0, 5);
        
        // Create recent runs from trend data
        const recentRuns = (await (async () => {
          try {
            const trendResponse = await fetch('/real-data/trend-data.json');
            if (trendResponse.ok) {
              const trendData = await trendResponse.json();
              return trendData.map((day: any) => ({
                suite: `Test Run ${day.date}`,
                date: day.date,
                passed: day.passed,
                failed: day.failed,
                status: day.failed === 0 ? 'passed' : 'failed'
              }));
            }
          } catch (e) {
            return [];
          }
          return [];
        })());
        
        setDashboardData({
          overall_health: {
            pass_rate: passRate,
            total_tests: total,
            passed,
            failed,
            avg_duration_ms: 45000,
          },
          recent_trends: trends,
          projects,
          flaky_tests: [],
          failed_test_names: failedTestNames,
          failed_tests_data: failedTestsData, // Full test objects
          recent_runs: recentRuns.slice(0, 5),
        });
        
        setLoading(false);
        
      } catch (error: any) {
        console.error('Error loading data:', error);
        setError(error.message || 'Failed to load dashboard data');
        setLoading(false);
        
        // Try to load from local files as last resort
        try {
          const fallbackResponse = await fetch('/real-data/all-results.json');
          if (fallbackResponse.ok) {
            const results = await fallbackResponse.json();
            // ... (keep existing fallback logic)
            const total = results.length;
            const passed = results.filter((r: any) => r.status === 'passed').length;
            const failed = results.filter((r: any) => r.status === 'failed' || r.status === 'broken').length;
            const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
            
            setDashboardData({
              overall_health: {
                pass_rate: passRate,
                total_tests: total,
                passed,
                failed,
                avg_duration_ms: 45000,
              },
              recent_trends: [],
              projects: [],
              flaky_tests: [],
              failed_test_names: [],
              failed_tests_data: [],
              recent_runs: [],
            });
            setLoading(false);
          }
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError);
        }
      }
    }
    
    loadData();
    
    // Auto-refresh every 1 minute to check for new data
    const interval = setInterval(() => {
      console.log('🔄 Auto-refreshing dashboard data...');
      loadData();
    }, 60 * 1000);  // Check every 1 minute
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-qualify-dark">
        <div className="text-qualify-teal text-xl">Loading...</div>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="flex h-screen items-center justify-center bg-qualify-dark">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-2">Error: {error}</div>
          <div className="text-gray-400 text-sm">Make sure backend services are running</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-qualify-dark">
      <Sidebar />
      
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <header className="flex items-center justify-between border-b border-gray-800 bg-qualify-dark-lighter px-8 py-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Activity className="h-6 w-6 text-qualify-teal" />
              <h1 className="text-xl font-bold text-white">QUALIFY.AI: Intelligent Test Observability</h1>
            </div>
          </div>
          <Button variant="teal" size="sm">
            Sonnet
          </Button>
        </header>

        {/* Main Content */}
        <main className="p-8">
          <div className="grid grid-cols-12 gap-6">
            {/* Overall Quality Health */}
            <div className="col-span-4">
              <Card className="border-gray-800 bg-qualify-dark-lighter">
                <CardHeader>
                  <CardTitle className="text-white">Overall Quality Health</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col items-center">
                  <QualityHealthCircle passRate={dashboardData.overall_health.pass_rate} />
                  
                  <div className="mt-6 grid w-full grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-xs text-gray-400">Defect Leakage</div>
                      <div className="text-sm font-semibold text-white">3%</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-400">Avg. 3%</div>
                      <div className="text-sm font-semibold text-white">-</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-400">Test Run Time</div>
                      <div className="text-sm font-semibold text-white">Avg. 18s</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* AI-Powered Insights */}
            <div className="col-span-8">
              <Card className="border-gray-800 bg-qualify-dark-lighter">
                <CardHeader>
                  <CardTitle className="text-white">AI-Powered Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <AIInsightsPanel 
                    failedTests={dashboardData.overall_health.failed}
                    totalTests={dashboardData.overall_health.total_tests}
                    failedTestNames={dashboardData.failed_test_names || []}
                    failedTestsData={dashboardData.failed_tests_data || []}
                  />
                </CardContent>
              </Card>
            </div>

            {/* Historical Trend */}
            <div className="col-span-8">
              <Card className="border-gray-800 bg-qualify-dark-lighter">
                <CardHeader>
                  <CardTitle className="text-white">Historical Trend: Pass Rate & Bugs</CardTitle>
                </CardHeader>
                <CardContent>
                  <TrendChart data={dashboardData.recent_trends} />
                </CardContent>
              </Card>
            </div>

            {/* Natural Language Query */}
            <div className="col-span-4">
              <Card className="border-gray-800 bg-qualify-dark-lighter h-full">
                <CardHeader>
                  <CardTitle className="text-sm text-gray-400">Natural Language Query (AI-Chat)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col gap-4">
                    <input
                      type="text"
                      placeholder="Ask Qualify AI..."
                      className="w-full rounded-lg border border-gray-700 bg-qualify-dark px-4 py-3 text-sm text-white placeholder-gray-500 focus:border-qualify-teal focus:outline-none"
                    />
                    
                    <div className="rounded-lg bg-qualify-dark p-4">
                      <p className="text-xs text-gray-400 mb-2">
                        Showing 5 failed tests related 'Gocoin' in the last 7 days:
                      </p>
                    </div>

                    <Button variant="outline" size="sm" className="w-full border-qualify-teal text-qualify-teal hover:bg-qualify-teal hover:text-white">
                      <Zap className="mr-2 h-4 w-4" />
                      AI-Chat
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Projects Test Review */}
            <div className="col-span-12">
              <Card className="border-gray-800 bg-qualify-dark-lighter">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="text-white">Projects Test Review</CardTitle>
                </CardHeader>
                <CardContent>
                  <ProjectGrid projects={dashboardData.projects} />
                </CardContent>
              </Card>
            </div>

            {/* Recent Test Runs */}
            <div className="col-span-6">
              <Card className="border-gray-800 bg-qualify-dark-lighter">
                <CardHeader>
                  <CardTitle className="text-sm text-gray-400">Recent Test Runs</CardTitle>
                </CardHeader>
                <CardContent>
                  <RecentTestRuns runs={dashboardData.recent_runs || []} />
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

