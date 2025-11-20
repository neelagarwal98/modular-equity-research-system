"""
Synthesis Agent - Generates comprehensive equity research reports
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain.chains import RetrievalQA
from datetime import datetime

from config import LLM_MODEL, MAX_TOKENS
from utils.logger import logger
from utils.embeddings import VectorStoreManager

class SynthesisAgent:
    """
    Synthesizes research into comprehensive reports with:
    - Executive summary
    - Key findings
    - Detailed analysis
    - Source citations
    - Confidence scores
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model=LLM_MODEL, temperature=0.4, max_tokens=MAX_TOKENS)
        self.vector_manager = VectorStoreManager()
        
        self.report_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert equity research analyst preparing a comprehensive report.
            
            Create a well-structured research report with these sections:
            
            1. EXECUTIVE SUMMARY (2-3 sentences)
            2. KEY FINDINGS (3-5 bullet points)
            3. DETAILED ANALYSIS (2-3 paragraphs)
            4. IMPORTANT CONSIDERATIONS (risks, limitations)
            
            Use professional financial language. Be specific and data-driven when possible.
            Cite sources inline using [Source: URL] format.
            """),
            ("user", """Company: {company_name}
Research Intent: {research_intent}
Key Topics: {key_topics}

Context from sources:
{context}

Question: {question}

Generate a comprehensive research report based on the available information.""")
        ])
    
    def generate_report(
        self, 
        query_analysis: Dict, 
        documents: List[Document], 
        validation_report: Dict,
        user_question: str
    ) -> Dict:
        """Generate comprehensive research report"""
        
        logger.log_activity(
            "Synthesis Agent",
            "Generating report",
            "info",
            f"Processing {len(documents)} documents"
        )
        
        if not documents:
            return self._generate_empty_report(user_question)
        
        try:
            # Create vector store for semantic search
            self.vector_manager.create_vector_store(documents)
            
            # Retrieve relevant context
            relevant_docs = self.vector_manager.similarity_search(user_question, k=5)
            context = self._format_context(relevant_docs)
            
            # Generate report using LLM
            chain = self.report_prompt | self.llm
            
            response = chain.invoke({
                "company_name": query_analysis.get("company_name", "Unknown"),
                "research_intent": query_analysis.get("research_intent", "General research"),
                "key_topics": ", ".join(query_analysis.get("key_topics", [])),
                "context": context,
                "question": user_question
            })
            
            report_content = response.content
            
            # Extract sources properly - THIS IS THE FIX
            sources_list = self._extract_sources(documents, validation_report)
            
            # Build complete report
            report = {
                "title": f"Equity Research Report: {query_analysis.get('company_name', 'N/A')}",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "company": query_analysis.get("company_name", "Unknown"),
                "ticker": query_analysis.get("ticker", "N/A"),
                "research_type": query_analysis.get("research_intent", "General"),
                "content": report_content,
                "confidence_score": validation_report.get("overall_confidence", 0),
                "sources": sources_list,  # Use the properly formatted sources
                "validation_notes": validation_report.get("validation_notes", []),
                "metadata": {
                    "total_sources": len(documents),
                    "trusted_sources": validation_report.get("trusted_sources", 0),
                    "analysis_depth": self._calculate_depth(documents),
                    "sources_analyzed": [doc.metadata.get("source", "Unknown") for doc in documents]
                }
            }
            
            logger.log_activity(
                "Synthesis Agent",
                "Report generated successfully",
                "success",
                f"Confidence: {report['confidence_score']:.1f}% | Sources: {len(sources_list)}"
            )
            
            return report
            
        except Exception as e:
            logger.log_activity(
                "Synthesis Agent",
                "Report generation failed",
                "error",
                str(e)
            )
            return self._generate_error_report(user_question, str(e))
    
    def _format_context(self, documents: List[Document]) -> str:
        """Format documents into context string"""
        context_parts = []
        
        for idx, doc in enumerate(documents[:5]):  # Top 5 most relevant
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content[:400]  # First 400 chars
            context_parts.append(f"[Source {idx + 1}: {source}]\n{content}\n")
        
        return "\n---\n".join(context_parts)
    
    def _extract_sources(self, documents: List[Document], validation_report: Dict = None) -> List[Dict]:
        """
        Extract and format source information properly
        FIXED VERSION - includes credibility scores and proper formatting
        """
        sources = []
        seen_sources = set()
        
        # Get validation scores if available
        doc_scores = {}
        if validation_report:
            for score_info in validation_report.get("document_scores", []):
                source_url = score_info.get("source", "")
                doc_scores[source_url] = {
                    "credibility_score": score_info.get("credibility_score", 0),
                    "is_trusted": score_info.get("is_trusted", False)
                }
        
        for idx, doc in enumerate(documents):
            source_url = doc.metadata.get("source", f"Unknown Source {idx + 1}")
            
            if source_url not in seen_sources:
                # Get domain name for better display
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(source_url)
                    domain = parsed.netloc or parsed.path.split('/')[0]
                    title = f"Source from {domain}" if domain else source_url
                except:
                    title = source_url
                
                # Get validation info
                validation_info = doc_scores.get(source_url, {})
                credibility = validation_info.get("credibility_score", "N/A")
                is_trusted = validation_info.get("is_trusted", False)
                
                source_dict = {
                    "url": source_url,
                    "title": title,
                    "index": len(sources) + 1
                }
                
                # Add credibility if available
                if credibility != "N/A":
                    source_dict["credibility_score"] = credibility
                    source_dict["is_trusted"] = is_trusted
                
                sources.append(source_dict)
                seen_sources.add(source_url)
        
        return sources
    
    def _calculate_depth(self, documents: List[Document]) -> str:
        """Calculate analysis depth based on content volume"""
        total_chars = sum(len(doc.page_content) for doc in documents)
        
        if total_chars > 10000:
            return "Deep"
        elif total_chars > 5000:
            return "Moderate"
        else:
            return "Surface"
    
    def _generate_empty_report(self, question: str) -> Dict:
        """Generate report when no documents available"""
        return {
            "title": "Research Report - No Data Available",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "company": "Unknown",
            "ticker": "N/A",
            "research_type": "Failed",
            "content": """# Unable to Generate Report
            
