"""
Allure Report Parser
Parses Allure JSON/XML format test results
"""
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import zipfile
import io

from shared.schemas import TestStatusEnum
from shared.utils import logger, generate_history_id


class AllureParser:
    """Parser for Allure test reports"""
    
    def __init__(self):
        self.status_mapping = {
            "passed": TestStatusEnum.PASSED,
            "failed": TestStatusEnum.FAILED,
            "broken": TestStatusEnum.BROKEN,
            "skipped": TestStatusEnum.SKIPPED,
            "unknown": TestStatusEnum.UNKNOWN
        }
    
    def parse_json_report(self, file_path: str) -> Dict[str, Any]:
        """
        Parse Allure JSON report file
        
        Args:
            file_path: Path to Allure JSON file
            
        Returns:
            Parsed test report data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self._process_json_data(data)
        except Exception as e:
            logger.error(f"Error parsing JSON report: {str(e)}")
            raise
    
    def parse_json_content(self, content: str) -> Dict[str, Any]:
        """
        Parse Allure JSON content from string
        
        Args:
            content: JSON content as string
            
        Returns:
            Parsed test report data
        """
        try:
            data = json.loads(content)
            return self._process_json_data(data)
        except Exception as e:
            logger.error(f"Error parsing JSON content: {str(e)}")
            raise
    
    def _process_json_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Allure JSON data structure"""
        
        result = {
            "name": data.get("name", "Unknown Test"),
            "fullName": data.get("fullName", data.get("name", "")),
            "status": self._map_status(data.get("status", "unknown")),
            "statusDetails": data.get("statusDetails", {}),
            "time": {
                "start": data.get("start", 0),
                "stop": data.get("stop", 0),
                "duration": data.get("stop", 0) - data.get("start", 0)
            },
            "description": data.get("description", ""),
            "labels": self._extract_labels(data.get("labels", [])),
            "links": data.get("links", []),
            "parameters": self._extract_parameters(data.get("parameters", [])),
            "attachments": self._extract_attachments(data.get("attachments", [])),
            "steps": self._extract_steps(data.get("steps", [])),
            "historyId": data.get("historyId", self._generate_history_id_from_data(data)),
            "testCaseId": data.get("testCaseId"),
            "uuid": data.get("uuid")
        }
        
        return result
    
    def parse_results_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Parse all Allure result files in a directory
        Groups retries by testCaseId and only keeps the final result
        
        Args:
            directory_path: Path to directory containing Allure results
            
        Returns:
            List of parsed test results (deduplicated by testCaseId, keeping latest)
        """
        all_results = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Parse all *-result.json files
        for json_file in directory.glob("*-result.json"):
            try:
                result = self.parse_json_report(str(json_file))
                # Add file modification time for sorting retries
                result["_file_mtime"] = json_file.stat().st_mtime
                all_results.append(result)
            except Exception as e:
                logger.error(f"Error parsing {json_file}: {str(e)}")
                continue
        
        # Group by testCaseId (or historyId if testCaseId not available)
        test_cases = {}
        flaky_tests = []
        
        for result in all_results:
            # Use testCaseId as primary key, fallback to historyId
            key = result.get("testCaseId") or result.get("historyId")
            
            if not key:
                # If no key available, use fullName as fallback
                key = result.get("fullName", result.get("name", ""))
            
            if key not in test_cases:
                test_cases[key] = []
            
            test_cases[key].append(result)
        
        # For each test case, keep only the latest result (by file modification time)
        # Also detect flaky tests (tests with both passed and failed in retries)
        final_results = []
        
        for key, results in test_cases.items():
            # Sort by file modification time (latest first)
            results.sort(key=lambda x: x.get("_file_mtime", 0), reverse=True)
            
            # Get all statuses for this test case
            statuses = [r["status"] for r in results]
            unique_statuses = set(statuses)
            
            # Detect flaky: has both passed and (failed or broken)
            is_flaky = False
            if len(results) > 1:
                has_passed = TestStatusEnum.PASSED in unique_statuses
                has_failed = TestStatusEnum.FAILED in unique_statuses or TestStatusEnum.BROKEN in unique_statuses
                is_flaky = has_passed and has_failed
            
            # Keep the latest result (first after sorting)
            final_result = results[0].copy()
            
            # Remove internal field
            final_result.pop("_file_mtime", None)
            
            # Add retry information
            if len(results) > 1:
                final_result["retry_count"] = len(results) - 1
                final_result["retry_statuses"] = [s.value if hasattr(s, 'value') else str(s) for s in statuses]
                final_result["is_flaky"] = is_flaky
                
                if is_flaky:
                    flaky_tests.append({
                        "testCaseId": key,
                        "test_name": final_result.get("name", "Unknown"),
                        "retry_count": len(results),
                        "statuses": final_result["retry_statuses"],
                        "final_status": final_result["status"].value if hasattr(final_result["status"], 'value') else str(final_result["status"])
                    })
            
            final_results.append(final_result)
        
        logger.info(f"Parsed {len(all_results)} result files -> {len(final_results)} unique test cases from {directory_path}")
        if flaky_tests:
            logger.info(f"Detected {len(flaky_tests)} flaky tests (with retries)")
        
        return final_results
    
    def parse_zip_file(self, zip_content: bytes) -> List[Dict[str, Any]]:
        """
        Parse Allure results from ZIP file
        
        Args:
            zip_content: ZIP file content as bytes
            
        Returns:
            List of parsed test results
        """
        results = []
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
                # Find all result JSON files
                for filename in zf.namelist():
                    if filename.endswith("-result.json"):
                        content = zf.read(filename).decode('utf-8')
                        try:
                            result = self.parse_json_content(content)
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Error parsing {filename}: {str(e)}")
                            continue
        except Exception as e:
            logger.error(f"Error parsing ZIP file: {str(e)}")
            raise
        
        return results
    
    def _map_status(self, status: str) -> TestStatusEnum:
        """Map Allure status to internal status enum"""
        return self.status_mapping.get(status.lower(), TestStatusEnum.UNKNOWN)
    
    def _extract_labels(self, labels: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """Extract and organize labels"""
        organized_labels = {}
        
        for label in labels:
            name = label.get("name", "")
            value = label.get("value", "")
            
            if name not in organized_labels:
                organized_labels[name] = []
            
            organized_labels[name].append(value)
        
        return organized_labels
    
    def _extract_parameters(self, parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract test parameters"""
        params = {}
        
        for param in parameters:
            name = param.get("name", "")
            value = param.get("value", "")
            params[name] = value
        
        return params
    
    def _extract_attachments(self, attachments: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Extract attachment information"""
        processed_attachments = []
        
        for attachment in attachments:
            processed_attachments.append({
                "name": attachment.get("name", ""),
                "source": attachment.get("source", ""),
                "type": attachment.get("type", ""),
            })
        
        return processed_attachments
    
    def _extract_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract test steps"""
        processed_steps = []
        
        for step in steps:
            processed_steps.append({
                "name": step.get("name", ""),
                "status": self._map_status(step.get("status", "unknown")),
                "time": {
                    "start": step.get("start", 0),
                    "stop": step.get("stop", 0),
                    "duration": step.get("stop", 0) - step.get("start", 0)
                },
                "attachments": self._extract_attachments(step.get("attachments", [])),
                "parameters": self._extract_parameters(step.get("parameters", []))
            })
        
        return processed_steps
    
    def _generate_history_id_from_data(self, data: Dict[str, Any]) -> str:
        """Generate history ID from test data"""
        test_name = data.get("fullName", data.get("name", ""))
        parameters = self._extract_parameters(data.get("parameters", []))
        
        return generate_history_id(test_name, parameters)
    
    def extract_error_info(self, status_details: Dict[str, Any]) -> Dict[str, str]:
        """Extract error message and trace from status details"""
        return {
            "message": status_details.get("message", ""),
            "trace": status_details.get("trace", "")
        }
    
    def parse_categories(self, categories_path: str) -> List[Dict[str, Any]]:
        """
        Parse Allure categories.json file
        
        Args:
            categories_path: Path to categories.json
            
        Returns:
            List of categories
        """
        try:
            with open(categories_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error parsing categories: {str(e)}")
            return []
    
    def parse_environment(self, env_path: str) -> Dict[str, str]:
        """
        Parse Allure environment.properties file
        
        Args:
            env_path: Path to environment.properties
            
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Error parsing environment: {str(e)}")
        
        return env_vars


class AllureAggregator:
    """Aggregate multiple Allure reports"""
    
    def __init__(self):
        self.parser = AllureParser()
    
    def aggregate_reports(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate multiple test reports into summary statistics
        
        Args:
            reports: List of parsed test reports
            
        Returns:
            Aggregated statistics
        """
        total_tests = len(reports)
        passed = sum(1 for r in reports if r["status"] == TestStatusEnum.PASSED)
        failed = sum(1 for r in reports if r["status"] == TestStatusEnum.FAILED)
        broken = sum(1 for r in reports if r["status"] == TestStatusEnum.BROKEN)
        skipped = sum(1 for r in reports if r["status"] == TestStatusEnum.SKIPPED)
        
        total_duration = sum(r["time"]["duration"] for r in reports)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        return {
            "total": total_tests,
            "passed": passed,
            "failed": failed,
            "broken": broken,
            "skipped": skipped,
            "pass_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            "total_duration_ms": total_duration,
            "avg_duration_ms": avg_duration,
            "start_time": min((r["time"]["start"] for r in reports), default=0),
            "end_time": max((r["time"]["stop"] for r in reports), default=0)
        }
    
    def group_by_suite(self, reports: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group test reports by suite"""
        suites = {}
        
        for report in reports:
            suite_name = report.get("labels", {}).get("suite", ["default"])[0]
            
            if suite_name not in suites:
                suites[suite_name] = []
            
            suites[suite_name].append(report)
        
        return suites
    
    def identify_flaky_tests(
        self,
        historical_results: List[List[Dict[str, Any]]],
        threshold: float = 0.2
    ) -> List[str]:
        """
        Identify potentially flaky tests from historical data
        
        Args:
            historical_results: List of test run results (each run is a list of test results)
            threshold: Flakiness threshold (0.0 to 1.0)
            
        Returns:
            List of test names that appear to be flaky
        """
        test_history = {}
        
        # Build history for each test
        for run_results in historical_results:
            for result in run_results:
                test_id = result["historyId"]
                
                if test_id not in test_history:
                    test_history[test_id] = {
                        "name": result["name"],
                        "total": 0,
                        "passed": 0,
                        "failed": 0
                    }
                
                test_history[test_id]["total"] += 1
                if result["status"] == TestStatusEnum.PASSED:
                    test_history[test_id]["passed"] += 1
                elif result["status"] in [TestStatusEnum.FAILED, TestStatusEnum.BROKEN]:
                    test_history[test_id]["failed"] += 1
        
        # Identify flaky tests
        flaky_tests = []
        
        for test_id, history in test_history.items():
            if history["total"] < 2:
                continue
            
            # Calculate flakiness score
            minority = min(history["passed"], history["failed"])
            flakiness = minority / history["total"]
            
            if flakiness >= threshold:
                flaky_tests.append({
                    "name": history["name"],
                    "history_id": test_id,
                    "flakiness_score": flakiness,
                    "stats": history
                })
        
        return flaky_tests

