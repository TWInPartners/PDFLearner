import streamlit as st
import traceback
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import functools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling with user-friendly messages"""
    
    ERROR_MESSAGES = {
        # PDF Processing Errors
        'pdf_upload_failed': {
            'title': 'Upload Problem',
            'message': 'We couldn\'t process your PDF file. Please make sure it\'s a valid PDF and try again.',
            'suggestions': [
                'Check that your file is actually a PDF',
                'Try a smaller file (under 50MB works best)',
                'Make sure the PDF isn\'t password protected'
            ]
        },
        'pdf_no_text': {
            'title': 'No Text Found',
            'message': 'Your PDF appears to be mostly images or scanned pages.',
            'suggestions': [
                'Our OCR system will try to read text from images',
                'For best results, use PDFs with selectable text',
                'Consider using a higher quality scan if possible'
            ]
        },
        'ocr_failed': {
            'title': 'Text Recognition Issue',
            'message': 'We had trouble reading text from images in your PDF.',
            'suggestions': [
                'The document will still work with any regular text found',
                'Try uploading a clearer version if available',
                'PDFs with selectable text work better than scanned images'
            ]
        },
        
        # Database Errors
        'db_connection_failed': {
            'title': 'Connection Problem',
            'message': 'We\'re having trouble saving your data right now.',
            'suggestions': [
                'Your work is temporarily stored and won\'t be lost',
                'Try refreshing the page in a moment',
                'Contact support if this keeps happening'
            ]
        },
        'db_save_failed': {
            'title': 'Save Problem',
            'message': 'We couldn\'t save your study materials to the database.',
            'suggestions': [
                'Your flashcards are still available in this session',
                'Try generating them again',
                'Check your internet connection'
            ]
        },
        
        # Content Generation Errors
        'generation_failed': {
            'title': 'Generation Problem',
            'message': 'We couldn\'t create flashcards from your document.',
            'suggestions': [
                'Try with a different document',
                'Make sure your PDF has enough readable text',
                'Contact support if this keeps happening'
            ]
        },
        'insufficient_content': {
            'title': 'Not Enough Content',
            'message': 'Your document doesn\'t have enough text to create good study materials.',
            'suggestions': [
                'Try uploading a longer document',
                'Make sure the PDF has readable text content',
                'Documents with at least a few paragraphs work best'
            ]
        },
        
        # Google Drive Errors
        'drive_auth_failed': {
            'title': 'Google Drive Connection Failed',
            'message': 'We couldn\'t connect to your Google Drive account.',
            'suggestions': [
                'Try connecting again',
                'Make sure you\'re signed into the right Google account',
                'Check that you gave permission to access your Drive'
            ]
        },
        'drive_sync_failed': {
            'title': 'Sync Problem',
            'message': 'We couldn\'t sync your study materials to Google Drive.',
            'suggestions': [
                'Your local copy is still safe',
                'Check your internet connection',
                'Try syncing again in a moment'
            ]
        },
        
        # General Errors
        'unexpected_error': {
            'title': 'Something Went Wrong',
            'message': 'We encountered an unexpected problem.',
            'suggestions': [
                'Try refreshing the page',
                'Your work should still be saved',
                'Contact support if this keeps happening'
            ]
        },
        'file_too_large': {
            'title': 'File Too Large',
            'message': 'Your PDF file is too big to process.',
            'suggestions': [
                'Try a file smaller than 200MB',
                'Consider splitting large documents into smaller sections',
                'Compress your PDF if possible using online tools'
            ]
        }
    }
    
    @staticmethod
    def display_error(error_type: str, technical_details: Optional[str] = None, 
                     show_technical: bool = False) -> None:
        """Display a user-friendly error message"""
        error_info = ErrorHandler.ERROR_MESSAGES.get(
            error_type, 
            ErrorHandler.ERROR_MESSAGES['unexpected_error']
        )
        
        # Show main error message
        st.error(f"**{error_info['title']}**")
        st.write(error_info['message'])
        
        # Show suggestions
        if error_info['suggestions']:
            st.info("**What you can try:**")
            for suggestion in error_info['suggestions']:
                st.write(f"• {suggestion}")
        
        # Show technical details if requested (for debugging)
        if show_technical and technical_details:
            with st.expander("Technical Details (for support)"):
                st.code(technical_details)
        
        # Log the error
        logger.error(f"Error: {error_type} - {technical_details}")
    
    @staticmethod
    def handle_exception(error_type: str, show_technical: bool = False):
        """Decorator for handling exceptions with user-friendly messages"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    technical_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                    ErrorHandler.display_error(error_type, technical_details, show_technical)
                    return None
            return wrapper
        return decorator
    
    @staticmethod
    def safe_execute(func: Callable, error_type: str, 
                    fallback_value: Any = None, show_technical: bool = False) -> Any:
        """Safely execute a function with error handling"""
        try:
            return func()
        except Exception as e:
            technical_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            ErrorHandler.display_error(error_type, technical_details, show_technical)
            return fallback_value
    
    @staticmethod
    def validate_file(uploaded_file) -> Dict[str, Any]:
        """Validate uploaded file and return status"""
        if not uploaded_file:
            return {'valid': False, 'error': 'No file uploaded'}
        
        # Check file type
        if not uploaded_file.name.lower().endswith('.pdf'):
            return {'valid': False, 'error': 'file_not_pdf'}
        
        # Check file size (200MB limit)
        file_size = len(uploaded_file.getvalue())
        if file_size > 200 * 1024 * 1024:  # 200MB
            return {'valid': False, 'error': 'file_too_large'}
        
        return {'valid': True, 'size': file_size}
    
    @staticmethod
    def show_success(message: str, details: Optional[str] = None) -> None:
        """Display success message with optional details"""
        st.success(f"**Success!** {message}")
        if details:
            st.info(details)
    
    @staticmethod
    def show_warning(message: str, suggestions: Optional[list] = None) -> None:
        """Display warning message with suggestions"""
        st.warning(f"**Heads up:** {message}")
        if suggestions:
            for suggestion in suggestions:
                st.write(f"• {suggestion}")

# Convenience decorators for common error types
pdf_error_handler = ErrorHandler.handle_exception('pdf_upload_failed')
db_error_handler = ErrorHandler.handle_exception('db_connection_failed')
generation_error_handler = ErrorHandler.handle_exception('generation_failed')
drive_error_handler = ErrorHandler.handle_exception('drive_sync_failed')