No sources could be loaded for analysis. This could be due to:
- Invalid or inaccessible URLs
- Network connectivity issues
- Source websites blocking automated access

Please try:
1. Checking the URLs are correct and accessible
2. Using different sources
3. Reformulating your query
            """,
            "confidence_score": 0,
            "sources": [],
            "validation_notes": ["⚠️ No sources available for analysis"],
            "metadata": {
                "total_sources": 0,
                "trusted_sources": 0,
                "analysis_depth": "None"
            }
        }
    
    def _generate_error_report(self, question: str, error: str) -> Dict:
        """Generate report when error occurs"""
        return {
            "title": "Research Report - Error",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "company": "Unknown",
            "ticker": "N/A",
            "research_type": "Error",
            "content": f"""# Report Generation Error
            
An error occurred during report generation:

Error: {error}

Please try again or contact support if the issue persists.
            """,
            "confidence_score": 0,
            "sources": [],
            "validation_notes": ["❌ Report generation failed"],
            "metadata": {
                "total_sources": 0,
                "trusted_sources": 0,
                "analysis_depth": "None"
            }
        }
    
    def answer_question(self, question: str, documents: List[Document]) -> str:
        """Answer a specific question using RAG"""
        try:
            if not documents:
                return "No sources available to answer this question."
            
            # Create vector store
            self.vector_manager.create_vector_store(documents)
            
            # Create QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_manager.vector_store.as_retriever(search_kwargs={"k": 3})
            )
            
            result = qa_chain.invoke({"query": question})
            return result.get("result", "Unable to generate answer.")
            
        except Exception as e:
            logger.log_activity(
                "Synthesis Agent",
                "Question answering failed",
                "error",
                str(e)
            )
            return f"Error answering question: {str(e)}"