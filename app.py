import streamlit as st
import json
import os
from datetime import datetime
import base64
from utils.pdf_processor import PDFProcessor
from utils.flashcard_generator import FlashcardGenerator
from utils.google_drive_sync import GoogleDriveSync
from utils.auth import GoogleAuth
from utils.error_handler import ErrorHandler
from utils.auth_manager import AuthManager
from utils.avatar_generator import AvatarGenerator
from utils.avatar_system_fixed import FixedAvatarGenerator
from database import get_db_manager

# Page configuration for PWA
st.set_page_config(
    page_title="StudyGen - PDF to Flashcards",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UX
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main container styling */
    .main {
        padding: 1rem 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit header and footer */
    header[data-testid="stHeader"] {
        height: 0px;
        display: none;
    }
    
    .stApp > footer {
        display: none;
    }
    
    /* Custom header styling */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        margin: -1rem -2rem 2rem -2rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .custom-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .custom-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Card styling */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    /* Upload area styling */
    .upload-zone {
        border: 2px dashed #667eea;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(45deg, #f8f9ff 0%, #f0f4ff 100%);
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #5a6fd8;
        background: linear-gradient(45deg, #f5f7ff 0%, #eef2ff 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        white-space: nowrap;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 48px;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Navigation button specific styling */
    .nav-button {
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* Top navigation bar styling */
    .top-nav {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        margin: -1rem -2rem 1rem -2rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
    }
    
    .top-nav-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .top-nav-right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: 2px solid white;
    }
    
    .user-info {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }
    
    .user-name {
        font-weight: 600;
        font-size: 1rem;
        margin: 0;
    }
    
    .user-email {
        font-size: 0.8rem;
        opacity: 0.8;
        margin: 0;
    }
    
    .logout-btn {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .logout-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-1px);
    }
    
    /* Flashcard styling */
    .flashcard {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        border: 1px solid #f0f0f0;
        margin: 1rem 0;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .flashcard-question {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    
    .flashcard-answer {
        font-size: 1.1rem;
        color: #4a5568;
        line-height: 1.6;
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }
    
    /* Progress bar styling */
    .progress-container {
        background: #f0f0f0;
        border-radius: 20px;
        height: 8px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 20px;
        transition: width 0.3s ease;
    }
    
    /* Stats styling */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Navigation tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background: transparent;
        border-radius: 8px;
        color: #6b7280;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .custom-header h1 {
            font-size: 2rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
        
        .upload-zone {
            padding: 2rem 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Add PWA manifest
def add_pwa_support():
    manifest_json = """
    {
        "name": "PDF Flashcard Generator",
        "short_name": "FlashCards",
        "description": "Generate flashcards from PDF documents",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#ff6b6b",
        "icons": [
            {
                "src": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyIiBoZWlnaHQ9IjE5MiIgdmlld0JveD0iMCAwIDE5MiAxOTIiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxOTIiIGhlaWdodD0iMTkyIiByeD0iMjQiIGZpbGw9IiNmZjZiNmIiLz4KPHN2ZyB4PSI0OCIgeT0iNDgiIHdpZHRoPSI5NiIgaGVpZ2h0PSI5NiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiPgo8cGF0aCBkPSJtMTQgMi0zIDMgMi41IDIuNUwxNiA1bDMgMyAyLjUtMi41TDI0IDIgMTQgMnoiLz4KPHA+
            </g>
        </svg>",
                "sizes": "192x192",
                "type": "image/svg+xml"
            }
        ]
    }
    """
    
    st.markdown(
        f'<link rel="manifest" href="data:application/json;base64,{base64.b64encode(manifest_json.encode()).decode()}">',
        unsafe_allow_html=True
    )

load_css()
add_pwa_support()

# Initialize session state
def initialize_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = []
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_card' not in st.session_state:
        st.session_state.current_card = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'study_mode' not in st.session_state:
        st.session_state.study_mode = 'flashcards'
    if 'google_drive' not in st.session_state:
        st.session_state.google_drive = None
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    if 'study_session' not in st.session_state:
        st.session_state.study_session = None
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = get_db_manager()
    if 'study_start_time' not in st.session_state:
        st.session_state.study_start_time = None
    if 'cards_studied_session' not in st.session_state:
        st.session_state.cards_studied_session = 0
    if 'questions_answered_session' not in st.session_state:
        st.session_state.questions_answered_session = 0

initialize_session_state()

# Remove auto-login - let users choose

def create_navigation():
    """Create modern navigation header"""
    st.markdown("""
    <div class="custom-header">
        <h1>🎓 StudyGen</h1>
        <p>Transform any PDF into interactive flashcards and quizzes</p>
    </div>
    """, unsafe_allow_html=True)

def create_top_navigation_bar(user_info, avatar_config, auth_manager):
    """Create top navigation bar with user info and logout"""
    
    # Create HTML structure for top navigation
    avatar_html = ""
    if avatar_config:
        avatar_generator = FixedAvatarGenerator()
        avatar_svg = avatar_generator.render_avatar_svg(avatar_config)
        import base64
        svg_bytes = avatar_svg.encode('utf-8')
        svg_b64 = base64.b64encode(svg_bytes).decode('utf-8')
        avatar_html = f'<img src="data:image/svg+xml;base64,{svg_b64}" class="user-avatar" alt="User Avatar">'
    else:
        avatar_html = '<div class="user-avatar">👤</div>'
    
    # Use columns to create the layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Left side - user info with avatar
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem; padding: 0.5rem 0;">
            {avatar_html}
            <div>
                <div style="font-weight: 600; font-size: 1rem; margin: 0; color: #333;">{user_info.get('name', 'User')}</div>
                <div style="font-size: 0.8rem; opacity: 0.7; margin: 0; color: #666;">{user_info.get('email', '')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Right side - logout button
        if st.button("🚪 Logout", key="top_logout_btn", use_container_width=True):
            auth_manager.logout_user()
            st.session_state.current_page = 'login'
            st.rerun()

def create_homepage():
    """Create an engaging homepage with features overview"""
    
    # Get user statistics from database
    db = st.session_state.db_manager
    user_stats = db.get_user_stats(st.session_state.user_id)
    
    # Display user avatar
    avatar_config = st.session_state.get('user_avatar', {})
    if avatar_config:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            avatar_generator = AvatarGenerator()
            avatar_svg = avatar_generator.render_avatar_svg(avatar_config)
            
            # Convert SVG to image to prevent code display
            import base64
            svg_bytes = avatar_svg.encode('utf-8')
            svg_b64 = base64.b64encode(svg_bytes).decode('utf-8')
            svg_data_url = f"data:image/svg+xml;base64,{svg_b64}"
            
            st.image(svg_data_url, width=120)
            st.markdown(f"<p style='text-align: center; margin-top: 0.5rem; font-weight: bold;'>Welcome back, {st.session_state.user_name}!</p>", unsafe_allow_html=True)
    
    # Gamification banner
    st.markdown("### 🏆 Your Progress")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['current_streak']}🔥</span>
            <span class="stat-label">Day Streak</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">Lv.{user_stats['level']}</span>
            <span class="stat-label">Level</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['badges_count']}🏆</span>
            <span class="stat-label">Badges</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['experience_points']}</span>
            <span class="stat-label">XP Points</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        study_hours = user_stats['total_study_time_minutes'] / 60 if user_stats['total_study_time_minutes'] > 0 else 0
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{study_hours:.1f}h</span>
            <span class="stat-label">Study Time</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Show recent badges
    if user_stats['badges_count'] > 0:
        st.markdown("---")
        st.markdown("### 🏆 Recent Badges")
        badges = db.get_user_badges(st.session_state.user_id)
        
        if badges:
            # Show up to 3 most recent badges
            recent_badges = badges[:3]
            cols = st.columns(len(recent_badges))
            
            for i, badge in enumerate(recent_badges):
                with cols[i]:
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1rem;">
                        <span style="font-size: 2rem;">{badge['icon']}</span>
                        <h4 style="margin: 0.5rem 0;">{badge['name']}</h4>
                        <p style="margin: 0; font-size: 0.9rem; color: #666;">{badge['description']}</p>
                        <small>Earned {badge['earned_at'].strftime('%b %d')}</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Study statistics
    st.markdown("---")
    st.markdown("### 📊 Study Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['documents']}</span>
            <span class="stat-label">Documents</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['flashcards']}</span>
            <span class="stat-label">Flashcards</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['questions']}</span>
            <span class="stat-label">Quiz Questions</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['study_sessions']}</span>
            <span class="stat-label">Study Sessions</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent documents section
    if user_stats['documents'] > 0:
        st.markdown("---")
        st.markdown("### 📋 Recent Documents")
        
        recent_docs = db.get_user_documents(st.session_state.user_id)[:3]  # Show last 3
        
        for doc in recent_docs:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**📄 {doc.title}**")
                st.caption(f"Created: {doc.created_at.strftime('%B %d, %Y')} • {doc.word_count:,} words")
            
            with col2:
                flashcard_count = len(db.get_document_flashcards(doc.id))
                st.metric("Cards", flashcard_count)
            
            with col3:
                if st.button(f"Study", key=f"study_{doc.id}"):
                    # Load document data
                    st.session_state.current_document = doc
                    flashcards = db.get_document_flashcards(doc.id)
                    questions = db.get_document_questions(doc.id)
                    
                    # Convert database objects to dictionaries for compatibility
                    st.session_state.flashcards = [
                        {'question': f.question, 'answer': f.answer, 'type': f.card_type} 
                        for f in flashcards
                    ]
                    st.session_state.questions = [
                        {
                            'question': q.question_text, 
                            'options': q.options, 
                            'correct_answer': q.correct_answer,
                            'type': q.question_type
                        } 
                        for q in questions
                    ]
                    st.session_state.pdf_text = doc.content_text
                    st.session_state.current_card = 0
                    st.session_state.show_answer = False
                    st.session_state.current_page = 'study'
                    st.rerun()
        
        st.markdown("---")
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📤</span>
            <h3>Upload & Process</h3>
            <p>Upload any PDF and our smart AI will extract key information to create study materials.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📤 Start with PDF Upload", key="upload_nav", use_container_width=True):
            st.session_state.current_page = 'upload'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📚</span>
            <h3>Study & Learn</h3>
            <p>Practice with flashcards or test yourself with multiple choice questions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📚 Study Mode", key="study_nav", use_container_width=True):
            st.session_state.current_page = 'study'
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">☁️</span>
            <h3>Sync & Share</h3>
            <p>Save your study materials to Google Drive and access them anywhere.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("☁️ Cloud Sync", key="sync_nav", use_container_width=True):
            st.session_state.current_page = 'sync'
            st.rerun()
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 New Study Set", type="primary", use_container_width=True):
            st.session_state.current_page = 'upload'
            st.rerun()
    
    with col2:
        if st.button("🔀 Shuffle & Study", disabled=not st.session_state.flashcards, use_container_width=True):
            if st.session_state.flashcards:
                import random
                random.shuffle(st.session_state.flashcards)
                st.session_state.current_card = 0
                st.session_state.show_answer = False
                st.session_state.current_page = 'study'
                st.rerun()
    
    with col3:
        if st.button("📊 View Progress", disabled=not (st.session_state.flashcards or st.session_state.questions), use_container_width=True):
            st.session_state.current_page = 'review'
            st.rerun()

def main():
    # Check authentication first
    auth_manager = st.session_state.get('auth_manager')
    
    # Handle welcome page
    if st.session_state.current_page == 'welcome':
        auth_manager.render_welcome_page()
        return
    
    # If not authenticated, show login page
    if not auth_manager or not auth_manager.is_authenticated():
        if st.session_state.current_page not in ['login', 'welcome']:
            st.session_state.current_page = 'login'
        
        # Show login page
        auth_manager.render_login_page()
        return
    
    # User is authenticated - show main app
    
    # Get user info and avatar
    user = auth_manager.get_current_user()
    avatar_config = st.session_state.get('user_avatar', {})
    
    # Create top navigation bar with user info and logout
    create_top_navigation_bar(user, avatar_config, auth_manager)
    
    # Add spacing
    st.markdown("---")
    
    # Create main navigation header
    create_navigation()
    
    # Navigation menu
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    with col1:
        if st.button("🏠 Home", key="home_nav", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()
    
    with col2:
        if st.button("📤 Upload", key="upload_menu", use_container_width=True):
            st.session_state.current_page = 'upload'
            st.rerun()
    
    with col3:
        if st.button("📚 Study", key="study_menu", use_container_width=True):
            st.session_state.current_page = 'study'
            st.rerun()
    
    with col4:
        if st.button("🏆 Badges", key="badges_menu", use_container_width=True):
            st.session_state.current_page = 'badges'
            st.rerun()
    
    with col5:
        if st.button("📊 Dashboard", key="dashboard_menu", use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    
    with col6:
        if st.button("👤 Profile", key="profile_menu", use_container_width=True):
            st.session_state.current_page = 'profile'
            st.rerun()
    
    with col7:
        if st.button("⚙️ Settings", key="settings_menu", use_container_width=True):
            st.session_state.current_page = 'sync'
            st.rerun()
    
    st.markdown("---")
    
    # Route to different pages (only for authenticated users)
    if st.session_state.current_page == 'login':
        # This shouldn't happen as we handle auth above, but just in case
        auth_manager.render_login_page()
    elif st.session_state.current_page == 'home':
        create_homepage()
    elif st.session_state.current_page == 'upload':
        upload_pdf_section()
    elif st.session_state.current_page == 'study':
        study_section()
    elif st.session_state.current_page == 'badges':
        badges_section()
    elif st.session_state.current_page == 'review':
        review_section()
    elif st.session_state.current_page == 'dashboard':
        dashboard_section()
    elif st.session_state.current_page == 'profile':
        profile_section()
    elif st.session_state.current_page == 'settings' or st.session_state.current_page == 'sync':
        settings_section()
    else:
        create_homepage()

def profile_section():
    """User profile page with avatar customization"""
    st.markdown("### 👤 Your Profile")
    
    # Get current user info
    auth_manager = st.session_state.auth_manager
    user = auth_manager.get_current_user()
    db = st.session_state.db_manager
    
    # Profile overview
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Current Avatar")
        # Display current avatar
        current_avatar = st.session_state.get('user_avatar', {})
        if current_avatar:
            avatar_generator = FixedAvatarGenerator()
            avatar_svg = avatar_generator.render_avatar_svg(current_avatar)
            
            # Convert SVG to data URL
            import base64
            svg_bytes = avatar_svg.encode('utf-8')
            svg_b64 = base64.b64encode(svg_bytes).decode('utf-8')
            svg_data_url = f"data:image/svg+xml;base64,{svg_b64}"
            st.image(svg_data_url, width=150)
        else:
            st.markdown("👤 No avatar set")
            
    with col2:
        st.markdown("#### Profile Information")
        st.markdown(f"**Name:** {user['name']}")
        st.markdown(f"**Email:** {user['email']}")
        
        # Get user stats
        user_stats = db.get_user_stats(st.session_state.user_id)
        st.markdown(f"**Level:** {user_stats['level']}")
        st.markdown(f"**Current Streak:** {user_stats['current_streak']} days 🔥")
        st.markdown(f"**Total XP:** {user_stats['experience_points']}")
        st.markdown(f"**Documents Created:** {user_stats['documents']}")
    
    st.markdown("---")
    
    # Avatar customization section
    st.markdown("### 🎨 Customize Your Avatar")
    st.info("Design your unique avatar that represents you throughout StudyGen!")
    
    # Initialize fixed avatar generator
    avatar_generator = FixedAvatarGenerator()
    
    # Get current avatar config or create new one
    current_config = st.session_state.get('user_avatar', {})
    if not current_config:
        current_config = avatar_generator.generate_random_avatar()
    
    # Render avatar customizer with live updates
    new_avatar_config = avatar_generator.render_avatar_customizer_with_live_update(current_config)
    
    st.markdown("---")
    
    # Save avatar button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Save Avatar Changes", type="primary", use_container_width=True):
            with st.spinner("Saving your new avatar..."):
                # Update user avatar in database
                def save_avatar():
                    db.update_user_avatar(st.session_state.user_id, new_avatar_config)
                    st.session_state.user_avatar = new_avatar_config
                    return True
                
                result = ErrorHandler.handle_database_operation(save_avatar, "avatar save")
                
                if result:
                    ErrorHandler.show_success("Avatar updated successfully!", "Your new avatar is now visible throughout the app.")
                    st.balloons()
                    
                    # Small delay to show success message
                    import time
                    time.sleep(1)
                    st.rerun()

def dashboard_section():
    """Database-driven dashboard with comprehensive statistics"""
    st.markdown("### 📊 Study Dashboard")
    
    db = st.session_state.db_manager
    user_stats = db.get_user_stats(st.session_state.user_id)
    
    # Overview stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['documents']}</span>
            <span class="stat-label">Total Documents</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['flashcards']}</span>
            <span class="stat-label">Flashcards</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['questions']}</span>
            <span class="stat-label">Questions</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['study_sessions']}</span>
            <span class="stat-label">Study Sessions</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        study_hours = user_stats['total_study_time_minutes'] / 60 if user_stats['total_study_time_minutes'] > 0 else 0
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{study_hours:.1f}h</span>
            <span class="stat-label">Study Time</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # All Documents Section
    st.markdown("### 📚 All Documents")
    
    all_docs = db.get_user_documents(st.session_state.user_id)
    
    if not all_docs:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <span class="feature-icon">📄</span>
            <h3>No Documents Yet</h3>
            <p>Upload your first PDF to get started with studying!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📤 Upload First PDF", type="primary", use_container_width=True):
            st.session_state.current_page = 'upload'
            st.rerun()
    else:
        for doc in all_docs:
            with st.expander(f"📄 {doc.title} ({doc.created_at.strftime('%b %d, %Y')})"):
                # Document details
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📝 Word Count", f"{doc.word_count:,}")
                
                with col2:
                    flashcard_count = len(db.get_document_flashcards(doc.id))
                    st.metric("📇 Flashcards", flashcard_count)
                
                with col3:
                    question_count = len(db.get_document_questions(doc.id))
                    st.metric("❓ Questions", question_count)
                
                # Document actions
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button(f"📚 Study", key=f"study_dash_{doc.id}"):
                        # Load document data
                        st.session_state.current_document = doc
                        flashcards = db.get_document_flashcards(doc.id)
                        questions = db.get_document_questions(doc.id)
                        
                        # Convert database objects to dictionaries
                        st.session_state.flashcards = [
                            {'question': f.question, 'answer': f.answer, 'type': f.card_type} 
                            for f in flashcards
                        ]
                        st.session_state.questions = [
                            {
                                'question': q.question_text, 
                                'options': q.options, 
                                'correct_answer': q.correct_answer,
                                'type': q.question_type
                            } 
                            for q in questions
                        ]
                        st.session_state.pdf_text = doc.content_text
                        st.session_state.current_card = 0
                        st.session_state.show_answer = False
                        st.session_state.current_page = 'study'
                        st.rerun()
                
                with col2:
                    if st.button(f"👁️ Preview", key=f"preview_{doc.id}"):
                        st.text_area("Content Preview", doc.content_text[:500] + "...", height=200, disabled=True)
                
                with col3:
                    if st.button(f"📊 Stats", key=f"stats_{doc.id}"):
                        flashcards = db.get_document_flashcards(doc.id)
                        if flashcards:
                            total_studied = sum(f.times_studied for f in flashcards)
                            total_correct = sum(f.times_correct for f in flashcards)
                            accuracy = (total_correct / total_studied * 100) if total_studied > 0 else 0
                            st.metric("Study Accuracy", f"{accuracy:.1f}%")
                        else:
                            st.info("No study data yet")
                
                with col4:
                    if st.button(f"🗑️ Delete", key=f"delete_{doc.id}", type="secondary"):
                        st.warning("Delete functionality would be implemented here")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload New PDF", type="primary", use_container_width=True):
            st.session_state.current_page = 'upload'
            st.rerun()
    
    with col2:
        if st.button("🎲 Random Study", disabled=user_stats['flashcards'] == 0, use_container_width=True):
            if all_docs:
                import random
                random_doc = random.choice(all_docs)
                st.session_state.current_document = random_doc
                
                flashcards = db.get_document_flashcards(random_doc.id)
                questions = db.get_document_questions(random_doc.id)
                
                st.session_state.flashcards = [
                    {'question': f.question, 'answer': f.answer, 'type': f.card_type} 
                    for f in flashcards
                ]
                st.session_state.questions = [
                    {
                        'question': q.question_text, 
                        'options': q.options, 
                        'correct_answer': q.correct_answer,
                        'type': q.question_type
                    } 
                    for q in questions
                ]
                
                import random
                random.shuffle(st.session_state.flashcards)
                st.session_state.current_card = 0
                st.session_state.show_answer = False
                st.session_state.current_page = 'study'
                st.rerun()
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = 'settings'
            st.rerun()

def upload_pdf_section():
    st.markdown("### 📤 Upload & Generate Study Materials")
    
    # Upload zone
    st.markdown("""
    <div class="upload-zone">
        <h3>📄 Drop your PDF here</h3>
        <p>Supported formats: PDF files up to 200MB</p>
        <p><strong>📊 Large File Support:</strong> Intelligent processing for files up to 200MB with progress tracking!</p>
        <p><strong>🔍 Enhanced OCR:</strong> Now extracts text from images and figures too!</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to generate flashcards from",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Validate file first
        validation = ErrorHandler.validate_file(uploaded_file)
        if not validation['valid']:
            if validation['error'] == 'file_too_large':
                ErrorHandler.display_error('file_too_large')
            elif validation['error'] == 'file_not_pdf':
                st.error("**File Type Error**")
                st.write("Please upload a PDF file only.")
                st.info("**What you can try:**")
                st.write("• Make sure your file has a .pdf extension")
                st.write("• Convert other formats (Word, PowerPoint) to PDF first")
            return
        
        # File info
        file_size = validation['size'] / (1024 * 1024)  # Convert to MB
        ErrorHandler.show_success(
            f"File uploaded successfully!", 
            f"📁 **{uploaded_file.name}** ({file_size:.1f} MB)"
        )
        
        with st.spinner("🔍 Processing PDF and extracting content (including images)..."):
            def process_pdf():
                pdf_processor = PDFProcessor()
                text = pdf_processor.extract_text(uploaded_file)
                if not text or len(text.strip()) < 100:
                    ErrorHandler.display_error('insufficient_content')
                    return None
                return text
            
            text = ErrorHandler.safe_execute(
                process_pdf,
                'pdf_upload_failed',
                fallback_value=None
            )
            
            if text is None:
                return
                
            st.session_state.pdf_text = text
            
            # Display stats
            word_count = len(text.split())
            char_count = len(text)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Words", f"{word_count:,}")
            with col2:
                st.metric("📝 Characters", f"{char_count:,}")
            with col3:
                st.metric("📄 Pages", "Auto-detected")
            
            # Content validation and selection section
            st.markdown("### 📋 Review & Select Content")
            st.info("Review the extracted content below and select which sections to include in your study materials.")
            
            # Split text into manageable chunks for selection
            chunks = split_text_into_chunks(text)
            
            # Initialize session state for chunk selection
            if 'selected_chunks' not in st.session_state:
                st.session_state.selected_chunks = list(range(len(chunks)))
            
            # Batch selection controls
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Select All", use_container_width=True, key="select_all"):
                    st.session_state.selected_chunks = list(range(len(chunks)))
                    st.rerun()
            with col2:
                if st.button("❌ Deselect All", use_container_width=True, key="deselect_all"):
                    st.session_state.selected_chunks = []
                    st.rerun()
            with col3:
                if st.button("🔄 Reset Selection", use_container_width=True, key="reset_selection"):
                    st.session_state.selected_chunks = list(range(len(chunks)))
                    st.rerun()
            
            # Display chunks with selection checkboxes
            st.markdown("#### Select Content Sections:")
            
            selected_chunks = []
            for i, chunk in enumerate(chunks):
                # Create container for each chunk
                with st.container():
                    col1, col2 = st.columns([0.1, 0.9])
                    
                    with col1:
                        is_selected = st.checkbox(
                            f"",
                            value=i in st.session_state.selected_chunks,
                            key=f"chunk_{i}",
                            label_visibility="collapsed"
                        )
                        if is_selected:
                            selected_chunks.append(i)
                    
                    with col2:
                        # Show chunk preview with styling
                        chunk_preview = chunk[:200] + "..." if len(chunk) > 200 else chunk
                        
                        # Style based on selection
                        bg_color = "#e8f5e8" if is_selected else "#f8f9fa"
                        border_color = "#28a745" if is_selected else "#dee2e6"
                        
                        st.markdown(f"""
                        <div style="
                            background-color: {bg_color};
                            border: 2px solid {border_color};
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.5rem;
                        ">
                            <strong>Section {i+1}</strong> ({len(chunk.split())} words)<br>
                            <span style="color: #6c757d; font-size: 0.9rem;">{chunk_preview}</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Update session state with current selections
            st.session_state.selected_chunks = selected_chunks
            
            # Show selection summary
            selected_count = len(selected_chunks)
            total_count = len(chunks)
            selected_words = sum(len(chunks[i].split()) for i in selected_chunks) if selected_chunks else 0
            
            st.markdown(f"""
            <div style="
                background-color: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 6px;
                padding: 1rem;
                margin: 1rem 0;
            ">
                <strong>📊 Selection Summary:</strong><br>
                Selected: {selected_count} of {total_count} sections ({selected_words:,} words)
            </div>
            """, unsafe_allow_html=True)
            
            # Update text based on selection for study material generation
            if selected_chunks:
                text = "\n\n".join(chunks[i] for i in selected_chunks)
                st.session_state.pdf_text = text
            else:
                st.warning("⚠️ No sections selected. Please select at least one section to continue.")
                text = ""
            
            # Generation options
            st.markdown("#### ⚙️ Generation Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📇 Flashcards**")
                num_flashcards = st.slider(
                    "Number of flashcards to generate",
                    min_value=5,
                    max_value=50,
                    value=15,
                    help="More flashcards = more comprehensive coverage"
                )
                
            with col2:
                st.markdown("**❓ Quiz Questions**")
                num_questions = st.slider(
                    "Number of multiple choice questions",
                    min_value=5,
                    max_value=30,
                    value=10,
                    help="Quiz questions test your understanding"
                )
            
            st.markdown("---")
            
            # Only show generation options and button if content is selected
            if text and selected_chunks:
                # Generate button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🚀 Generate Study Materials", type="primary", use_container_width=True):
                        with st.spinner("Creating your study materials..."):
                            # Save document to database first
                            file_size_bytes = len(uploaded_file.getvalue())
                        file_size_mb = file_size_bytes / (1024 * 1024)
                        
                        # Show warning for large files
                        if file_size_mb > 50:
                            ErrorHandler.show_warning(
                                f"Processing large file ({file_size_mb:.1f} MB)",
                                ['This may take several minutes', 'Please don\'t refresh the page']
                            )
                        
                        def save_document():
                            db = st.session_state.db_manager
                            return db.save_document(
                                user_id=st.session_state.user_id,
                                title=uploaded_file.name,
                                filename=uploaded_file.name,
                                file_size=file_size_bytes,
                                content_text=text
                            )
                        
                        document = ErrorHandler.safe_execute(
                            save_document,
                            'db_save_failed',
                            fallback_value=None
                        )
                        
                        if document:
                            st.session_state.current_document = document
                            generate_content_safe(text, num_flashcards, num_questions)

def generate_content_safe(text, num_flashcards, num_questions):
    """Generate flashcards and questions with enhanced error handling"""
    def generate_flashcards():
        flashcard_gen = FlashcardGenerator()
        return flashcard_gen.generate_flashcards(text, num_flashcards)
    
    def generate_questions():
        flashcard_gen = FlashcardGenerator()
        return flashcard_gen.generate_questions(text, num_questions)
    
    def save_flashcards(flashcards):
        if st.session_state.current_document:
            db = st.session_state.db_manager
            saved_count = 0
            for card in flashcards:
                try:
                    # Use execute_with_retry through the database manager
                    def save_single_card():
                        session = db.get_session()
                        try:
                            from database import Flashcard
                            flashcard = Flashcard(
                                document_id=st.session_state.current_document.id,
                                question=card['question'][:2000] if len(card['question']) > 2000 else card['question'],
                                answer=card['answer'][:5000] if len(card['answer']) > 5000 else card['answer'],
                                card_type=card.get('type', 'general')
                            )
                            session.add(flashcard)
                            session.commit()
                            return flashcard
                        finally:
                            session.close()
                    
                    db.execute_with_retry(save_single_card)
                    saved_count += 1
                except Exception as e:
                    # Log error but continue with other cards
                    st.warning(f"Could not save flashcard {saved_count + 1}: Content may be too long")
                    continue
            
            if saved_count < len(flashcards):
                st.warning(f"Saved {saved_count} out of {len(flashcards)} flashcards. Some may have been too long.")
        return True
    
    def save_questions(questions):
        if st.session_state.current_document:
            db = st.session_state.db_manager
            saved_count = 0
            for question in questions:
                try:
                    # Use execute_with_retry through the database manager
                    def save_single_question():
                        session = db.get_session()
                        try:
                            from database import Question
                            q = Question(
                                document_id=st.session_state.current_document.id,
                                question_text=question['question'][:2000] if len(question['question']) > 2000 else question['question'],
                                options=question['options'],
                                correct_answer=question['correct_answer'][:1000] if len(question['correct_answer']) > 1000 else question['correct_answer'],
                                question_type=question.get('type', 'multiple_choice')
                            )
                            session.add(q)
                            session.commit()
                            return q
                        finally:
                            session.close()
                    
                    db.execute_with_retry(save_single_question)
                    saved_count += 1
                except Exception as e:
                    # Log error but continue with other questions
                    st.warning(f"Could not save question {saved_count + 1}: Content may be too long")
                    continue
            
            if saved_count < len(questions):
                st.warning(f"Saved {saved_count} out of {len(questions)} questions. Some may have been too long.")
        return True
    
    # Generate flashcards
    with st.status("📇 Creating flashcards...", expanded=False) as status:
        flashcards = ErrorHandler.safe_execute(
            generate_flashcards,
            'generation_failed',
            fallback_value=[]
        )
        
        if flashcards:
            st.session_state.flashcards = flashcards
            ErrorHandler.safe_execute(
                lambda: save_flashcards(flashcards),
                'db_save_failed'
            )
            status.update(label="✅ Flashcards created!", state="complete")
        else:
            status.update(label="❌ Flashcard generation failed", state="error")
            return
    
    # Generate questions
    with st.status("❓ Creating quiz questions...", expanded=False) as status:
        questions = ErrorHandler.safe_execute(
            generate_questions,
            'generation_failed',
            fallback_value=[]
        )
        
        if questions:
            st.session_state.questions = questions
            ErrorHandler.safe_execute(
                lambda: save_questions(questions),
                'db_save_failed'
            )
            status.update(label="✅ Questions created!", state="complete")
        else:
            status.update(label="❌ Question generation failed", state="error")
            return
    
    # Success message and navigation
    ErrorHandler.show_success(
        "Study materials generated successfully!",
        "Ready to study! Navigate to the Study section to begin."
    )
    
    # Auto-navigate to study page
    st.session_state.current_page = 'study'
    st.rerun()

def settings_section():
    """Settings and Google Drive sync page"""
    st.markdown("### ⚙️ Settings & Cloud Sync")
    
    # Google Drive Authentication Section
    st.markdown("#### ☁️ Google Drive Integration")
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🔐</span>
            <h3>Connect to Google Drive</h3>
            <p>Save your flashcards to the cloud and access them from any device. Your study materials will be automatically synced across all your devices.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔐 Connect Google Drive", type="primary", use_container_width=True):
                try:
                    auth = GoogleAuth()
                    credentials = auth.authenticate()
                    if credentials:
                        st.session_state.authenticated = True
                        st.session_state.google_drive = GoogleDriveSync(credentials)
                        st.success("✅ Google Drive connected successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
        
        with col2:
            if st.button("📱 Continue Offline", use_container_width=True):
                st.session_state.authenticated = True
                st.info("📴 Working in offline mode - your data won't be synced.")
                st.rerun()
    
    else:
        # Connected state
        if st.session_state.google_drive:
            st.success("✅ **Google Drive Connected** - Your data is being synced automatically")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Sync Now", use_container_width=True):
                    sync_data()
            
            with col2:
                if st.button("📂 View Drive Files", use_container_width=True):
                    try:
                        files = st.session_state.google_drive.list_files()
                        if files:
                            st.markdown("**📁 Your Study Files:**")
                            for file in files[:5]:  # Show last 5 files
                                st.markdown(f"• {file['name']} ({file.get('createdTime', 'Unknown date')})")
                        else:
                            st.info("No files found in your Google Drive folder.")
                    except Exception as e:
                        st.error(f"Error accessing files: {str(e)}")
            
            with col3:
                if st.button("🔌 Disconnect", use_container_width=True):
                    st.session_state.google_drive = None
                    st.warning("Disconnected from Google Drive")
                    st.rerun()
        else:
            st.warning("📴 **Offline Mode** - Your flashcards are saved locally only")
    
    st.markdown("---")
    
    # App Preferences
    st.markdown("#### 🎨 App Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Study Mode**")
        st.session_state.study_mode = st.selectbox(
            "Default study mode",
            ["flashcards", "multiple_choice"],
            format_func=lambda x: "📇 Flashcards" if x == "flashcards" else "❓ Multiple Choice",
            key="study_mode_setting"
        )
    
    with col2:
        st.markdown("**Auto-reveal**")
        auto_reveal = st.checkbox("Automatically show answers after 5 seconds", value=False)
    
    st.markdown("---")
    
    # Data Management
    st.markdown("#### 📊 Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📇 Flashcards", len(st.session_state.flashcards))
    
    with col2:
        st.metric("❓ Questions", len(st.session_state.questions))
    
    with col3:
        words = len(st.session_state.pdf_text.split()) if st.session_state.pdf_text else 0
        st.metric("📝 Words", f"{words:,}")
    
    # Clear data options
    st.markdown("**🗑️ Clear Data**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear Flashcards", use_container_width=True):
            if st.session_state.flashcards:
                st.session_state.flashcards = []
                st.session_state.current_card = 0
                st.session_state.show_answer = False
                st.success("Flashcards cleared")
                st.rerun()
    
    with col2:
        if st.button("Clear Questions", use_container_width=True):
            if st.session_state.questions:
                st.session_state.questions = []
                st.success("Questions cleared")
                st.rerun()
    
    with col3:
        if st.button("Clear All Data", type="secondary", use_container_width=True):
            if st.session_state.flashcards or st.session_state.questions:
                st.session_state.flashcards = []
                st.session_state.questions = []
                st.session_state.pdf_text = ""
                st.session_state.current_card = 0
                st.session_state.show_answer = False
                st.warning("All data cleared")
                st.rerun()

def generate_content(text, num_flashcards, num_questions):
    with st.spinner("🤖 Generating flashcards and questions..."):
        try:
            generator = FlashcardGenerator()
            db = st.session_state.db_manager
            
            # Generate flashcards
            flashcards = generator.generate_flashcards(text, num_flashcards)
            st.session_state.flashcards = flashcards
            
            # Generate multiple choice questions
            questions = generator.generate_questions(text, num_questions)
            st.session_state.questions = questions
            
            # Save to database if we have a document
            if st.session_state.current_document:
                with st.spinner("💾 Saving to database..."):
                    # Save flashcards
                    db.save_flashcards(st.session_state.current_document.id, flashcards)
                    
                    # Save questions
                    db.save_questions(st.session_state.current_document.id, questions)
            
            # Reset study progress
            st.session_state.current_card = 0
            st.session_state.show_answer = False
            
            # Sync to Google Drive if connected
            if st.session_state.google_drive:
                sync_data()
            
            st.success(f"✅ Generated {len(flashcards)} flashcards and {len(questions)} questions!")
            st.info("📚 Ready to study! Navigate to the Study section to begin.")
            
            # Auto-navigate to study page
            st.session_state.current_page = 'study'
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error generating content: {str(e)}")

def study_section():
    if not st.session_state.flashcards and not st.session_state.questions:
        st.info("No study materials available. Please upload a PDF first.")
        return
    
    # Initialize study session tracking
    if st.session_state.study_start_time is None:
        st.session_state.study_start_time = datetime.now()
        st.session_state.cards_studied_session = 0
        st.session_state.questions_answered_session = 0
    
    # Display current session stats
    study_duration = (datetime.now() - st.session_state.study_start_time).total_seconds() / 60
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Session Time", f"{int(study_duration)} min")
    with col2:
        st.metric("Cards Studied", st.session_state.cards_studied_session)
    with col3:
        st.metric("Questions Answered", st.session_state.questions_answered_session)
    
    if st.session_state.study_mode == "flashcards":
        display_flashcards()
    else:
        display_questions()

def display_flashcards():
    if not st.session_state.flashcards:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <span class="feature-icon">📇</span>
            <h3>No Flashcards Yet</h3>
            <p>Upload a PDF first to generate your study materials.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📤 Upload PDF", type="primary", use_container_width=True):
            st.session_state.current_page = 'upload'
            st.rerun()
        return
    
    st.markdown("### 📇 Flashcard Study Mode")
    
    # Progress bar
    progress = (st.session_state.current_card + 1) / len(st.session_state.flashcards)
    progress_percent = int(progress * 100)
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_percent}%"></div>
    </div>
    <p style="text-align: center; color: #6b7280; margin: 0.5rem 0;">
        Card {st.session_state.current_card + 1} of {len(st.session_state.flashcards)} • {progress_percent}% Complete
    </p>
    """, unsafe_allow_html=True)
    
    # Current flashcard
    current_flashcard = st.session_state.flashcards[st.session_state.current_card]
    
    # Flashcard display
    st.markdown(f"""
    <div class="flashcard">
        <div class="flashcard-question">
            💭 {current_flashcard['question']}
        </div>
        {f'<div class="flashcard-answer">✅ {current_flashcard["answer"]}</div>' if st.session_state.show_answer else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_card == 0, use_container_width=True):
            st.session_state.current_card -= 1
            st.session_state.show_answer = False
            st.rerun()
    
    with col2:
        if st.button(
            "👁️ Reveal Answer" if not st.session_state.show_answer else "🙈 Hide Answer",
            type="primary",
            use_container_width=True
        ):
            st.session_state.show_answer = not st.session_state.show_answer
            # Track card as studied when answer is revealed
            if st.session_state.show_answer:
                st.session_state.cards_studied_session += 1
            st.rerun()
    
    with col3:
        if st.button("➡️ Next", disabled=st.session_state.current_card >= len(st.session_state.flashcards) - 1, use_container_width=True):
            st.session_state.current_card += 1
            st.session_state.show_answer = False
            st.rerun()
    
    # Additional controls
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔀 Shuffle Cards"):
            import random
            random.shuffle(st.session_state.flashcards)
            st.session_state.current_card = 0
            st.session_state.show_answer = False
            st.rerun()
    
    with col2:
        if st.button("⏮️ First Card"):
            st.session_state.current_card = 0
            st.session_state.show_answer = False
            st.rerun()
    
    with col3:
        if st.button("⏭️ Last Card"):
            st.session_state.current_card = len(st.session_state.flashcards) - 1
            st.session_state.show_answer = False
            st.rerun()
    
    with col4:
        if st.button("📊 Quiz Mode"):
            st.session_state.study_mode = 'multiple_choice'
            st.rerun()
    
    # End session button and progress tracking
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 End Study Session", type="secondary", use_container_width=True):
            end_study_session()
    
    with col2:
        if st.button("🏆 View Badges", use_container_width=True):
            st.session_state.current_page = 'badges'
            st.rerun()

def display_questions():
    if not st.session_state.questions:
        st.info("No questions generated yet. Please upload a PDF and generate questions.")
        return
    
    st.header("❓ Multiple Choice Quiz")
    
    for i, question in enumerate(st.session_state.questions):
        with st.expander(f"Question {i + 1}"):
            st.markdown(f"**{question['question']}**")
            
            # Create unique key for each question
            selected_option = st.radio(
                "Choose your answer:",
                question['options'],
                key=f"question_{i}",
                index=None
            )
            
            if selected_option:
                # Track question answered
                st.session_state.questions_answered_session += 1
                if selected_option == question['correct_answer']:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {question['correct_answer']}")

def review_section():
    st.header("📊 Study Review")
    
    if not st.session_state.flashcards and not st.session_state.questions:
        st.info("No study materials to review. Please upload a PDF first.")
        return
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Flashcards", len(st.session_state.flashcards))
    
    with col2:
        st.metric("Total Questions", len(st.session_state.questions))
    
    with col3:
        if st.session_state.pdf_text:
            word_count = len(st.session_state.pdf_text.split())
            st.metric("Words Processed", word_count)
    
    # Export options
    st.subheader("📥 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.flashcards and st.button("Download Flashcards (JSON)"):
            json_data = json.dumps(st.session_state.flashcards, indent=2)
            st.download_button(
                label="Download Flashcards",
                data=json_data,
                file_name=f"flashcards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.session_state.questions and st.button("Download Questions (JSON)"):
            json_data = json.dumps(st.session_state.questions, indent=2)
            st.download_button(
                label="Download Questions",
                data=json_data,
                file_name=f"questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Display all flashcards
    if st.session_state.flashcards:
        st.subheader("📇 All Flashcards")
        for i, card in enumerate(st.session_state.flashcards):
            with st.expander(f"Flashcard {i + 1}"):
                st.markdown(f"**Q:** {card['question']}")
                st.markdown(f"**A:** {card['answer']}")
    
    # Display all questions
    if st.session_state.questions:
        st.subheader("❓ All Questions")
        for i, question in enumerate(st.session_state.questions):
            with st.expander(f"Question {i + 1}"):
                st.markdown(f"**Q:** {question['question']}")
                for j, option in enumerate(question['options']):
                    if option == question['correct_answer']:
                        st.markdown(f"**{chr(65+j)}.** {option} ✅")
                    else:
                        st.markdown(f"{chr(65+j)}. {option}")

def badges_section():
    """Display user badges and gamification achievements"""
    st.markdown("### 🏆 Your Badges & Achievements")
    
    db = st.session_state.db_manager
    user_stats = db.get_user_stats(st.session_state.user_id)
    badges = db.get_user_badges(st.session_state.user_id)
    
    # Progress overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">Lv.{user_stats['level']}</span>
            <span class="stat-label">Current Level</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['experience_points']}</span>
            <span class="stat-label">Total XP</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['current_streak']}🔥</span>
            <span class="stat-label">Current Streak</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <span class="stat-number">{user_stats['longest_streak']}</span>
            <span class="stat-label">Best Streak</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Level progress bar
    st.markdown("---")
    st.markdown("### 📈 Level Progress")
    
    current_level_xp = (user_stats['level'] - 1) * 100
    next_level_xp = user_stats['level'] * 100
    progress = (user_stats['experience_points'] - current_level_xp) / 100
    
    st.progress(progress)
    st.markdown(f"**{user_stats['experience_points'] - current_level_xp} / 100 XP** to Level {user_stats['level'] + 1}")
    
    # Display badges
    st.markdown("---")
    if badges:
        st.markdown(f"### 🎖️ Earned Badges ({len(badges)})")
        
        # Group badges by type
        streak_badges = [b for b in badges if b['type'] == 'streak']
        level_badges = [b for b in badges if b['type'] == 'level']
        activity_badges = [b for b in badges if b['type'] == 'activity']
        
        # Streak badges
        if streak_badges:
            st.markdown("#### 🔥 Streak Badges")
            cols = st.columns(min(4, len(streak_badges)))
            for i, badge in enumerate(streak_badges):
                with cols[i % 4]:
                    featured = "⭐ " if badge['is_featured'] else ""
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1rem; {'' if not badge['is_featured'] else 'border: 2px solid #FFD700;'}">
                        <span style="font-size: 2.5rem;">{badge['icon']}</span>
                        <h4 style="margin: 0.5rem 0;">{featured}{badge['name']}</h4>
                        <p style="margin: 0; font-size: 0.9rem; color: #666;">{badge['description']}</p>
                        <small>Earned {badge['earned_at'].strftime('%b %d, %Y')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Level badges  
        if level_badges:
            st.markdown("#### ⭐ Level Badges")
            cols = st.columns(min(4, len(level_badges)))
            for i, badge in enumerate(level_badges):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1rem;">
                        <span style="font-size: 2.5rem;">{badge['icon']}</span>
                        <h4 style="margin: 0.5rem 0;">{badge['name']}</h4>
                        <p style="margin: 0; font-size: 0.9rem; color: #666;">{badge['description']}</p>
                        <small>Earned {badge['earned_at'].strftime('%b %d, %Y')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Activity badges
        if activity_badges:
            st.markdown("#### 🎯 Activity Badges")
            cols = st.columns(min(4, len(activity_badges)))
            for i, badge in enumerate(activity_badges):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="feature-card" style="text-align: center; padding: 1rem;">
                        <span style="font-size: 2.5rem;">{badge['icon']}</span>
                        <h4 style="margin: 0.5rem 0;">{badge['name']}</h4>
                        <p style="margin: 0; font-size: 0.9rem; color: #666;">{badge['description']}</p>
                        <small>Earned {badge['earned_at'].strftime('%b %d, %Y')}</small>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown("### 🎯 No Badges Yet!")
        st.markdown("""
        <div class="feature-card" style="text-align: center; padding: 2rem;">
            <span class="feature-icon">🏆</span>
            <h3>Start Your Journey!</h3>
            <p>Study regularly to earn your first badges. Build a streak, reach new levels, and unlock achievements!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📚 Start Studying", type="primary", use_container_width=True):
            st.session_state.current_page = 'study'
            st.rerun()
    
    # Streak calendar view
    if user_stats['current_streak'] > 0:
        st.markdown("---")
        st.markdown("### 📅 Study Streak Calendar")
        streak_data = db.get_user_streak_data(st.session_state.user_id, days=14)
        
        if streak_data:
            cols = st.columns(min(7, len(streak_data)))
            for i, day in enumerate(streak_data):
                with cols[i % 7]:
                    study_indicator = "🔥" if day['study_minutes'] > 0 else "⭕"
                    st.markdown(f"""
                    <div style="text-align: center; padding: 0.5rem; border: 1px solid #ddd; border-radius: 8px; margin: 0.2rem;">
                        <div style="font-size: 1.5rem;">{study_indicator}</div>
                        <div style="font-size: 0.8rem;">{day['date'].strftime('%m/%d')}</div>
                        <div style="font-size: 0.7rem; color: #666;">{day['study_minutes']}m</div>
                    </div>
                    """, unsafe_allow_html=True)

def end_study_session():
    """End current study session and update gamification progress"""
    if st.session_state.study_start_time is None:
        return
    
    # Calculate session duration
    session_duration = (datetime.now() - st.session_state.study_start_time).total_seconds() / 60
    
    # Update gamification stats
    db = st.session_state.db_manager
    result = db.update_user_gamification(
        user_id=st.session_state.user_id,
        study_minutes=int(session_duration),
        cards_studied=st.session_state.cards_studied_session,
        questions_answered=st.session_state.questions_answered_session
    )
    
    # Show achievements
    if result:
        st.success(f"🎉 Study session complete! Earned {result['xp_gained']} XP!")
        
        if result['level_up']:
            st.balloons()
            st.success(f"🎊 LEVEL UP! You reached Level {result['new_level']}!")
        
        if result['new_badges']:
            st.success("🏆 New badges earned:")
            for badge in result['new_badges']:
                st.success(f"{badge['icon']} {badge['name']}: {badge['description']}")
        
        if result['current_streak'] > 1:
            streak_emoji = "🔥" if result['current_streak'] < 7 else "🚀" if result['current_streak'] < 30 else "👑"
            st.success(f"{streak_emoji} Current streak: {result['current_streak']} days!")
    
    # Reset session tracking
    st.session_state.study_start_time = None
    st.session_state.cards_studied_session = 0
    st.session_state.questions_answered_session = 0
    
    st.rerun()

def split_text_into_chunks(text, chunk_size=1000):
    """Split text into manageable chunks for content selection"""
    if not text:
        return []
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk size, start new chunk
        if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Filter out very small chunks (less than 50 characters)
    chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
    
    return chunks

def sync_data():
    """Sync data to Google Drive with enhanced error handling"""
    if not st.session_state.google_drive:
        ErrorHandler.show_warning("Google Drive not connected", 
                                ['Connect to Google Drive first in Settings'])
        return
    
    with st.spinner("Syncing with Google Drive..."):
        try:
            # Create data to sync
            data = {
                'flashcards': st.session_state.flashcards,
                'questions': st.session_state.questions,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Upload to Google Drive
            st.session_state.google_drive.save_data(data)
            ErrorHandler.show_success("Data synced successfully!", 
                                    "Your study materials are now backed up to Google Drive")
        except Exception as e:
            ErrorHandler.display_error('drive_sync_failed', str(e))

# Initialize session state variables
def init_session_state():
    """Initialize all session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "welcome"
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = []
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    if 'google_drive' not in st.session_state:
        st.session_state.google_drive = None
    if 'study_start_time' not in st.session_state:
        st.session_state.study_start_time = None
    if 'cards_studied_session' not in st.session_state:
        st.session_state.cards_studied_session = 0
    if 'questions_answered_session' not in st.session_state:
        st.session_state.questions_answered_session = 0

# Initialize the application
def init_app():
    """Initialize the application"""
    try:
        # Initialize session state first
        init_session_state()
        
        # Initialize database manager
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = get_db_manager()
        
        # Initialize authentication manager
        if 'auth_manager' not in st.session_state:
            st.session_state.auth_manager = AuthManager(st.session_state.db_manager)
        
        # Run main application
        main()
        
    except Exception as e:
        st.error(f"Application initialization failed: {str(e)}")
        st.info("Please refresh the page to try again.")

# Run the application
init_app()
