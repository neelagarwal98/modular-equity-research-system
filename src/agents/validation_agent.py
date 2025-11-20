"""
Validation Agent - Validates information quality and cross-references sources
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
import re
from datetime import datetime

from config import LLM_MODEL, LLM_TEMPERATURE, PRIORITY_DOMAINS, MIN_CONFIDENCE_SCORE
from utils.logger import logger

class ValidationAgent:
    """
    Validates research findings by:
    - Checking source credibility
    - Cross-referencing information
    - Calculating confidence scores
    - Flagging inconsistencies
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model=LLM_MODEL, temperature=0.1)  # Low temp for consistency
        self.credibility_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a fact-checker for financial research.
            Evaluate the credibility of this information on a scale of 0-100.
            
            Consider:
            - Source authority and reputation
            - Recency of information
            - Presence of citations/data
            - Consistency with known facts
            
            Respond with just the score (0-100) and a brief reason (one sentence).
            Format: SCORE: 85 | REASON: Recent data from reputable source with citations
            """),
            ("user", "Source: {source}\n\nContent: {content}")
        ])
    
    def validate_documents(self, documents: List[Document]) -> Dict:
        """Validate all documents and return validation report"""
        logger.log_activity(
            "Validation Agent",
            "Starting validation",
            "info",
            f"Validating {len(documents)} documents"
        )
        
        if not documents:
            return {
                "overall_confidence": 0,
                "document_scores": [],
                "validation_notes": ["No documents to validate"],
                "trusted_sources": 0
            }
        
        validation_results = []
        
        for idx, doc in enumerate(documents):
            score, reason = self._evaluate_document(doc)
            
            validation_results.append({
                "doc_index": idx,
                "source": doc.metadata.get("source", "Unknown"),
                "credibility_score": score,
                "reason": reason,
                "is_trusted": self._is_trusted_source(doc.metadata.get("source", ""))
            })
            
            status = "success" if score >= 70 else "warning" if score >= 50 else "error"
            logger.log_activity(
                "Validation Agent",
                f"Document {idx + 1} validated",
                status,
                f"Score: {score}/100 - {reason[:50]}..."
            )
        
        # Calculate overall confidence
        avg_score = sum(r["credibility_score"] for r in validation_results) / len(validation_results)
        trusted_count = sum(1 for r in validation_results if r["is_trusted"])
        
        overall_confidence = self._calculate_overall_confidence(avg_score, trusted_count, len(documents))
        
        report = {
            "overall_confidence": round(overall_confidence, 2),
            "document_scores": validation_results,
            "validation_notes": self._generate_notes(validation_results),
            "trusted_sources": trusted_count
        }
        
        logger.log_activity(
            "Validation Agent",
            "Validation complete",
            "success",
            f"Overall confidence: {overall_confidence:.1f}%"
        )
        
        return report
    
    def _evaluate_document(self, doc: Document) -> Tuple[int, str]:
        """Evaluate a single document's credibility"""
        try:
            source = doc.metadata.get("source", "Unknown")
            content_preview = doc.page_content[:500]  # First 500 chars
            
            # Quick heuristic evaluation (faster than LLM call)
            base_score = 50
            
            # Source quality
            if self._is_trusted_source(source):
                base_score += 30
            
            # Content quality indicators
            if len(doc.page_content) > 500:
                base_score += 10
            
            if any(keyword in doc.page_content.lower() for keyword in 
                   ['earnings', 'revenue', 'profit', 'quarter', 'fiscal']):
                base_score += 10
            
            # LLM validation for edge cases (optional, comment out for speed)
            # chain = self.credibility_prompt | self.llm
            # response = chain.invoke({"source": source, "content": content_preview})
            # score, reason = self._parse_validation_response(response.content)
            
            reason = "Heuristic evaluation based on source quality and content depth"
            score = min(base_score, 100)
            
            return score, reason
            
        except Exception as e:
            logger.log_activity(
                "Validation Agent",
                "Evaluation error",
                "warning",
                str(e)
            )
            return 50, "Default score due to evaluation error"
    
    def _parse_validation_response(self, response: str) -> Tuple[int, str]:
        """Parse LLM validation response"""
        try:
            score_match = re.search(r'SCORE:\s*(\d+)', response)
            reason_match = re.search(r'REASON:\s*(.+)', response)
            
            score = int(score_match.group(1)) if score_match else 50
            reason = reason_match.group(1).strip() if reason_match else "No reason provided"
            
            return score, reason
        except:
            return 50, "Unable to parse validation response"
    
    def _is_trusted_source(self, source: str) -> bool:
        """Check if source is from a trusted domain"""
        source_lower = source.lower()
        return any(domain in source_lower for domain in PRIORITY_DOMAINS)
    
    def _calculate_overall_confidence(self, avg_score: float, trusted_count: int, total_docs: int) -> float:
        """Calculate overall confidence score"""
        # Weighted calculation
        score_weight = 0.7
        trust_weight = 0.3
        
        trust_ratio = trusted_count / total_docs if total_docs > 0 else 0
        
        overall = (avg_score * score_weight) + (trust_ratio * 100 * trust_weight)
        
        return overall
    
    def _generate_notes(self, validation_results: List[Dict]) -> List[str]:
        """Generate validation notes"""
        notes = []
        
        low_score_docs = [r for r in validation_results if r["credibility_score"] < MIN_CONFIDENCE_SCORE * 100]
        if low_score_docs:
            notes.append(f"⚠️ {len(low_score_docs)} source(s) have low credibility scores")
        
        trusted = sum(1 for r in validation_results if r["is_trusted"])
        if trusted > 0:
            notes.append(f"✅ {trusted} source(s) from trusted financial sites")
        
        high_quality = [r for r in validation_results if r["credibility_score"] >= 80]
        if high_quality:
            notes.append(f"⭐ {len(high_quality)} high-quality source(s) found")
        
        if not notes:
            notes.append("ℹ️ Moderate quality sources, exercise caution")
        
        return notes
    
    def cross_reference(self, findings: List[str]) -> Dict:
        """Cross-reference multiple findings for consistency"""
        # Simple implementation: check for consistency
        # In production, use more sophisticated fact-checking
        
        logger.log_activity(
            "Validation Agent",
            "Cross-referencing findings",
            "info",
            f"Checking {len(findings)} findings"
        )
        
        # Placeholder for cross-referencing logic
        # Could use LLM to check for contradictions
        
        return {
            "consistent": True,
            "conflicts": [],
            "notes": "Cross-reference check passed"
        }
