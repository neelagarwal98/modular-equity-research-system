"""
Modular Equity Research System
Streamlit Dashboard
"""
import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.query_analyzer import QueryAnalyzer
from modules.research_module import ResearchModule
from modules.validation_module import ValidationModule
from modules.synthesis_module import SynthesisModule
from utils.logger import logger
from config import OPENAI_API_KEY

# Page configuration
st.set_page_config(
    page_title="Modular Equity Research System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .module-status {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .confidence-high {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .confidence-medium {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .confidence-low {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'research_complete' not in st.session_state:
        st.session_state.research_complete = False
    if 'report' not in st.session_state:
        st.session_state.report = None
    if 'query_analysis' not in st.session_state:
        st.session_state.query_analysis = None

def check_api_key():
    """Check if OpenAI API key is configured"""
    if not OPENAI_API_KEY:
        st.error("⚠️ OpenAI API key not found! Please set OPENAI_API_KEY in your .env file")
        st.info("Create a .env file with: OPENAI_API_KEY=your_key_here")
        st.stop()

def display_header():
    """Display application header"""
    st.markdown('<p class="main-header">📊 Modular Equity Research System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI modules working in coordination to analyze financial markets</p>', unsafe_allow_html=True)
    st.markdown("---")

def display_module_info():
    """Display information about the modules"""
    with st.expander("🤖 About the Modular System", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("### 🔍 Query Analyzer")
            st.write("Analyzes research queries and extracts key information")
        
        with col2:
            st.markdown("### 📰 Research Module")
            st.write("Discovers and loads relevant sources autonomously")
        
        with col3:
            st.markdown("### ✅ Validation Module")
            st.write("Validates sources and calculates confidence scores")
        
        with col4:
            st.markdown("### 📝 Synthesis Module")
            st.write("Generates comprehensive research reports")

def run_research(query: str, mode: str, user_urls: list = None):
    """Execute the multi modular research pipeline"""
    logger.clear_logs()
    
    try:
        # Initialize modules
        query_analyzer = QueryAnalyzer()
        research_module = ResearchModule()
        validation_module = ValidationModule()
        synthesis_module = SynthesisModule()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Query Analysis (20%)
        status_text.text("🔍 Analyzing your query...")
        progress_bar.progress(20)
        query_analysis = query_analyzer.analyze(query)
        st.session_state.query_analysis = query_analysis
        
        # Display analysis
        with st.expander("📋 Query Analysis Results", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Company:**", query_analysis.get("company_name", "N/A"))
                st.write("**Ticker:**", query_analysis.get("ticker", "N/A"))
                st.write("**Research Type:**", query_analysis.get("research_intent", "N/A"))
            with col2:
                st.write("**Key Topics:**")
                for topic in query_analysis.get("key_topics", []):
                    st.write(f"- {topic}")
        
        # Step 2: Research (40%)
        status_text.text("📰 Discovering and loading sources...")
        progress_bar.progress(40)
        
        if mode == "autonomous" or not user_urls:
            documents = research_module.search_and_load(query_analysis)
        else:
            documents = research_module.load_from_user_urls(user_urls)
        
        if not documents:
            st.error("❌ No sources could be loaded. Please try different URLs or query.")
            return
        
        st.success(f"✅ Loaded {len(documents)} sources successfully")
        
        # Step 3: Validation (60%)
        status_text.text("✅ Validating sources and checking credibility...")
        progress_bar.progress(60)
        validation_report = validation_module.validate_documents(documents)
        
        # Display validation
        with st.expander("🔒 Validation Report", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                confidence = validation_report.get("overall_confidence", 0)
                st.metric("Overall Confidence", f"{confidence:.1f}%")
            with col2:
                st.metric("Total Sources", validation_report.get("trusted_sources", 0))
            with col3:
                st.metric("Trusted Sources", validation_report.get("trusted_sources", 0))
            
            for note in validation_report.get("validation_notes", []):
                st.info(note)
        
        # Step 4: Synthesis (80%)
        status_text.text("📝 Generating comprehensive report...")
        progress_bar.progress(80)
        report = synthesis_module.generate_report(
            query_analysis,
            documents,
            validation_report,
            query
        )
        st.session_state.report = report
        
        # Complete (100%)
        progress_bar.progress(100)
        status_text.text("✅ Research complete!")
        st.session_state.research_complete = True
        
        # Display report
        # display_report(report)
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)

def display_report(report: dict):
    """Display the generated research report"""
    st.markdown("---")
    st.markdown("## 📊 Research Report")
    
    # Header with metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Company", report.get("company", "N/A"))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Ticker", report.get("ticker", "N/A"))
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        confidence = report.get("confidence_score", 0)
        st.metric("Confidence", f"{confidence:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Sources", report["metadata"].get("total_sources", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Confidence indicator
    confidence = report.get("confidence_score", 0)
    if confidence >= 75:
        css_class = "confidence-high"
        indicator = "🟢 High Confidence"
    elif confidence >= 50:
        css_class = "confidence-medium"
        indicator = "🟡 Medium Confidence"
    else:
        css_class = "confidence-low"
        indicator = "🔴 Low Confidence"
    
    st.markdown(f'<div class="module-status {css_class}">{indicator}</div>', unsafe_allow_html=True)
    
    # Report content
    st.markdown("### 📄 Report Content")
    st.markdown(report.get("content", "No content available"))
    
    # # Sources
    # st.markdown("### 🔗 Sources")
    # sources = report.get("sources", [])
    # if sources:
    #     for idx, source in enumerate(sources, 1):
    #         st.markdown(f"{idx}. [{source.get('title', 'Source')}]({source.get('url', '#')})")
    # else:
    #     st.info("No sources available")
    # Sources
    

    st.markdown("### 🔗 Sources")
    sources = report.get("sources", [])

    if sources and len(sources) > 0:
        st.markdown(f"**Analyzed {len(sources)} source(s):**")
        st.markdown("")  # Add spacing
        
        for source in sources:
            if isinstance(source, dict):
                # Get source information
                url = source.get('url', '#')
                title = source.get('title', url)
                index = source.get('index', '')
                credibility = source.get('credibility_score')
                is_trusted = source.get('is_trusted', False)
                
                # Create source display with credibility badge
                if credibility and credibility != "N/A":
                    # Color code based on credibility
                    if credibility >= 80:
                        badge_color = "🟢"
                        badge_text = f"High Quality ({credibility}/100)"
                    elif credibility >= 60:
                        badge_color = "🟡"
                        badge_text = f"Medium Quality ({credibility}/100)"
                    else:
                        badge_color = "🔴"
                        badge_text = f"Low Quality ({credibility}/100)"
                    
                    # Display with badge
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{index}.** [{title}]({url})")
                    with col2:
                        st.caption(f"{badge_color} {badge_text}")
                        if is_trusted:
                            st.caption("✅ Trusted Source")
                else:
                    # Display without credibility score
                    st.markdown(f"**{index}.** [{title}]({url})")
                
                st.markdown("")  # Add spacing between sources
                
            elif isinstance(source, str):
                # Source is just a URL string
                st.markdown(f"- [{source}]({source})")
    else:
        # Try to get sources from metadata as fallback
        metadata_sources = report.get("metadata", {}).get("sources_analyzed", [])
        if metadata_sources:
            st.markdown(f"**Sources analyzed ({len(metadata_sources)}):**")
            for idx, source_url in enumerate(metadata_sources, 1):
                # Extract domain for display
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(source_url)
                    domain = parsed.netloc or "Unknown"
                    st.markdown(f"{idx}. [{domain}]({source_url})")
                except:
                    st.markdown(f"{idx}. [{source_url}]({source_url})")
        else:
            st.info("ℹ️ No source information available in this report")
    
    # Validation notes
    if report.get("validation_notes"):
        st.markdown("### ℹ️ Validation Notes")
        for note in report["validation_notes"]:
            st.info(note)
    
    # Metadata
    with st.expander("📈 Analysis Metadata"):
        st.json(report["metadata"])

def main():
    """Main application function"""
    initialize_session_state()
    check_api_key()
    display_header()
    display_module_info()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Research Configuration")
        
        # Mode selection
        mode = st.radio(
            "Research Mode",
            ["autonomous", "manual"],
            format_func=lambda x: "🤖 Autonomous (AI finds sources)" if x == "autonomous" else "📝 Manual (Provide URLs)",
            help="Autonomous mode: AI modules discover sources automatically\nManual mode: Provide your own URLs"
        )
        
        user_urls = []
        if mode == "manual":
            st.markdown("### 📎 Enter URLs")
            st.caption("Provide up to 5 URLs for analysis")
            for i in range(5):
                url = st.text_input(f"URL {i+1}", key=f"url_{i}", placeholder="https://example.com/article")
                if url:
                    user_urls.append(url)
        
        st.markdown("---")
        st.markdown("### 📊 Activity Log")
        log_container = st.container()
        
        with log_container:
            logger.display_logs()
        
        if st.button("🗑️ Clear Log"):
            logger.clear_logs()
            st.rerun()
    
    # Main content area
    st.markdown("## 🔍 Research Query")
    
    # Query input
    query_input = st.text_area(
        "Enter your equity research question:",
        placeholder="Example: Analyze Tesla's recent earnings performance and delivery numbers for Q4 2024",
        height=100,
        help="Be specific! Include company name and what you want to research."
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        start_research = st.button("🚀 Start Research", type="primary", use_container_width=True)
    with col2:
        if st.session_state.research_complete:
            if st.button("🔄 New Research", use_container_width=True):
                st.session_state.research_complete = False
                st.session_state.report = None
                logger.clear_logs()
                st.rerun()
    
    # Execute research
    if start_research and query_input:
        run_research(query_input, mode, user_urls if mode == "manual" else None)
    elif start_research:
        st.warning("⚠️ Please enter a research query")
    
    # Display existing report if available
    if st.session_state.research_complete and st.session_state.report:
        display_report(st.session_state.report)

if __name__ == "__main__":
    main()
