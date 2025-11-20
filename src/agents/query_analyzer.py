"""
Query Analyzer Agent - Analyzes and structures user research queries
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, List
import json
import re
from config import LLM_MODEL, LLM_TEMPERATURE
from utils.logger import logger

class QueryAnalyzerAgent:
    """
    Analyzes user queries to extract:
    - Company/ticker information
    - Research intent (valuation, news, competition, etc.)
    - Key topics and entities
    - Suggested search queries
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert financial analyst specializing in equity research.
            Analyze the user's research query and extract structured information.
            
            Return a JSON object with:
            - company_name: Primary company being researched
            - ticker: Stock ticker if mentioned
            - research_intent: Type of research (news, valuation, competition, earnings, outlook, etc.)
            - key_topics: List of important topics to investigate
            - time_frame: Time period of interest (recent, quarterly, annual, etc.)
            - search_queries: 3-5 specific search queries to find relevant information
            
            Example output:
            {{
                "company_name": "Tesla",
                "ticker": "TSLA",
                "research_intent": "earnings_analysis",
                "key_topics": ["Q4 earnings", "delivery numbers", "profit margins"],
                "time_frame": "recent",
                "search_queries": [
                    "Tesla Q4 2024 earnings report",
                    "TSLA delivery numbers 2024",
                    "Tesla profit margin analysis"
                ]
            }}
            """),
            ("user", "{query}")
        ])
    
    def analyze(self, query: str) -> Dict:
        """Analyze the query and return structured information"""
        logger.log_activity(
            "Query Analyzer",
            "Analyzing research query",
            "info",
            f"Query: {query[:100]}..."
        )
        
        try:
            # Generate analysis
            chain = self.prompt | self.llm
            response = chain.invoke({"query": query})
            
            # Parse JSON response
            content = response.content
            
            # Extract JSON from response (handle cases where LLM adds extra text)
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                # Fallback parsing
                analysis = self._fallback_parse(query)
            
            # Validate and set defaults
            analysis = self._validate_analysis(analysis, query)
            
            logger.log_activity(
                "Query Analyzer",
                "Query analysis complete",
                "success",
                f"Identified: {analysis.get('company_name', 'Unknown')}"
            )
            
            return analysis
            
        except Exception as e:
            logger.log_activity(
                "Query Analyzer",
                "Analysis failed, using fallback",
                "warning",
                str(e)
            )
            return self._fallback_parse(query)
    
    def _validate_analysis(self, analysis: Dict, original_query: str) -> Dict:
        """Validate and ensure all required fields exist"""
        defaults = {
            "company_name": "Unknown",
            "ticker": "",
            "research_intent": "general_research",
            "key_topics": [],
            "time_frame": "recent",
            "search_queries": []
        }
        
        # Merge with defaults
        for key, default_value in defaults.items():
            if key not in analysis or not analysis[key]:
                analysis[key] = default_value
        
        # If no search queries, create basic ones
        if not analysis["search_queries"]:
            company = analysis["company_name"]
            analysis["search_queries"] = [
                f"{company} latest news",
                f"{company} stock analysis",
                f"{company} financial performance"
            ]
        
        return analysis
    
    def _fallback_parse(self, query: str) -> Dict:
        """Simple fallback parser if LLM fails"""
        # Extract potential company name (capitalize words)
        words = query.split()
        company_candidates = [w for w in words if w[0].isupper() and len(w) > 2]
        company_name = ' '.join(company_candidates[:2]) if company_candidates else "Unknown Company"
        
        return {
            "company_name": company_name,
            "ticker": "",
            "research_intent": "general_research",
            "key_topics": ["latest news", "financial performance"],
            "time_frame": "recent",
            "search_queries": [
                f"{company_name} latest news",
                f"{company_name} stock analysis",
                f"{company_name} earnings"
            ]
        }
