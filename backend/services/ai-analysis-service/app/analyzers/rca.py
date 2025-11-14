"""
Root Cause Analysis (RCA) Module
Analyzes test failures to determine root causes using AI
"""
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import json

from shared.config import settings
from shared.utils import logger


class RootCauseAnalyzer:
    """AI-powered root cause analyzer for test failures"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        
        self.rca_prompt = PromptTemplate(
            input_variables=["test_name", "error_message", "stack_trace", "test_description", "historical_context"],
            template="""You are an expert QA engineer analyzing test failures.

Test Information:
- Test Name: {test_name}
- Description: {test_description}

Failure Details:
- Error Message: {error_message}
- Stack Trace: 
{stack_trace}

Historical Context:
{historical_context}

Please analyze this test failure and provide:
1. Root Cause: The most likely underlying issue causing the failure
2. Confidence Level: Your confidence in this analysis (0-100%)
3. Similar Issues: Any patterns matching known issues
4. Recommended Actions: Specific steps to resolve the issue
5. Category: Classify as (Infrastructure/Code Bug/Test Flakiness/Configuration/Data Issue)

Provide your analysis in JSON format:
{{
    "root_cause": "detailed explanation",
    "confidence": 85,
    "category": "category name",
    "similar_patterns": ["pattern1", "pattern2"],
    "recommended_actions": ["action1", "action2", "action3"],
    "technical_details": "deeper technical analysis"
}}
"""
        )
    
    async def analyze_failure(
        self,
        test_name: str,
        error_message: str,
        stack_trace: str,
        test_description: str = "",
        historical_failures: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a test failure and determine root cause
        
        Args:
            test_name: Name of the failed test
            error_message: Error message from the failure
            stack_trace: Full stack trace
            test_description: Description of what the test does
            historical_failures: List of previous failures for context
            
        Returns:
            Analysis results with root cause and recommendations
        """
        try:
            # Prepare historical context
            historical_context = self._prepare_historical_context(historical_failures)
            
            # Create prompt
            prompt = self.rca_prompt.format(
                test_name=test_name,
                error_message=error_message,
                stack_trace=stack_trace[:2000],  # Limit stack trace length
                test_description=test_description or "No description available",
                historical_context=historical_context
            )
            
            # Call OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert QA engineer specializing in root cause analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            result["analysis_model"] = self.model
            result["tokens_used"] = response.usage.total_tokens
            
            logger.info(f"RCA completed for test: {test_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in RCA analysis: {str(e)}")
            return {
                "root_cause": "Analysis failed - unable to determine root cause",
                "confidence": 0,
                "category": "Unknown",
                "error": str(e)
            }
    
    def _prepare_historical_context(self, historical_failures: Optional[List[Dict[str, Any]]]) -> str:
        """Prepare historical context from previous failures"""
        if not historical_failures:
            return "No historical failures available for this test."
        
        context_parts = ["Previous failures for this test:"]
        
        for i, failure in enumerate(historical_failures[:5], 1):  # Limit to last 5
            context_parts.append(
                f"\n{i}. Date: {failure.get('date', 'Unknown')}, "
                f"Error: {failure.get('error_message', 'N/A')[:200]}"
            )
        
        return "\n".join(context_parts)
    
    async def compare_failures(
        self,
        current_failure: Dict[str, Any],
        historical_failures: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Compare current failure with historical failures to find similar issues
        
        Args:
            current_failure: Current test failure data
            historical_failures: List of historical failures
            
        Returns:
            List of similar failures with similarity scores
        """
        similar_failures = []
        
        try:
            current_error = current_failure.get("error_message", "")
            current_trace = current_failure.get("stack_trace", "")
            
            for historical in historical_failures:
                similarity_score = self._calculate_similarity(
                    current_error,
                    current_trace,
                    historical.get("error_message", ""),
                    historical.get("stack_trace", "")
                )
                
                if similarity_score > 0.7:  # 70% similarity threshold
                    similar_failures.append({
                        "failure_id": historical.get("id"),
                        "date": historical.get("date"),
                        "similarity_score": similarity_score,
                        "error_message": historical.get("error_message")
                    })
            
            # Sort by similarity score
            similar_failures.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return similar_failures[:5]  # Return top 5
            
        except Exception as e:
            logger.error(f"Error comparing failures: {str(e)}")
            return []
    
    def _calculate_similarity(
        self,
        error1: str,
        trace1: str,
        error2: str,
        trace2: str
    ) -> float:
        """
        Calculate similarity between two failures
        Simple implementation - could be enhanced with embeddings
        """
        # Simple word overlap similarity
        def get_words(text: str) -> set:
            return set(text.lower().split())
        
        error1_words = get_words(error1)
        error2_words = get_words(error2)
        
        if not error1_words or not error2_words:
            return 0.0
        
        intersection = error1_words & error2_words
        union = error1_words | error2_words
        
        return len(intersection) / len(union) if union else 0.0
    
    async def analyze_batch(
        self,
        failures: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple failures in batch
        
        Args:
            failures: List of test failures to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        
        for failure in failures:
            analysis = await self.analyze_failure(
                test_name=failure.get("test_name", ""),
                error_message=failure.get("error_message", ""),
                stack_trace=failure.get("stack_trace", ""),
                test_description=failure.get("description", ""),
                historical_failures=failure.get("historical_failures")
            )
            
            results.append({
                "test_id": failure.get("id"),
                "test_name": failure.get("test_name"),
                "analysis": analysis
            })
        
        return results
    
    async def generate_executive_summary(
        self,
        analyses: List[Dict[str, Any]],
        time_period: str = "week"
    ) -> str:
        """
        Generate an executive summary of test failures
        
        Args:
            analyses: List of RCA analyses
            time_period: Time period for the summary
            
        Returns:
            Executive summary text
        """
        try:
            # Prepare summary data
            total_failures = len(analyses)
            categories = {}
            
            for analysis in analyses:
                category = analysis.get("analysis", {}).get("category", "Unknown")
                categories[category] = categories.get(category, 0) + 1
            
            summary_prompt = f"""Generate an executive summary for test failures over the past {time_period}.

Total Failures: {total_failures}
Failure Categories:
{json.dumps(categories, indent=2)}

Key Analyses:
{json.dumps([a.get("analysis", {}).get("root_cause", "") for a in analyses[:5]], indent=2)}

Provide a concise executive summary focusing on:
1. Overall quality health
2. Most critical issues
3. Trends and patterns
4. Recommended actions for management

Keep it brief and business-focused (2-3 paragraphs)."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a QA manager creating executive summaries."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Unable to generate summary: {str(e)}"

