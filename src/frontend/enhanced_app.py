"""
Enhanced Streamlit Frontend - Modern and beautiful web interface for customer service chatbot.
"""

import os
import streamlit as st
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="AI Customer Service Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Enhanced Custom CSS with modern gradient design
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header with gradient */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    .subtitle {
        text-align: center;
        color: #6B7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Chat message styles */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 0.25rem;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 20%;
        border-bottom-left-radius: 0.25rem;
    }
    
    .message-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    
    .message-content {
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .message-time {
        font-size: 0.75rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }
    
    /* Badge styles */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .badge-intent {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #065F46;
    }
    
    .badge-positive {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #065F46;
    }
    
    .badge-negative {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #991B1B;
    }
    
    .badge-neutral {
        background: linear-gradient(135deg, #e0e7ff 0%, #cfd9ff 100%);
        color: #374151;
    }
    
    .badge-state {
        background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
        color: #1F2937;
    }
    
    /* Card styles */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 20%, #ff9a9e 100%);
        padding: 1.25rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: white;
        transition: transform 0.2s;
    }
    
    .recommendation-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    
    .recommendation-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .recommendation-category {
        font-size: 0.85rem;
        opacity: 0.9;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .recommendation-description {
        font-size: 0.95rem;
        margin: 0.75rem 0;
        line-height: 1.5;
    }
    
    .recommendation-score {
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Stats card */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 1rem;
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .status-online {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #065F46;
    }
    
    .status-offline {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #991B1B;
    }
    
    /* Button styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
        transform: translateY(-2px);
    }
    
    /* Input styles */
    .stTextInput > div > div > input {
        border-radius: 0.75rem;
        border: 2px solid #E5E7EB;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Sidebar styles */
    .css-1d391kg {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6B7280;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 1px solid #E5E7EB;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #E5E7EB;
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
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            st.error(f"❌ Unsupported HTTP method: {method}")
            return {}
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ API Error: {response.status_code}")
            return {}
    
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return {}
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to API. Make sure the backend is running.")
        return {}
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return {}


def display_message(role: str, content: str, metadata: Optional[Dict] = None, timestamp: str = None):
    """
    Display chat message with enhanced styling.
    
    Args:
        role: Message role (user/assistant)
        content: Message content
        metadata: Optional metadata
        timestamp: Message timestamp
    """
    css_class = "user-message" if role == "user" else "bot-message"
    icon = "👤" if role == "user" else "🤖"
    
    # Format timestamp
    time_str = ""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%I:%M %p")
        except:
            time_str = datetime.now().strftime("%I:%M %p")
    
    message_html = f"""
    <div class="chat-message {css_class}">
        <div class="message-icon">{icon}</div>
        <div class="message-content">{content}</div>
    """
    
    if metadata:
        message_html += "<div style='margin-top: 1rem;'>"
        
        if 'intent' in metadata and metadata['intent']:
            message_html += f'<span class="badge badge-intent">🎯 {metadata["intent"]}</span>'
        
        if 'sentiment' in metadata and metadata['sentiment']:
            sentiment = metadata['sentiment'].get('sentiment', 'neutral')
            score = metadata['sentiment'].get('score', 0)
            emoji = "😊" if sentiment == "positive" else "😟" if sentiment == "negative" else "😐"
            message_html += f'<span class="badge badge-{sentiment}">{emoji} {sentiment.capitalize()} ({score:.2f})</span>'
        
        if 'state' in metadata and metadata['state']:
            message_html += f'<span class="badge badge-state">📊 {metadata["state"]}</span>'
        
        message_html += "</div>"
    
    if time_str:
        message_html += f'<div class="message-time">⏰ {time_str}</div>'
    
    message_html += "</div>"
    st.markdown(message_html, unsafe_allow_html=True)


def display_recommendations(recommendations: List[Dict]):
    """Display recommendations with enhanced styling."""
    if not recommendations:
        return
    
    st.markdown("### 💡 Personalized Recommendations")
    
    for i, rec in enumerate(recommendations):
        relevance = rec.get('relevance_score', 0) * 100
        
        # Choose gradient based on category
        category = rec.get('category', '').lower()
        
        st.markdown(f"""
        <div class="recommendation-card">
            <div class="recommendation-category">📦 {rec['category']}</div>
            <div class="recommendation-title">{rec['name']}</div>
            <div class="recommendation-description">{rec['description']}</div>
            <div class="recommendation-score">⭐ Relevance: {relevance:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)


def display_statistics_chart(stats_data: Dict):
    """Display statistics with interactive charts."""
    if not stats_data:
        return
    
    # Intent distribution
    if 'intents' in stats_data:
        intents = stats_data['intents']
        if intents:
            fig = px.pie(
                values=list(intents.values()),
                names=list(intents.keys()),
                title="Intent Distribution",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment distribution
    if 'sentiments' in stats_data:
        sentiments = stats_data['sentiments']
        if sentiments:
            fig = go.Figure(data=[
                go.Bar(
                    x=list(sentiments.keys()),
                    y=list(sentiments.values()),
                    marker=dict(
                        color=['#84fab0', '#ffecd2', '#fbc2eb'],
                        line=dict(color='white', width=2)
                    )
                )
            ])
            fig.update_layout(
                title="Sentiment Analysis",
                xaxis_title="Sentiment",
                yaxis_title="Count",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)


def main():
    """Main application."""
    
    # Animated Header
    st.markdown('''
    <div class="main-header">
        🤖 AI Customer Service Assistant
    </div>
    <div class="subtitle">
        Powered by RAG Technology & Qianwen AI 🚀
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")
        
        # Check API status
        health_data = call_api("/health", "GET")
        if health_data and health_data.get('status') == 'healthy':
            st.markdown('''
            <div class="status-indicator status-online">
                🟢 System Online
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="status-indicator status-offline">
                🔴 System Offline
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User settings
        st.markdown("### 👤 User Settings")
        user_id = st.text_input("User ID", placeholder="Enter your ID (optional)")
        
        use_rag = st.checkbox(
            "🔍 Enable Knowledge Base Search",
            value=True,
            help="Use RAG for more accurate responses"
        )
        
        st.markdown("---")
        
        # Session management
        st.markdown("### 💬 Session")
        
        if 'session_id' in st.session_state and st.session_state.session_id:
            st.info(f"🔑 Session: {st.session_state.session_id[:12]}...")
            
            if st.button("🔄 New Conversation", use_container_width=True):
                call_api(f"/session/{st.session_state.session_id}", "DELETE")
                st.session_state.clear()
                st.rerun()
        else:
            st.info("✨ No active session")
            if st.button("▶️ Start New Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        
        stats_data = call_api("/statistics", "GET")
        if stats_data:
            sessions = stats_data.get('sessions', {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'''
                <div class="stats-card">
                    <div class="stats-label">Sessions</div>
                    <div class="stats-number">{sessions.get('total_sessions', 0)}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'''
                <div class="stats-card">
                    <div class="stats-label">Users</div>
                    <div class="stats-number">{sessions.get('active_users', 0)}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Show detailed stats in expander
            with st.expander("📈 Detailed Analytics"):
                display_statistics_chart(stats_data)
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🎯 Get Recommendations", use_container_width=True):
            with st.spinner("Loading recommendations..."):
                rec_data = call_api("/recommendations", "POST", {})
            
            if rec_data and rec_data.get('recommendations'):
                st.session_state.show_recommendations = rec_data['recommendations']
        
        if st.button("📚 Search Knowledge", use_container_width=True):
            st.session_state.show_search = True
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'show_search' not in st.session_state:
        st.session_state.show_search = False
    if 'show_recommendations' not in st.session_state:
        st.session_state.show_recommendations = None
    
    # Main layout
    col1, col2 = st.columns([2.5, 1.5])
    
    with col1:
        st.markdown("### 💬 Conversation")
        
        # Display conversation history
        chat_container = st.container()
        with chat_container:
            if not st.session_state.messages:
                st.markdown('''
                <div class="info-card">
                    <h4 style="margin-top: 0;">👋 Welcome!</h4>
                    <p>I'm your AI customer service assistant. How can I help you today?</p>
                    <p><strong>Try asking:</strong></p>
                    <ul>
                        <li>How do I reset my password?</li>
                        <li>Track my order</li>
                        <li>I have a billing question</li>
                        <li>Tell me about your products</li>
                    </ul>
                </div>
                ''', unsafe_allow_html=True)
            else:
                for message in st.session_state.messages:
                    display_message(
                        role=message['role'],
                        content=message['content'],
                        metadata=message.get('metadata'),
                        timestamp=message.get('timestamp')
                    )
        
        # Chat input
        user_input = st.chat_input("💭 Type your message here...")
        
        if user_input:
            # Add user message to history
            st.session_state.messages.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Call API
            with st.spinner("🤔 Thinking..."):
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
                
                # Store recommendations
                if 'recommendations' in response_data and response_data['recommendations']:
                    st.session_state.last_recommendations = response_data['recommendations']
            
            st.rerun()
    
    with col2:
        st.markdown("### 📋 Context Info")
        
        # Display current context
        if st.session_state.messages:
            last_bot_message = None
            for msg in reversed(st.session_state.messages):
                if msg['role'] == 'assistant':
                    last_bot_message = msg
                    break
            
            if last_bot_message and 'metadata' in last_bot_message:
                metadata = last_bot_message['metadata']
                
                st.markdown(f'''
                <div class="info-card">
                    <h4 style="margin-top: 0;">📊 Current Status</h4>
                ''', unsafe_allow_html=True)
                
                if metadata.get('intent'):
                    st.markdown(f"**🎯 Intent:** `{metadata['intent']}`")
                
                if metadata.get('state'):
                    st.markdown(f"**📈 State:** `{metadata['state']}`")
                
                if metadata.get('sentiment'):
                    sentiment = metadata['sentiment']
                    sentiment_emoji = "😊" if sentiment.get('sentiment') == 'positive' else "😟" if sentiment.get('sentiment') == 'negative' else "😐"
                    st.markdown(f"**{sentiment_emoji} Sentiment:** `{sentiment.get('sentiment')}` ({sentiment.get('score', 0):.2f})")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Recommendations section
        st.markdown("---")
        
        if 'last_recommendations' in st.session_state and st.session_state.last_recommendations:
            display_recommendations(st.session_state.last_recommendations)
        elif st.session_state.show_recommendations:
            display_recommendations(st.session_state.show_recommendations)
        
        # Search section
        if st.session_state.show_search:
            st.markdown("---")
            st.markdown("### 🔍 Knowledge Search")
            
            search_query = st.text_input("Search query", key="search_input")
            
            if st.button("Search", use_container_width=True) and search_query:
                with st.spinner("Searching knowledge base..."):
                    search_results = call_api(
                        "/retrieval/search",
                        "POST",
                        {'query': search_query, 'top_k': 5}
                    )
                
                if search_results and search_results.get('results'):
                    for idx, result in enumerate(search_results['results'], 1):
                        score = result.get('score', 0) * 100
                        st.markdown(f'''
                        <div class="info-card">
                            <strong>Result {idx}</strong> (Match: {score:.0f}%)<br/>
                            <small>{result.get('content', '')[:300]}...</small>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No results found")
            
            if st.button("Close Search"):
                st.session_state.show_search = False
                st.rerun()
    
    # Footer
    st.markdown('''
    <div class="footer">
        <strong>RAG-based Intelligent Customer Service System</strong><br/>
        Powered by Qianwen API 🚀 | Built with ❤️ using Streamlit & FastAPI
    </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
