"""
Flaky Test Detection Module
Identifies and analyzes flaky tests
"""
from typing import Dict, Any, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import statistics

from shared.utils import logger, calculate_flakiness_score


class FlakyTestDetector:
    """Detector for identifying flaky tests"""
    
    def __init__(self, min_runs: int = 3, flakiness_threshold: float = 0.2):
        """
        Initialize flaky test detector
        
        Args:
            min_runs: Minimum number of runs before considering a test flaky
            flakiness_threshold: Threshold for flakiness score (0.0 to 1.0)
        """
        self.min_runs = min_runs
        self.flakiness_threshold = flakiness_threshold
    
    def detect_flaky_tests(
        self,
        test_history: List[Dict[str, Any]],
        time_window_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Detect flaky tests from historical test results
        
        Args:
            test_history: List of test results with history_id, status, timestamp
            time_window_days: Number of days to look back
            
        Returns:
            List of flaky tests with analysis
        """
        # Group results by test
        test_groups = defaultdict(list)
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        for result in test_history:
            timestamp = result.get("timestamp", datetime.utcnow())
            if timestamp >= cutoff_date:
                test_id = result.get("history_id")
                test_groups[test_id].append(result)
        
        # Analyze each test
        flaky_tests = []
        
        for test_id, results in test_groups.items():
            if len(results) < self.min_runs:
                continue
            
            analysis = self._analyze_test_stability(results)
            
            if analysis["flakiness_score"] >= self.flakiness_threshold:
                flaky_tests.append({
                    "test_id": test_id,
                    "test_name": results[0].get("test_name", "Unknown"),
                    "flakiness_score": analysis["flakiness_score"],
                    "total_runs": analysis["total_runs"],
                    "passed_runs": analysis["passed_runs"],
                    "failed_runs": analysis["failed_runs"],
                    "failure_rate": analysis["failure_rate"],
                    "patterns": analysis["patterns"],
                    "recommendation": self._generate_recommendation(analysis)
                })
        
        # Sort by flakiness score
        flaky_tests.sort(key=lambda x: x["flakiness_score"], reverse=True)
        
        logger.info(f"Detected {len(flaky_tests)} flaky tests")
        
        return flaky_tests
    
    def _analyze_test_stability(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze stability of a single test"""
        total_runs = len(results)
        passed_runs = sum(1 for r in results if r.get("status") == "passed")
        failed_runs = sum(1 for r in results if r.get("status") in ["failed", "broken"])
        
        flakiness_score = calculate_flakiness_score(total_runs, passed_runs, failed_runs)
        failure_rate = (failed_runs / total_runs) * 100 if total_runs > 0 else 0
        
        # Detect patterns
        patterns = self._detect_patterns(results)
        
        return {
            "total_runs": total_runs,
            "passed_runs": passed_runs,
            "failed_runs": failed_runs,
            "flakiness_score": flakiness_score,
            "failure_rate": failure_rate,
            "patterns": patterns
        }
    
    def _detect_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns in test failures"""
        patterns = {
            "consecutive_failures": 0,
            "alternating": False,
            "time_based": False,
            "environment_specific": False
        }
        
        # Check for consecutive failures
        max_consecutive = 0
        current_consecutive = 0
        prev_status = None
        
        for result in sorted(results, key=lambda x: x.get("timestamp", datetime.min)):
            status = result.get("status")
            
            if status == prev_status and status in ["failed", "broken"]:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
            
            prev_status = status
        
        patterns["consecutive_failures"] = max_consecutive
        
        # Check for alternating pass/fail pattern
        statuses = [r.get("status") for r in sorted(results, key=lambda x: x.get("timestamp", datetime.min))]
        alternations = sum(1 for i in range(len(statuses)-1) if statuses[i] != statuses[i+1])
        patterns["alternating"] = alternations > (len(statuses) * 0.6)
        
        # Check for environment-specific failures
        env_failures = defaultdict(int)
        env_totals = defaultdict(int)
        
        for result in results:
            env = result.get("environment", "default")
            env_totals[env] += 1
            if result.get("status") in ["failed", "broken"]:
                env_failures[env] += 1
        
        # Check if failures are concentrated in specific environments
        if len(env_totals) > 1:
            failure_rates = {env: (env_failures[env] / env_totals[env]) if env_totals[env] > 0 else 0 
                           for env in env_totals}
            if max(failure_rates.values()) - min(failure_rates.values()) > 0.5:
                patterns["environment_specific"] = True
                patterns["environment_details"] = failure_rates
        
        return patterns
    
    def _generate_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Generate recommendations for fixing flaky test"""
        patterns = analysis.get("patterns", {})
        flakiness = analysis["flakiness_score"]
        
        recommendations = []
        
        if flakiness > 0.5:
            recommendations.append("Critical: Test is highly unstable and should be fixed immediately or quarantined.")
        elif flakiness > 0.3:
            recommendations.append("High priority: Test shows significant instability.")
        else:
            recommendations.append("Monitor: Test shows some instability.")
        
        if patterns.get("alternating"):
            recommendations.append("Pattern detected: Alternating pass/fail suggests timing or race condition issues.")
        
        if patterns.get("environment_specific"):
            recommendations.append("Pattern detected: Environment-specific failures suggest configuration issues.")
        
        if patterns.get("consecutive_failures", 0) > 3:
            recommendations.append("Pattern detected: Consecutive failures may indicate a persistent issue rather than flakiness.")
        
        return " ".join(recommendations)
    
    def rank_flaky_tests(
        self,
        flaky_tests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank flaky tests by priority for fixing
        
        Args:
            flaky_tests: List of flaky test analyses
            
        Returns:
            Ranked list with priority scores
        """
        for test in flaky_tests:
            # Calculate priority score (0-100)
            flakiness = test["flakiness_score"]
            total_runs = test["total_runs"]
            
            # Higher flakiness and more runs = higher priority
            priority_score = (flakiness * 70) + min((total_runs / 100) * 30, 30)
            
            test["priority_score"] = round(priority_score, 2)
            
            if priority_score > 70:
                test["priority"] = "Critical"
            elif priority_score > 50:
                test["priority"] = "High"
            elif priority_score > 30:
                test["priority"] = "Medium"
            else:
                test["priority"] = "Low"
        
        # Sort by priority score
        flaky_tests.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return flaky_tests
    
    def generate_flaky_report(
        self,
        flaky_tests: List[Dict[str, Any]],
        time_period: str = "30 days"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive flaky test report
        
        Args:
            flaky_tests: List of flaky tests
            time_period: Time period for the report
            
        Returns:
            Report with statistics and insights
        """
        if not flaky_tests:
            return {
                "summary": f"No flaky tests detected in the last {time_period}",
                "total_flaky_tests": 0
            }
        
        # Calculate statistics
        total_flaky = len(flaky_tests)
        avg_flakiness = statistics.mean([t["flakiness_score"] for t in flaky_tests])
        avg_failure_rate = statistics.mean([t["failure_rate"] for t in flaky_tests])
        
        # Get top offenders
        top_flaky = flaky_tests[:10]
        
        # Count by priority
        priority_counts = defaultdict(int)
        for test in flaky_tests:
            priority = test.get("priority", "Unknown")
            priority_counts[priority] += 1
        
        report = {
            "time_period": time_period,
            "total_flaky_tests": total_flaky,
            "average_flakiness_score": round(avg_flakiness, 3),
            "average_failure_rate": round(avg_failure_rate, 2),
            "priority_breakdown": dict(priority_counts),
            "top_10_flaky_tests": [
                {
                    "name": t["test_name"],
                    "flakiness_score": t["flakiness_score"],
                    "priority": t.get("priority", "Unknown"),
                    "recommendation": t["recommendation"]
                }
                for t in top_flaky
            ],
            "summary": f"Detected {total_flaky} flaky tests with average flakiness score of {avg_flakiness:.2f}"
        }
        
        return report

