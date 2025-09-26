import streamlit as st
import requests
import json
from typing import List, Dict, Optional
import time
from io import BytesIO
import warnings
import os
from datetime import datetime
from pathlib import Path


# Suppress specific warnings
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")

# Get parent of the current working directory
parent_dir = Path(os.getcwd())

# Get today's date as a string, e.g., "2025-09-26"
date_str = datetime.today().strftime("%Y-%m-%d")
pdf_dir = parent_dir / f"pdfs_{date_str}"

# Create the directory if not exists
pdf_dir.mkdir(parents=True, exist_ok=True)

# Use pdf_dir as your PDF storage directory (as string)
PDF_STORAGE_DIR = str(pdf_dir)

# Ensure the directory exists
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)

# Configure page
st.set_page_config(
    page_title="RAG AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
INGESTION_ENDPOINT = f"{API_BASE_URL}/ingestion"
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"

# Custom CSS for AI-themed dark interface
st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Sidebar styling */
    .stSidebar {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f23 100%);
    }
    
    .stSidebar .stMarkdown {
        color: #e0e6ed;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 18px 18px 5px 18px;
        margin: 1rem 0;
        margin-left: 3rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
    }
    
    .user-message::before {
        content: "You";
        position: absolute;
        top: -20px;
        right: 1rem;
        background: rgba(102, 126, 234, 0.8);
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        color: #e2e8f0;
        padding: 1.2rem;
        border-radius: 18px 18px 18px 5px;
        margin: 1rem 0;
        margin-right: 3rem;
        box-shadow: 0 4px 15px rgba(45, 55, 72, 0.4);
        border: 1px solid rgba(102, 126, 234, 0.2);
        position: relative;
    }
    
    .assistant-message::before {
        content: "🤖 AI Assistant";
        position: absolute;
        top: -20px;
        left: 1rem;
        background: rgba(45, 55, 72, 0.8);
        color: #e2e8f0;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(45, 55, 72, 0.8) !important;
        color: white !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 25px !important;
        padding: 12px 20px !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: rgba(45, 55, 72, 0.6) !important;
        border: 2px dashed rgba(102, 126, 234, 0.5) !important;
        border-radius: 15px !important;
        padding: 2rem !important;
    }
    
    .stFileUploader label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    /* Success/Error messages */
    .success-message {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
        animation: slideIn 0.3s ease;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(245, 101, 101, 0.3);
        animation: slideIn 0.3s ease;
    }
    
    /* Sidebar sections */
    .sidebar-section {
        background: rgba(45, 55, 72, 0.3);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .sidebar-section h3 {
        color: #667eea;
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .chat-history-item {
        background: rgba(102, 126, 234, 0.1);
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #667eea;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #e2e8f0;
        font-size: 0.9rem;
    }
    
    .chat-history-item:hover {
        background: rgba(102, 126, 234, 0.2);
        transform: translateX(5px);
    }
    
    .document-item {
        background: rgba(118, 75, 162, 0.1);
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 3px solid #764ba2;
        color: #e2e8f0;
        font-size: 0.9rem;
    }
    
    /* Fixed Chat input area - removed extra padding/margin */
    .chat-input-area {
        margin-top: 1rem;
        padding: 0;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

class DocumentIngestion:
    """Handle document ingestion functionality"""
    
    @staticmethod
    def upload_pdf(file) -> tuple[bool, str]:
        """Save PDF locally and send path to ingestion endpoint"""
        try:
            # Save PDF to local directory
            file_path = os.path.join(PDF_STORAGE_DIR, file.name)
            
            # Write the uploaded file to local storage
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            
            print(f"PDF saved to: {file_path}")  # Debug info
            
            # Send the local file path to ingestion endpoint
            data = {
                "URI": file_path,
                "source": "file"
            }
            
            print(f"Sending ingestion request: {data}")  # Debug info
            
            response = requests.post(
                INGESTION_ENDPOINT, 
                json=data,
                headers={
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                timeout=1000
            )
            
            print(f"Upload PDF Response Status: {response.status_code}")
            print(f"Upload PDF Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                success = response_data.get("status") == "success"
                return success, file.name
            
            return False, f"API Error: {response.status_code}"
            
        except Exception as e:
            error_msg = f"Error uploading PDF: {str(e)}"
            print(f"PDF Upload Exception: {error_msg}")
            return False, error_msg
    
    @staticmethod
    def ingest_url(url: str) -> tuple[bool, str]:
        """Send URL to ingestion endpoint"""
        try:
            print(f"=========={url}=================")
            data = {
                "URI": url,
                "source": "url"
            }
            
            print(f"Sending URL ingestion request: {data}")  # Debug info
            
            response = requests.post(
                INGESTION_ENDPOINT, 
                json=data,
                headers={
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                timeout=1000
            )
            
            print(f"URL Ingestion Response Status: {response.status_code}")
            print(f"URL Ingestion Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                success = response_data.get("status") == "success"
                return success, url
            
            return False, f"API Error: {response.status_code}"
            
        except Exception as e:
            error_msg = f"Error ingesting URL: {str(e)}"
            print(f"URL Ingestion Exception: {error_msg}")
            return False, error_msg

class ChatManager:
    """Handle chat functionality"""
    
    @staticmethod
    def send_message(message: str) -> Optional[str]:
        """Send message to chat endpoint and get response"""
        try:
            payload = {
                "question": message
            }
            
            print(f"Sending chat request: {payload}")  # Debug info
            
            response = requests.post(
                CHAT_ENDPOINT, 
                json=payload,
                headers={
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                timeout=1000
            )
            
            print(f"Chat Response Status: {response.status_code}")
            print(f"Chat Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get("answer", "No answer received")
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            error_msg = f"Error sending message: {str(e)}"
            print(f"Chat Exception: {error_msg}")
            return error_msg

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = []

def render_sidebar():
    """Render the enhanced sidebar with document management and history"""
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📄 Document Upload")
        
        # PDF Upload Section
        st.markdown("**Upload PDF:**")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to add to your knowledge base",
            key="pdf_uploader"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {uploaded_file.name}")
            with col2:
                if st.button("Upload", key="upload_pdf_btn", help="Upload PDF"):
                    with st.spinner("Processing PDF..."):
                        success, result = DocumentIngestion.upload_pdf(uploaded_file)
                        if success:
                            st.session_state.uploaded_documents.append({
                                "name": result,
                                "type": "PDF",
                                "uploaded_at": datetime.now().strftime("%H:%M")
                            })
                            st.success("✅ PDF uploaded successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ Upload failed: {result}")
        
        st.markdown("---")
        
        # URL Input Section
        st.markdown("**Add URL:**")
        url_input = st.text_input(
            "Enter URL",
            placeholder="https://example.com/article",
            help="Enter a URL to scrape and add to your knowledge base",
            key="url_input"
        )
        
        if url_input and st.button("Ingest URL", key="ingest_url_btn"):
            with st.spinner("Processing URL..."):
                success, result = DocumentIngestion.ingest_url(url_input)
                if success:
                    st.session_state.uploaded_documents.append({
                        "name": result,
                        "type": "URL",
                        "uploaded_at": datetime.now().strftime("%H:%M")
                    })
                    st.success("✅ URL ingested successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Ingestion failed: {result}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Uploaded Documents Section
        if st.session_state.uploaded_documents:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### 📚 Your Documents")
            for doc in st.session_state.uploaded_documents[-5:]:  # Show last 5 documents
                doc_icon = "📄" if doc["type"] == "PDF" else "🔗"
                st.markdown(
                    f'<div class="document-item">{doc_icon} {doc["name"][:30]}{"..." if len(doc["name"]) > 30 else ""}<br><small>{doc["uploaded_at"]}</small></div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat History Section
        if st.session_state.chat_history:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### 💬 Recent Chats")
            for chat in st.session_state.chat_history[-5:]:  # Show last 5 chats
                preview = chat[:50] + "..." if len(chat) > 50 else chat
                st.markdown(
                    f'<div class="chat-history-item">{preview}</div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

def render_chat_message(role: str, content: str):
    """Render a chat message with proper styling"""
    if role == "user":
        st.markdown(
            f'<div class="user-message">{content}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="assistant-message">{content}</div>',
            unsafe_allow_html=True
        )

def render_chat_interface():
    """Render the main chat interface"""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        render_chat_message(message["role"], message["content"])
    
    # Chat input area - simplified structure
    st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
    
    # Create form to handle enter key submission
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask me anything about your documents...",
                label_visibility="collapsed",
                key="user_message"
            )
        
        with col2:
            send_button = st.form_submit_button("Send 🚀")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle message sending
    if send_button and user_input.strip():
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        
        # Add to chat history if not already present
        if user_input.strip() not in st.session_state.chat_history:
            st.session_state.chat_history.append(user_input.strip())
        
        # Show a spinner while processing
        with st.spinner("🤖 AI is thinking..."):
            # Send to chat endpoint
            response = ChatManager.send_message(user_input.strip())
            
            if response:
                # Add AI response to messages
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                # Add error message if no response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "I apologize, but I encountered an error processing your request. Please try again."
                })
        
        # Force rerun to show new messages
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Header
    st.markdown('''
        <div class="main-header">
            <h1>🤖 RAG AI Assistant</h1>
            <p>Your intelligent document companion powered by advanced AI</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Chat interface
    render_chat_interface()
    
    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; color: #e2e8f0; margin: 2rem 0; padding: 2rem; background: rgba(45, 55, 72, 0.3); border-radius: 15px; border: 1px solid rgba(102, 126, 234, 0.2);">
            <h3 style="color: #667eea; margin-bottom: 1rem;">🚀 Welcome to your AI Assistant!</h3>
            <p><strong>Getting Started:</strong></p>
            <p>📄 Upload PDFs or add URLs using the sidebar</p>
            <p>💬 Ask questions about your documents</p>
            <p>🧠 Get intelligent, context-aware responses</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()