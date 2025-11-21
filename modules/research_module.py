import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.schema import Document
import requests
import time

from config import MAX_SOURCES, PRIORITY_DOMAINS, SERPER_API_KEY
from utils.logger import logger

class ResearchModule:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Initialize Google SERP API
        try:
            if SERPER_API_KEY:
                os.environ['SERPER_API_KEY'] = SERPER_API_KEY
                self.search = GoogleSerperAPIWrapper()
                self.serp_enabled = True
                logger.log_activity(
                    "Research Module",
                    "Google SERP API initialized",
                    "success",
                    "Using dynamic search"
                )
            else:
                self.serp_enabled = False
                logger.log_activity(
                    "Research Module",
                    "SERP API not configured",
                    "warning",
                    "Using fallback sources"
                )
        except Exception as e:
            self.serp_enabled = False
            logger.log_activity(
                "Research Module",
                "SERP API initialization failed",
                "warning",
                str(e)
            )
    
    def discover_sources(self, search_queries: List[str], company_name: str) -> List[str]:
        """Discover URLs using Google SERP API or fallback"""
        logger.log_activity(
            "Research Module",
            "Discovering sources",
            "info",
            f"Searching for: {company_name}"
        )
        
        discovered_urls = []
        
        if self.serp_enabled:
            urls = self._search_with_serp_api(search_queries, company_name)
            discovered_urls.extend(urls)
        else:
            urls = self._fallback_sources(company_name)
            discovered_urls.extend(urls)
        
        # Filter and prioritize financial URLs
        filtered_urls = self._filter_financial_urls(discovered_urls)
        unique_urls = list(dict.fromkeys(filtered_urls))[:MAX_SOURCES]
        
        logger.log_activity(
            "Research Module",
            f"Found {len(unique_urls)} sources",
            "success",
            "URLs ready for analysis"
        )
        
        return unique_urls
    
    def _search_with_serp_api(self, queries: List[str], company_name: str) -> List[str]:
        """Search using Google SERP API"""
        all_urls = []
        
        # Enhanced queries
        enhanced_queries = [
            f"{company_name} stock analysis financial news",
            f"{company_name} earnings report",
            f"{company_name} investor relations",
            *queries[:4]
        ]
        
        for query in enhanced_queries[:7]:
            try:
                logger.log_activity(
                    "Research Module",
                    "Searching Google",
                    "info",
                    query[:50] + "..."
                )
                
                results = self.search.results(query)
                
                if 'organic' in results:
                    for result in results['organic'][:3]:
                        if 'link' in result:
                            all_urls.append(result['link'])
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.log_activity(
                    "Research Module",
                    "Search error",
                    "warning",
                    str(e)[:50]
                )
                continue
        
        return all_urls
    
    def _filter_financial_urls(self, urls: List[str]) -> List[str]:
        """Filter for quality financial sources"""
        prioritized = []
        other_urls = []
        
        for url in urls:
            url_lower = url.lower()
            
            # Exclude social media, videos, etc.
            excluded = [
                'youtube.com', 'twitter.com', 'facebook.com',
                'instagram.com', 'reddit.com', 'pinterest.com'
            ]
            
            if any(ex in url_lower for ex in excluded):
                continue
            
            # Prioritize trusted financial domains
            if any(domain in url_lower for domain in PRIORITY_DOMAINS):
                prioritized.append(url)
            else:
                other_urls.append(url)
        
        return prioritized + other_urls
    
    def _fallback_sources(self, company_name: str) -> List[str]:
        """Fallback when SERP API unavailable"""
        logger.log_activity(
            "Research Module",
            "Using fallback sources",
            "warning",
            "Add SERPER_API_KEY to .env for better results"
        )
        
        return [
            "https://www.cnbc.com/finance/",
            "https://www.marketwatch.com/",
            "https://finance.yahoo.com/",
            "https://www.reuters.com/business/",
            "https://www.bloomberg.com/"
        ][:MAX_SOURCES]
    
    def load_documents(self, urls: List[str]) -> List[Document]:
        """Load content from URLs"""
        logger.log_activity(
            "Research Module",
            "Loading documents",
            "info",
            f"Processing {len(urls)} URLs"
        )
        
        documents = []
        successful_loads = 0
        
        for idx, url in enumerate(urls):
            try:
                logger.log_activity(
                    "Research Module",
                    f"Loading {idx + 1}/{len(urls)}",
                    "info",
                    url[:60] + "..."
                )
                
                loader = UnstructuredURLLoader(
                    urls=[url],
                    continue_on_failure=True,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                
                docs = loader.load()
                
                if docs and len(docs[0].page_content) > 100:
                    documents.extend(docs)
                    successful_loads += 1
                    logger.log_activity(
                        "Research Module",
                        "Loaded successfully",
                        "success",
                        f"{len(docs[0].page_content)} chars"
                    )
                
                time.sleep(1)
                
            except Exception as e:
                logger.log_activity(
                    "Research Module",
                    "Load failed",
                    "warning",
                    str(e)[:50]
                )
                continue
        
        logger.log_activity(
            "Research Module",
            "Loading complete",
            "success",
            f"{successful_loads}/{len(urls)} sources loaded"
        )
        
        return documents
    
    def load_from_user_urls(self, urls: List[str]) -> List[Document]:
        """Load from user-provided URLs"""
        logger.log_activity(
            "Research Module",
            "Loading user URLs",
            "info",
            f"{len(urls)} provided"
        )
        
        valid_urls = [url.strip() for url in urls if url and url.strip()]
        
        if not valid_urls:
            logger.log_activity(
                "Research Module",
                "No valid URLs",
                "warning",
                "Enter at least one URL"
            )
            return []
        
        return self.load_documents(valid_urls)
    
    def search_and_load(self, analysis: Dict) -> List[Document]:
        """Main method: search and load"""
        try:
            urls = self.discover_sources(
                analysis.get("search_queries", []),
                analysis.get("company_name", "")
            )
            
            if not urls:
                logger.log_activity(
                    "Research Module",
                    "No sources found",
                    "error",
                    "Unable to discover sources"
                )
                return []
            
            return self.load_documents(urls)
            
        except Exception as e:
            logger.log_activity(
                "Research Module",
                "Research failed",
                "error",
                str(e)
            )
            return []