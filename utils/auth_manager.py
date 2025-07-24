import streamlit as st
import hashlib
import secrets
from datetime import datetime, timezone
from utils.error_handler import ErrorHandler
from utils.avatar_system_fixed import FixedAvatarGenerator

class AuthManager:
    """Handles user authentication and session management"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.avatar_generator = FixedAvatarGenerator()
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Combine password and salt
        salted_password = password + salt
        
        # Hash the salted password
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        
        return hashed, salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash"""
        new_hash, _ = self.hash_password(password, salt)
        return new_hash == hashed_password
    
    def register_user(self, email: str, password: str, name: str) -> dict:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = self.db_manager.get_user_by_email(email)
            if existing_user:
                return {'success': False, 'error': 'User already exists'}
            
            # Hash the password
            hashed_password, salt = self.hash_password(password)
            
            # Create user in database
            user_data = {
                'email': email,
                'name': name,
                'password_hash': hashed_password,
                'salt': salt,
                'preferences': {'study_mode': 'flashcards', 'auto_reveal': False}
            }
            
            user = self.db_manager.create_user_with_password(user_data)
            
            return {'success': True, 'user': user}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def login_user(self, email: str, password: str) -> dict:
        """Authenticate user login"""
        try:
            # Get user from database
            user = self.db_manager.get_user_by_email(email)
            if not user:
                return {'success': False, 'error': 'Invalid email or password'}
            
            # Verify password
            if not self.verify_password(password, user['password_hash'], user['salt']):
                return {'success': False, 'error': 'Invalid email or password'}
            
            # Update last login
            self.db_manager.update_user_last_active(user['id'])
            
            return {'success': True, 'user': user}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def logout_user(self):
        """Clear user session"""
        session_keys = ['user_id', 'user_email', 'user_name', 'current_document', 
                       'flashcards', 'questions', 'selected_chunks', 'pdf_text']
        
        for key in session_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return 'user_id' in st.session_state and st.session_state.user_id is not None
    
    def get_current_user(self) -> dict:
        """Get current authenticated user info"""
        if not self.is_authenticated():
            return None
        
        return {
            'id': st.session_state.user_id,
            'email': st.session_state.get('user_email', ''),
            'name': st.session_state.get('user_name', '')
        }
    
    def require_auth(self):
        """Redirect to login if not authenticated"""
        if not self.is_authenticated():
            st.session_state.current_page = "🔐 Login"
            st.rerun()
    
    def render_login_page(self):
        """Render the gamified login/register interface"""
        # Header with animation
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3rem;
                margin-bottom: 0.5rem;
            ">🎓 StudyGen</h1>
            <p style="font-size: 1.2rem; color: #666; margin: 0;">
                Level up your learning with AI-powered study materials!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tab selection for Login/Register/Avatar Creation
        if 'registration_step' not in st.session_state:
            st.session_state.registration_step = 'login'
        
        if st.session_state.registration_step == 'avatar_creation':
            self._render_avatar_creation()
        else:
            login_tab, register_tab = st.tabs(["🚀 Login", "✨ Create Account"])
            
            with login_tab:
                self._render_login_form()
            
            with register_tab:
                self._render_register_form()
    
    def _render_login_form(self):
        """Render login form"""
        st.markdown("### Welcome Back!")
        st.info("Log in to access your study materials and track your progress.")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                login_button = st.form_submit_button("🚀 Log In", use_container_width=True, type="primary")
            
            if login_button:
                if not email or not password:
                    st.error("Please enter both email and password")
                    return
                
                with st.spinner("Logging in..."):
                    result = self.login_user(email, password)
                    
                    if result['success']:
                        # Set session state
                        user = result['user']
                        st.session_state.user_id = user['id']
                        st.session_state.user_email = user['email']
                        st.session_state.user_name = user['name']
                        st.session_state.user_avatar = user.get('avatar_config', {})
                        
                        st.success(f"Welcome back, {user['name']}!")
                        st.session_state.current_page = "home"
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result['error']}")
        
        # Demo mode option
        st.markdown("---")
        st.markdown("### 🎯 Try Demo Mode")
        st.info("Want to try the app without creating an account? Use demo mode with limited features.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📋 Continue as Demo User", use_container_width=True):
                # Create demo user session
                demo_user = self.db_manager.get_or_create_user(
                    email="demo@studygen.app",
                    name="Demo User"
                )
                st.session_state.user_id = demo_user['id']
                st.session_state.user_email = demo_user['email']
                st.session_state.user_name = demo_user['name']
                st.session_state.user_avatar = demo_user.get('avatar_config', {})
                st.session_state.current_page = "home"
                st.rerun()
    
    def _render_register_form(self):
        """Render gamified registration form"""
        st.markdown("### 🌟 Join the Learning Adventure!")
        st.info("Create your account and unlock personalized study experiences with gamification!")
        
        with st.form("register_form"):
            name = st.text_input("🏷️ Choose Your Study Name", placeholder="What should we call you?")
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
            password = st.text_input("🔒 Create Password", type="password", help="Make it strong to protect your progress!")
            confirm_password = st.text_input("🔒 Confirm Password", type="password")
            
            # Add some gamification preview
            st.markdown("### 🎮 What You'll Get:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("🏆 **Badges & Achievements**")
            with col2:
                st.markdown("📊 **Progress Tracking**")
            with col3:
                st.markdown("🎨 **Custom Avatar**")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                register_button = st.form_submit_button("🚀 Start Your Journey", use_container_width=True, type="primary")
            
            if register_button:
                # Validation
                if not name or not email or not password:
                    st.error("Please fill in all fields to begin your adventure!")
                    return
                
                if password != confirm_password:
                    st.error("Passwords don't match - please try again!")
                    return
                
                if len(password) < 6:
                    st.error("Password must be at least 6 characters for security!")
                    return
                
                # Store registration data and move to avatar creation
                st.session_state.pending_registration = {
                    'name': name,
                    'email': email,
                    'password': password
                }
                st.session_state.registration_step = 'avatar_creation'
                st.rerun()

    def _render_avatar_creation(self):
        """Render avatar creation interface for new users"""
        # Add CSS for step transitions
        st.markdown("""
        <style>
        .avatar-creation-step {
            animation: stepFadeIn 0.6s ease-in-out;
            transition: all 0.3s ease;
        }
        
        .step-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            animation: headerSlideIn 0.8s ease-out;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .step-description {
            background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            color: #4a5568;
            margin-bottom: 2rem;
            animation: descriptionFadeIn 1s ease-in-out;
            border-left: 4px solid #667eea;
        }
        
        .action-buttons {
            animation: buttonsSlideUp 1.2s ease-out;
        }
        
        @keyframes stepFadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes headerSlideIn {
            from { opacity: 0; transform: scale(0.9) translateY(-10px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }
        
        @keyframes descriptionFadeIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes buttonsSlideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="avatar-creation-step">', unsafe_allow_html=True)
        st.markdown('<div class="step-header"><h1 style="margin: 0;">🎨 Create Your Avatar!</h1></div>', unsafe_allow_html=True)
        st.markdown('<div class="step-description">🌟 Design your unique study companion to represent you in StudyGen! This avatar will appear throughout your learning journey.</div>', unsafe_allow_html=True)
        
        # Initialize avatar config if not exists
        if 'temp_avatar_config' not in st.session_state:
            st.session_state.temp_avatar_config = self.avatar_generator.generate_random_avatar()
        
        # Clear any existing avatar customizer state to prevent conflicts
        keys_to_clear = [key for key in st.session_state.keys() if 'avatar_customizer' in key]
        for key in keys_to_clear:
            del st.session_state[key]
        
        # Render avatar customizer with live preview
        new_config = self.avatar_generator.render_avatar_customizer(st.session_state.temp_avatar_config)
        
        # Update the temp config
        st.session_state.temp_avatar_config = new_config
        
        st.markdown("---")
        
        # Action buttons with animation
        st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Back to Registration", use_container_width=True):
                st.session_state.registration_step = 'login'
                if 'pending_registration' in st.session_state:
                    del st.session_state.pending_registration
                if 'temp_avatar_config' in st.session_state:
                    del st.session_state.temp_avatar_config
                # Clear avatar customizer state
                keys_to_clear = [key for key in st.session_state.keys() if 'avatar_customizer' in key]
                for key in keys_to_clear:
                    del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("🚀 Complete Registration", use_container_width=True, type="primary"):
                if 'pending_registration' in st.session_state:
                    # Get registration data
                    reg_data = st.session_state.pending_registration
                    
                    with st.spinner("Creating your account and avatar..."):
                        # Hash password
                        password_hash, salt = self.hash_password(reg_data['password'])
                        
                        # Create user with avatar
                        try:
                            user_data = {
                                'email': reg_data['email'],
                                'name': reg_data['name'],
                                'password_hash': password_hash,
                                'salt': salt,
                                'avatar_config': st.session_state.temp_avatar_config
                            }
                            
                            user = self.db_manager.create_user_with_password(user_data)
                            
                            if user:
                                # Login the user
                                st.session_state.user_id = user['id']
                                st.session_state.user_email = user['email']
                                st.session_state.user_name = user['name']
                                st.session_state.user_avatar = user['avatar_config']
                                
                                # Clear temporary data
                                del st.session_state.pending_registration
                                del st.session_state.temp_avatar_config
                                # Clear avatar customizer state
                                keys_to_clear = [key for key in st.session_state.keys() if 'avatar_customizer' in key]
                                for key in keys_to_clear:
                                    del st.session_state[key]
                                st.session_state.registration_step = 'login'
                                
                                # Show success and redirect
                                st.success("🎉 Welcome to StudyGen! Your avatar looks amazing!")
                                st.balloons()
                                st.session_state.current_page = "home"
                                st.rerun()
                            else:
                                st.error("Failed to create account. Please try again.")
                        except Exception as e:
                            st.error(f"Registration failed: {str(e)}")
        
        with col3:
            if st.button("🎲 New Random Avatar", use_container_width=True):
                with st.spinner('Generating new avatar...'):
                    import time
                    time.sleep(0.2)  # Brief animation pause
                    st.session_state.temp_avatar_config = self.avatar_generator.generate_random_avatar()
                    # Clear avatar customizer state
                    keys_to_clear = [key for key in st.session_state.keys() if 'avatar_customizer' in key]
                    for key in keys_to_clear:
                        del st.session_state[key]
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close action-buttons div
        st.markdown('</div>', unsafe_allow_html=True)  # Close avatar-creation-step div
    
    def render_welcome_page(self):
        """Render welcome page with option to try app or create account"""
        
        # Apply custom CSS for welcome page
        st.markdown("""
        <style>
        .welcome-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 3rem;
            text-align: center;
        }
        
        .welcome-header {
            margin-bottom: 3rem;
        }
        
        .welcome-header h1 {
            color: #667eea;
            font-size: 3rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        .welcome-header p {
            color: #6b7280;
            font-size: 1.2rem;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }
        
        .choice-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 2px solid transparent;
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        
        .choice-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
        }
        
        .choice-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .choice-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 1rem;
        }
        
        .choice-description {
            color: #6b7280;
            line-height: 1.5;
            margin-bottom: 1.5rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Welcome header
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-header">
                <h1>🎓 Welcome to StudyGen</h1>
                <p>Transform any PDF into interactive flashcards and quizzes. Choose how you'd like to get started!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Choice options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="choice-card">
                <div class="choice-icon">🚀</div>
                <div class="choice-title">Try the App</div>
                <div class="choice-description">
                    Jump right in with a demo account. Perfect for exploring features without commitment.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Try Demo", use_container_width=True, key="demo_btn"):
                self.create_demo_user()
                st.session_state.current_page = 'home'
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="choice-card">
                <div class="choice-icon">👤</div>
                <div class="choice-title">Create Account</div>
                <div class="choice-description">
                    Sign up to save your progress, sync across devices, and unlock all features.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("👤 Create Account", use_container_width=True, key="signup_btn"):
                st.session_state.current_page = 'login'
                st.rerun()
        
        # Features preview
        st.markdown("---")
        st.markdown("### ✨ What You Can Do")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📄 PDF Processing**
            - Upload any PDF document
            - Extract text with OCR support
            - Handle large files up to 200MB
            """)
        
        with col2:
            st.markdown("""
            **🎯 Smart Study Tools**
            - Auto-generate flashcards
            - Create quiz questions
            - Track your progress
            """)
        
        with col3:
            st.markdown("""
            **🏆 Gamification**
            - Earn XP and level up
            - Unlock badges and achievements
            - Build study streaks
            """)
    
    def create_demo_user(self):
        """Create a demo user for trying the app"""
        try:
            # Create or get demo user
            db = st.session_state.db_manager
            user_data = db.get_or_create_user(
                email="demo@studygen.app", 
                name="Demo User"
            )
            
            # Set session state
            st.session_state.user_id = user_data['id']
            st.session_state.user_email = user_data['email']
            st.session_state.user_name = user_data['name']
            st.session_state.authenticated = True
            
            # Generate random avatar for demo user
            avatar_config = self.avatar_generator.generate_random_avatar()
            st.session_state.user_avatar = avatar_config
            
            st.success("Welcome to StudyGen! You're now using a demo account.")
            
        except Exception as e:
            from utils.error_handler import ErrorHandler
            ErrorHandler.display_error('demo_creation_failed', str(e))

    def render_user_menu(self):
        """Render user menu in sidebar"""
        if not self.is_authenticated():
            return
        
        user = self.get_current_user()
        
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 {user['name']}**")
            st.caption(user['email'])
            
            if st.button("🚪 Logout", use_container_width=True):
                self.logout_user()
                st.session_state.current_page = "🔐 Login"
                st.rerun()