/**
 * Load Allure data directly from files
 */

export interface AllureResult {
  uuid: string;
  name: string;
  fullName: string;
  status: 'passed' | 'failed' | 'broken' | 'skipped';
  statusDetails?: {
    message?: string;
    trace?: string;
  };
  start: number;
  stop: number;
  labels?: Array<{ name: string; value: string }>;
  parameters?: Array<{ name: string; value: string }>;
}

/**
 * Parse Allure results from folder path
 */
export async function loadAllureDataFromFolder(folderPath: string): Promise<any> {
  // For development: load from JSON files in public folder
  // In production: this would call backend API
  
  try {
    // Try to load from backend API first
    const response = await fetch('http://localhost:8004/dashboard');
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.log('Backend not available, loading from local files...');
  }
  
  // Fallback: Load sample data
  try {
    const response = await fetch('/sample-data/sample-allure-result.json');
    const results: AllureResult[] = await response.json();
    
    return aggregateResults(results);
  } catch (error) {
    console.error('Error loading sample data:', error);
    return null;
  }
}

/**
 * Aggregate Allure results to dashboard format
 */
export function aggregateResults(results: AllureResult[]) {
  const total = results.length;
  const passed = results.filter(r => r.status === 'passed').length;
  const failed = results.filter(r => r.status === 'failed' || r.status === 'broken').length;
  const skipped = results.filter(r => r.status === 'skipped').length;
  
  const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
  
  // Group by suite
  const suites: Record<string, { total: number; passed: number }> = {};
  results.forEach(r => {
    const suiteLabel = r.labels?.find(l => l.name === 'suite');
    const suiteName = suiteLabel?.value || 'Unknown';
    
    if (!suites[suiteName]) {
      suites[suiteName] = { total: 0, passed: 0 };
    }
    suites[suiteName].total++;
    if (r.status === 'passed') {
      suites[suiteName].passed++;
    }
  });
  
  // Convert to projects array
  const projects = Object.entries(suites).map(([name, stats]) => ({
    name: name.split('\\').pop() || name,
    pass_rate: Math.round((stats.passed / stats.total) * 100),
    trend: stats.passed > stats.total / 2 ? 'up' : 'down',
  }));
  
  // Generate trend data (mock for now)
  const trends = Array.from({ length: 9 }, (_, i) => ({
    date: `${i * 30}ms`,
    passed: Math.floor(passed * (0.8 + Math.random() * 0.4)),
    failed: Math.floor(failed * (0.8 + Math.random() * 0.4)),
  }));
  
  return {
    overall_health: {
      pass_rate: passRate,
      total_tests: total,
      passed,
      failed,
      avg_duration_ms: 45000,
    },
    recent_trends: trends,
    projects: projects.slice(0, 6),
    flaky_tests: [],
  };
}

