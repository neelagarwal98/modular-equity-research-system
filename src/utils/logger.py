"""
Activity Logger for tracking module operations
"""
import streamlit as st
from datetime import datetime
from typing import List, Dict
import json

class ModuleLogger:
    """Tracks and displays Module activities in real-time"""
    
    def __init__(self):
        if 'activity_log' not in st.session_state:
            st.session_state.activity_log = []
    
    def log_activity(self, module_name: str, action: str, status: str = "info", details: str = ""):
        """Log an module activity"""
        log_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "module": module_name,
            "action": action,
            "status": status,  # info, success, warning, error
            "details": details
        }
        st.session_state.activity_log.append(log_entry)
        return log_entry
    
    def get_logs(self) -> List[Dict]:
        """Retrieve all logs"""
        return st.session_state.activity_log
    
    def clear_logs(self):
        """Clear all logs"""
        st.session_state.activity_log = []
    
    def display_logs(self, container=None):
        """Display logs in Streamlit UI"""
        if container is None:
            container = st
        
        logs = self.get_logs()
        if not logs:
            container.info("No activities yet. Start a research query!")
            return
        
        for log in reversed(logs[-10:]):  # Show last 10 activities
            status_emoji = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌"
            }.get(log["status"], "ℹ️")
            
            container.text(f"{status_emoji} [{log['timestamp']}] {log['module']}: {log['action']}")
            if log.get("details"):
                container.caption(f"   └─ {log['details']}")

# Global logger instance
logger = ModuleLogger()
