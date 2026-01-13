"""
Streamlit Frontend - Interactive web interface for customer service chatbot.
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

# Page configuration
st.set_page_config(
    page_title="AI Customer Service",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #DBEAFE;
        margin-left: 2rem;
    }
    .bot-message {
        background-color: #F3F4F6;
        margin-right: 2rem;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .sentiment-positive {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .sentiment-negative {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    .sentiment-neutral {
        background-color: #E5E7EB;
        color: #374151;
    }
    .recommendation-card {
        padding: 1rem;
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .stats-card {
        background-color: #F9FAFB;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def call_api(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
    """
    Call API endpoint.
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        data: Request data for POST requests
        
    Returns:
        Response data
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return {}
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}
    
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return {}


def display_message(role: str, content: str, metadata: Optional[Dict] = None):
    """
    Display chat message.
    
    Args:
        role: Message role (user/assistant)
        content: Message content
        metadata: Optional metadata
    """
    css_class = "user-message" if role == "user" else "bot-message"
    icon = "👤" if role == "user" else "🤖"
    
    message_html = f"""
    <div class="chat-message {css_class}">
        <strong>{icon} {role.capitalize()}:</strong><br/>
        {content}
    """
    
    if metadata:
        if 'intent' in metadata:
            message_html += f'<br/><br/><span class="intent-badge" style="background-color: #DBEAFE; color: #1E40AF;">Intent: {metadata["intent"]}</span>'
        
        if 'sentiment' in metadata:
            sentiment = metadata['sentiment'].get('sentiment', 'neutral')
            sentiment_class = f"sentiment-{sentiment}"
            message_html += f'<span class="intent-badge {sentiment_class}">Sentiment: {sentiment}</span>'
    
    message_html += "</div>"
    st.markdown(message_html, unsafe_allow_html=True)


def display_recommendations(recommendations: List[Dict]):
    """Display recommendations."""
    if not recommendations:
        return
    
    st.markdown("### 💡 Recommendations")
    
    for rec in recommendations:
        relevance = rec.get('relevance_score', 0) * 100
        st.markdown(f"""
        <div class="recommendation-card">
            <strong>{rec['name']}</strong><br/>
            <small style="color: #6B7280;">{rec['category']}</small><br/>
            {rec['description']}<br/>
            <small style="color: #059669;">Relevance: {relevance:.0f}%</small>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application."""
    
    # Header
    st.markdown('<div class="main-header">🤖 AI-Powered Customer Service</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Check API status
        health_data = call_api("/health", "GET")
        if health_data:
            status = health_data.get('status', 'unknown')
            status_color = "🟢" if status == "healthy" else "🟡"
            st.markdown(f"**API Status:** {status_color} {status.upper()}")
        else:
            st.markdown("**API Status:** 🔴 OFFLINE")
        
        st.divider()
        
        # User settings
        st.subheader("User Settings")
        user_id = st.text_input("User ID (optional)", placeholder="Enter your ID")
        
        use_rag = st.checkbox("Enable RAG (Knowledge Base)", value=True, 
                             help="Use retrieval-augmented generation for better responses")
        
        st.divider()
        
        # Session management
        st.subheader("Session Management")
        
        if st.button("🔄 New Session"):
            if 'session_id' in st.session_state:
                # End current session
                call_api(f"/session/{st.session_state.session_id}", "DELETE")
            st.session_state.clear()
            st.rerun()
        
        if 'session_id' in st.session_state:
            st.info(f"Session: {st.session_state.session_id[:8]}...")
        
        st.divider()
        
        # Statistics
        if st.button("📊 View Statistics"):
            stats_data = call_api("/statistics", "GET")
            if stats_data:
                st.subheader("System Statistics")
                sessions = stats_data.get('sessions', {})
                st.metric("Active Sessions", sessions.get('total_sessions', 0))
                st.metric("Active Users", sessions.get('active_users', 0))
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    # Main chat area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat")
        
        # Display conversation history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                display_message(
                    role=message['role'],
                    content=message['content'],
                    metadata=message.get('metadata')
                )
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message to history
            st.session_state.messages.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Call API
            with st.spinner("Thinking..."):
                response_data = call_api(
                    "/chat",
                    "POST",
                    {
                        'message': user_input,
                        'session_id': st.session_state.session_id,
                        'user_id': user_id if user_id else None,
                        'use_rag': use_rag
                    }
                )
            
            if response_data:
                # Update session ID
                st.session_state.session_id = response_data.get('session_id')
                
                # Add bot response to history
                bot_message = {
                    'role': 'assistant',
                    'content': response_data.get('response', 'No response'),
                    'timestamp': datetime.now().isoformat(),
                    'metadata': {
                        'intent': response_data.get('intent'),
                        'sentiment': response_data.get('sentiment'),
                        'state': response_data.get('state')
                    }
                }
                st.session_state.messages.append(bot_message)
                
                # Store recommendations for sidebar display
                if 'recommendations' in response_data and response_data['recommendations']:
                    st.session_state.last_recommendations = response_data['recommendations']
            
            st.rerun()
    
    with col2:
        st.subheader("📋 Information")
        
        # Display intent and state
        if st.session_state.messages:
            last_bot_message = None
            for msg in reversed(st.session_state.messages):
                if msg['role'] == 'assistant':
                    last_bot_message = msg
                    break
            
            if last_bot_message and 'metadata' in last_bot_message:
                metadata = last_bot_message['metadata']
                
                # Intent
                if metadata.get('intent'):
                    st.markdown(f"**Intent:** {metadata['intent']}")
                
                # State
                if metadata.get('state'):
                    st.markdown(f"**State:** {metadata['state']}")
                
                # Sentiment
                if metadata.get('sentiment'):
                    sentiment = metadata['sentiment']
                    st.markdown(f"**Sentiment:** {sentiment.get('sentiment', 'N/A')} ({sentiment.get('score', 0):.2f})")
        
        st.divider()
        
        # Recommendations
        if 'last_recommendations' in st.session_state:
            display_recommendations(st.session_state.last_recommendations)
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("📚 Search Knowledge Base"):
            with st.expander("Search", expanded=True):
                search_query = st.text_input("Enter search query")
                if st.button("Search") and search_query:
                    with st.spinner("Searching..."):
                        search_results = call_api(
                            "/retrieval/search",
                            "POST",
                            {'query': search_query, 'top_k': 3}
                        )
                    
                    if search_results and search_results.get('results'):
                        for result in search_results['results']:
                            st.markdown(f"**Score:** {result['score']:.3f}")
                            st.text(result['content'][:200] + "...")
                            st.divider()
        
        if st.button("🎯 Get Recommendations"):
            with st.spinner("Loading..."):
                rec_data = call_api("/recommendations", "POST", {})
            
            if rec_data and rec_data.get('recommendations'):
                display_recommendations(rec_data['recommendations'])
    
    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #6B7280; font-size: 0.875rem;'>"
        "RAG-based Intelligent Customer Service System | Powered by Qianwen API"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
