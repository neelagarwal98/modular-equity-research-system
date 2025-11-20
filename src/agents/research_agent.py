"""
Research Agent - Finds and loads relevant sources for equity research
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.schema import Document
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time

from config import MAX_SOURCES, PRIORITY_DOMAINS, URL_LOAD_TIMEOUT
from utils.logger import logger

class ResearchAgent:
    """
    Finds relevant sources for equity research by:
    - Searching financial news sites
    - Discovering related articles
    - Loading and processing content
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def discover_sources(self, search_queries: List[str], company_name: str) -> List[str]:
        """Discover relevant URLs based on search queries"""
        logger.log_activity(
            "Research Agent",
            "Discovering sources",
            "info",
            f"Searching for: {company_name}"
        )
        
        discovered_urls = []
        
        # Method 1: Use predefined financial news sources
        urls = self._search_financial_sites(search_queries, company_name)
        discovered_urls.extend(urls)
        
        # Method 2: Google search simulation (without API for simplicity)
        # In production, use SerpAPI or similar
        
        # Deduplicate and limit
        unique_urls = list(dict.fromkeys(discovered_urls))[:MAX_SOURCES]
        
        logger.log_activity(
            "Research Agent",
            f"Found {len(unique_urls)} sources",
            "success",
            f"URLs ready for analysis"
        )
        
        return unique_urls
    
    def _search_financial_sites(self, queries: List[str], company_name: str) -> List[str]:
        """Generate URLs from known financial news sources"""
        urls = []
        
        # Predefined high-quality sources for equity research
        base_urls = [
            f"https://www.reuters.com/search/news?blob={quote_plus(company_name)}",
            f"https://www.marketwatch.com/search?q={quote_plus(company_name)}",
            f"https://finance.yahoo.com/quote/{company_name}/",
            f"https://www.fool.com/search/?q={quote_plus(company_name)}",
            f"https://seekingalpha.com/search?q={quote_plus(company_name)}"
        ]
        
        # For demo purposes, use sample URLs that work reliably
        # In production, implement actual search or use APIs
        sample_urls = [
            "https://www.cnbc.com/finance/",
            "https://www.marketwatch.com/",
            "https://finance.yahoo.com/"
        ]
        
        return sample_urls[:MAX_SOURCES]
    
    def load_documents(self, urls: List[str]) -> List[Document]:
        """Load content from discovered URLs"""
        logger.log_activity(
            "Research Agent",
            "Loading documents",
            "info",
            f"Processing {len(urls)} URLs"
        )
        
        documents = []
        successful_loads = 0
        
        for idx, url in enumerate(urls):
            try:
                logger.log_activity(
                    "Research Agent",
                    f"Loading source {idx + 1}/{len(urls)}",
                    "info",
                    url
                )
                
                # Use UnstructuredURLLoader for robust loading
                loader = UnstructuredURLLoader(
                    urls=[url],
                    continue_on_failure=True,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                
                docs = loader.load()
                
                if docs:
                    documents.extend(docs)
                    successful_loads += 1
                    logger.log_activity(
                        "Research Agent",
                        f"Successfully loaded",
                        "success",
                        f"{len(docs[0].page_content[:100])}... chars"
                    )
                else:
                    logger.log_activity(
                        "Research Agent",
                        "No content extracted",
                        "warning",
                        url
                    )
                
                time.sleep(1)  # Respectful crawling
                
            except Exception as e:
                logger.log_activity(
                    "Research Agent",
                    "Failed to load source",
                    "warning",
                    f"{url}: {str(e)}"
                )
                continue
        
        logger.log_activity(
            "Research Agent",
            f"Document loading complete",
            "success",
            f"Loaded {successful_loads}/{len(urls)} sources successfully"
        )
        
        return documents
    
    def load_from_user_urls(self, urls: List[str]) -> List[Document]:
        """Load documents from user-provided URLs (original functionality)"""
        logger.log_activity(
            "Research Agent",
            "Loading user-provided URLs",
            "info",
            f"{len(urls)} URLs provided"
        )
        
        # Filter out empty URLs
        valid_urls = [url.strip() for url in urls if url and url.strip()]
        
        if not valid_urls:
            logger.log_activity(
                "Research Agent",
                "No valid URLs provided",
                "warning",
                "Please enter at least one URL"
            )
            return []
        
        return self.load_documents(valid_urls)
    
    def search_and_load(self, analysis: Dict) -> List[Document]:
        """Main method: Search and load based on query analysis"""
        try:
            # Discover sources
            urls = self.discover_sources(
                analysis.get("search_queries", []),
                analysis.get("company_name", "")
            )
            
            if not urls:
                logger.log_activity(
                    "Research Agent",
                    "No sources discovered",
                    "error",
                    "Unable to find relevant sources"
                )
                return []
            
            # Load documents
            documents = self.load_documents(urls)
            
            return documents
            
        except Exception as e:
            logger.log_activity(
                "Research Agent",
                "Research failed",
                "error",
                str(e)
            )
            return []
