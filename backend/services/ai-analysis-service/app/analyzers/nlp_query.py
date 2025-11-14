"""
Natural Language Query Module
Process natural language queries about test results
"""
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
import json

from shared.config import settings
from shared.utils import logger


class NLPQueryEngine:
    """Natural language query processor for test data"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def process_query(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process natural language query about test results
        
        Args:
            query: User's natural language question
            context: Context data (project info, recent test results, etc.)
            
        Returns:
            Query response with answer and relevant data
        """
        try:
            # Prepare system prompt with context
            system_prompt = self._build_system_prompt(context)
            
            # Create messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # Call OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more factual responses
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            result["query"] = query
            result["confidence"] = result.get("confidence", 0.8)
            
            logger.info(f"NLP query processed: {query[:50]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing NLP query: {str(e)}")
            return {
                "query": query,
                "answer": f"Sorry, I couldn't process your question: {str(e)}",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with context"""
        prompt = """You are QUALIFY.AI, an intelligent assistant for test observability and quality analysis.

You have access to the following test data context:
"""
        
        # Add project information
        if "projects" in context:
            prompt += f"\nProjects: {len(context['projects'])} active projects\n"
        
        # Add recent test results
        if "recent_results" in context:
            prompt += f"\nRecent Test Results Summary:\n"
            results = context["recent_results"]
            prompt += f"- Total Tests: {results.get('total', 0)}\n"
            prompt += f"- Passed: {results.get('passed', 0)}\n"
            prompt += f"- Failed: {results.get('failed', 0)}\n"
            prompt += f"- Pass Rate: {results.get('pass_rate', 0)}%\n"
        
        # Add flaky tests info
        if "flaky_tests" in context:
            flaky = context["flaky_tests"]
            prompt += f"\nFlaky Tests: {len(flaky)} detected\n"
        
        prompt += """
Your job is to answer questions about test results, quality metrics, and provide insights.

Response Format (JSON):
{
    "answer": "Clear, concise answer to the question",
    "data": {"key": "relevant data if applicable"},
    "confidence": 0.85,
    "sources": ["source1", "source2"],
    "suggestions": ["related question 1", "related question 2"]
}

Guidelines:
1. Be concise and specific
2. Use data from the context when available
3. If you don't have enough information, say so
4. Provide actionable insights when possible
5. Suggest follow-up questions
"""
        
        return prompt
    
    async def extract_intent(self, query: str) -> Dict[str, Any]:
        """
        Extract intent and entities from query
        
        Args:
            query: User query
            
        Returns:
            Intent and entities
        """
        try:
            prompt = f"""Analyze this test-related query and extract the intent and entities.

Query: "{query}"

Identify:
1. Intent: What is the user asking for? (e.g., "get_test_results", "analyze_failures", "get_statistics", "find_flaky_tests")
2. Entities: Extract relevant entities (test names, date ranges, projects, etc.)
3. Filters: Any filters mentioned (status, environment, etc.)

Respond in JSON format:
{{
    "intent": "intent_name",
    "entities": {{"entity_type": "entity_value"}},
    "filters": {{"filter_type": "filter_value"}},
    "timeframe": "time period if mentioned"
}}
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an NLP intent classifier for test queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error extracting intent: {str(e)}")
            return {"intent": "unknown", "entities": {}}
    
    async def generate_sql_from_query(
        self,
        query: str,
        schema: Dict[str, Any]
    ) -> str:
        """
        Generate SQL query from natural language
        
        Args:
            query: Natural language query
            schema: Database schema information
            
        Returns:
            SQL query string
        """
        try:
            prompt = f"""Convert this natural language query to SQL based on the schema.

Query: "{query}"

Database Schema:
{json.dumps(schema, indent=2)}

Generate a valid SQL query. Return only the SQL query, no explanations.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at converting natural language to SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            sql = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if sql.startswith("```"):
                sql = sql.split("\n", 1)[1]
                sql = sql.rsplit("```", 1)[0]
            
            return sql.strip()
            
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return ""
    
    async def suggest_follow_up_questions(
        self,
        original_query: str,
        answer: str
    ) -> List[str]:
        """
        Suggest relevant follow-up questions
        
        Args:
            original_query: Original user query
            answer: Answer provided
            
        Returns:
            List of suggested questions
        """
        try:
            prompt = f"""Based on this Q&A, suggest 3 relevant follow-up questions.

Original Question: {original_query}
Answer: {answer}

Generate 3 natural follow-up questions that would provide deeper insights.
Return as JSON array: ["question1", "question2", "question3"]
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are helping generate relevant follow-up questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("questions", [])
            
        except Exception as e:
            logger.error(f"Error suggesting questions: {str(e)}")
            return []

