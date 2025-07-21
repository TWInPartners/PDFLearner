import streamlit as st
import json
import os
from datetime import datetime
import base64
from utils.pdf_processor import PDFProcessor
from utils.flashcard_generator import FlashcardGenerator
from utils.google_drive_sync import GoogleDriveSync
from utils.auth import GoogleAuth

# Page configuration for PWA
st.set_page_config(
    page_title="PDF Flashcard Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

initialize_session_state()

def main():
    st.title("📚 PDF Flashcard Generator")
    st.markdown("Upload a PDF and generate flashcards with Google Drive sync")
    
    # Authentication Section
    if not st.session_state.authenticated:
        st.header("🔐 Google Drive Authentication")
        st.info("Please authenticate with Google Drive to enable synchronization of your flashcards.")
        
        if st.button("Authenticate with Google Drive", type="primary"):
            try:
                auth = GoogleAuth()
                credentials = auth.authenticate()
                if credentials:
                    st.session_state.authenticated = True
                    st.session_state.google_drive = GoogleDriveSync(credentials)
                    st.success("Authentication successful!")
                    st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
        
        st.markdown("---")
        st.info("You can continue without authentication, but your flashcards won't be synced to Google Drive.")
        if st.button("Continue without sync"):
            st.session_state.authenticated = True
            st.rerun()
        return
    
    # Sidebar for navigation and settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        if st.session_state.google_drive:
            st.success("✅ Google Drive Connected")
            if st.button("Sync Data"):
                sync_data()
        else:
            st.warning("📴 Offline Mode")
        
        st.markdown("---")
        
        # Study mode selection
        st.session_state.study_mode = st.selectbox(
            "Study Mode",
            ["flashcards", "multiple_choice"],
            format_func=lambda x: "📇 Flashcards" if x == "flashcards" else "❓ Multiple Choice"
        )
        
        # Display statistics
        if st.session_state.flashcards:
            st.metric("Flashcards Generated", len(st.session_state.flashcards))
        if st.session_state.questions:
            st.metric("Questions Generated", len(st.session_state.questions))
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📤 Upload PDF", "📚 Study", "📊 Review"])
    
    with tab1:
        upload_pdf_section()
    
    with tab2:
        study_section()
    
    with tab3:
        review_section()

def upload_pdf_section():
    st.header("Upload PDF Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to generate flashcards from"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing PDF..."):
            try:
                # Process PDF
                pdf_processor = PDFProcessor()
                text = pdf_processor.extract_text(uploaded_file)
                st.session_state.pdf_text = text
                
                # Display extracted text preview
                st.subheader("📄 Extracted Text Preview")
                st.text_area("Text Preview", text[:500] + "..." if len(text) > 500 else text, height=100, disabled=True)
                
                # Generation options
                col1, col2 = st.columns(2)
                
                with col1:
                    num_flashcards = st.slider("Number of Flashcards", 5, 50, 15)
                
                with col2:
                    num_questions = st.slider("Number of Questions", 5, 30, 10)
                
                if st.button("🚀 Generate Flashcards & Questions", type="primary"):
                    generate_content(text, num_flashcards, num_questions)
                    
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")

def generate_content(text, num_flashcards, num_questions):
    with st.spinner("Generating flashcards and questions..."):
        try:
            generator = FlashcardGenerator()
            
            # Generate flashcards
            flashcards = generator.generate_flashcards(text, num_flashcards)
            st.session_state.flashcards = flashcards
            
            # Generate multiple choice questions
            questions = generator.generate_questions(text, num_questions)
            st.session_state.questions = questions
            
            # Reset study progress
            st.session_state.current_card = 0
            st.session_state.show_answer = False
            
            # Sync to Google Drive if connected
            if st.session_state.google_drive:
                sync_data()
            
            st.success(f"Generated {len(flashcards)} flashcards and {len(questions)} questions!")
            st.info("Switch to the 'Study' tab to review your flashcards.")
            
        except Exception as e:
            st.error(f"Error generating content: {str(e)}")

def study_section():
    if not st.session_state.flashcards and not st.session_state.questions:
        st.info("No study materials available. Please upload a PDF first.")
        return
    
    if st.session_state.study_mode == "flashcards":
        display_flashcards()
    else:
        display_questions()

def display_flashcards():
    if not st.session_state.flashcards:
        st.info("No flashcards generated yet. Please upload a PDF and generate flashcards.")
        return
    
    st.header("📇 Flashcard Study Mode")
    
    # Progress bar
    progress = (st.session_state.current_card + 1) / len(st.session_state.flashcards)
    st.progress(progress)
    st.caption(f"Card {st.session_state.current_card + 1} of {len(st.session_state.flashcards)}")
    
    # Current flashcard
    current_flashcard = st.session_state.flashcards[st.session_state.current_card]
    
    # Card display
    with st.container():
        st.markdown("### Question")
        st.markdown(f"**{current_flashcard['question']}**")
        
        if st.session_state.show_answer:
            st.markdown("### Answer")
            st.success(current_flashcard['answer'])
        
        # Control buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⬅️ Previous", disabled=st.session_state.current_card == 0):
                st.session_state.current_card -= 1
                st.session_state.show_answer = False
                st.rerun()
        
        with col2:
            if st.button("👁️ Show Answer" if not st.session_state.show_answer else "🙈 Hide Answer"):
                st.session_state.show_answer = not st.session_state.show_answer
                st.rerun()
        
        with col3:
            if st.button("➡️ Next", disabled=st.session_state.current_card >= len(st.session_state.flashcards) - 1):
                st.session_state.current_card += 1
                st.session_state.show_answer = False
                st.rerun()
        
        with col4:
            if st.button("🔀 Shuffle"):
                import random
                random.shuffle(st.session_state.flashcards)
                st.session_state.current_card = 0
                st.session_state.show_answer = False
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

def sync_data():
    if not st.session_state.google_drive:
        return
    
    try:
        with st.spinner("Syncing with Google Drive..."):
            # Create data to sync
            data = {
                'flashcards': st.session_state.flashcards,
                'questions': st.session_state.questions,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Upload to Google Drive
            st.session_state.google_drive.save_data(data)
            st.success("Data synced successfully!")
    except Exception as e:
        st.error(f"Sync failed: {str(e)}")

if __name__ == "__main__":
    main()
