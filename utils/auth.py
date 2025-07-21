import os
import json
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

class GoogleAuth:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/drive.file']
        self.credentials_info = self._get_credentials_info()
    
    def _get_credentials_info(self):
        """Get Google API credentials from environment or default"""
        # Try to get from environment variables first
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if client_id and client_secret:
            return {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8080/callback"]
                }
            }
        else:
            # Fallback credentials for demo purposes
            st.warning("Google API credentials not found. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
            return {
                "web": {
                    "client_id": "your-client-id.googleusercontent.com",
                    "client_secret": "your-client-secret",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8080/callback"]
                }
            }
    
    def authenticate(self):
        """Authenticate with Google and return credentials"""
        try:
            # Check if we already have valid credentials
            if 'google_credentials' in st.session_state:
                creds = Credentials.from_authorized_user_info(
                    st.session_state.google_credentials, self.scopes
                )
                if creds and creds.valid:
                    return creds
                elif creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    st.session_state.google_credentials = json.loads(creds.to_json())
                    return creds
            
            # If no valid credentials, show authentication instructions
            self._show_auth_instructions()
            return None
            
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return None
    
    def _show_auth_instructions(self):
        """Show authentication instructions to user"""
        st.info("""
        **Google Drive Authentication Setup:**
        
        To enable Google Drive synchronization, you need to:
        
        1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project or select an existing one
        3. Enable the Google Drive API
        4. Create OAuth 2.0 credentials
        5. Add your credentials as environment variables:
           - `GOOGLE_CLIENT_ID`
           - `GOOGLE_CLIENT_SECRET`
        
        For now, the app will work in offline mode without Google Drive sync.
        """)
        
        # Manual token input (for advanced users)
        st.subheader("Manual Token Input")
        st.info("If you already have a Google API token, you can paste it here:")
        
        token_input = st.text_area(
            "Paste your Google API token (JSON format):",
            height=100,
            placeholder='{"token": "ya29...", "refresh_token": "1//...", ...}'
        )
        
        if token_input and st.button("Use Token"):
            try:
                token_data = json.loads(token_input)
                creds = Credentials.from_authorized_user_info(token_data, self.scopes)
                if creds.valid:
                    st.session_state.google_credentials = token_data
                    st.success("Token accepted! Please refresh the page.")
                    return creds
                else:
                    st.error("Invalid token provided.")
            except json.JSONDecodeError:
                st.error("Invalid JSON format.")
            except Exception as e:
                st.error(f"Error processing token: {str(e)}")
    
    def create_oauth_flow(self, redirect_uri="http://localhost:8080/callback"):
        """Create OAuth flow for authentication"""
        try:
            flow = Flow.from_client_config(
                self.credentials_info,
                scopes=self.scopes,
                redirect_uri=redirect_uri
            )
            return flow
        except Exception as e:
            raise Exception(f"Error creating OAuth flow: {str(e)}")
    
    def get_authorization_url(self):
        """Get the authorization URL for OAuth flow"""
        try:
            flow = self.create_oauth_flow()
            auth_url, _ = flow.authorization_url(prompt='consent')
            return auth_url
        except Exception as e:
            return None
    
    def handle_callback(self, authorization_response):
        """Handle OAuth callback and return credentials"""
        try:
            flow = self.create_oauth_flow()
            flow.fetch_token(authorization_response=authorization_response)
            
            credentials = flow.credentials
            st.session_state.google_credentials = json.loads(credentials.to_json())
            
            return credentials
        except Exception as e:
            raise Exception(f"Error handling OAuth callback: {str(e)}")
    
    def revoke_credentials(self):
        """Revoke stored credentials"""
        if 'google_credentials' in st.session_state:
            del st.session_state.google_credentials
        
        st.success("Google Drive access revoked.")
