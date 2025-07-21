# replit.md

## Overview

This is a PDF Flashcard Generator application built with Streamlit that allows users to upload PDF documents and automatically generate flashcards from the content. The app features Google Drive integration for syncing flashcards and is designed as a Progressive Web App (PWA) for mobile-friendly usage.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

### Frontend Architecture
- **Framework**: Streamlit for the web interface
- **PWA Support**: Configured as a Progressive Web App with manifest.json and service worker
- **Layout**: Wide layout with expandable sidebar for better user experience
- **Mobile-First**: Designed for mobile usage with portrait orientation

### Backend Architecture
- **Main Application**: Flask-like Streamlit app (`app.py`) serving as the entry point
- **Modular Utils**: Separate utility modules for specific functionalities
- **Session Management**: Streamlit session state for maintaining user data across interactions

## Key Components

### Core Modules

1. **PDF Processor** (`utils/pdf_processor.py`)
   - Handles PDF text extraction using pdfplumber
   - Provides text cleaning and preprocessing capabilities
   - Error handling for various PDF formats and corrupt files

2. **Flashcard Generator** (`utils/flashcard_generator.py`)
   - Generates different types of flashcards (concept, definition, fact, process)
   - Uses natural language processing techniques to extract key information
   - Configurable number of cards with intelligent content distribution

3. **Google Drive Sync** (`utils/google_drive_sync.py`)
   - Manages Google Drive integration for cloud storage
   - Automatic folder creation and file management
   - JSON-based data persistence for flashcard sets

4. **Authentication** (`utils/auth.py`)
   - Google OAuth2 integration for Drive access
   - Environment variable configuration support
   - Fallback credentials for development/demo purposes

### PWA Components

1. **Manifest** (`manifest.json`)
   - Defines app metadata and behavior as PWA
   - Configured for standalone display mode
   - Includes app icons and screenshots for installation

2. **Service Worker** (`service_worker.js`)
   - Enables offline functionality through caching
   - Background sync capabilities for data persistence
   - Cache management and cleanup

## Data Flow

1. **PDF Upload**: User uploads PDF through Streamlit file uploader
2. **Text Extraction**: PDFProcessor extracts and cleans text content
3. **Flashcard Generation**: FlashcardGenerator creates structured flashcards from text
4. **Local Storage**: Flashcards stored in Streamlit session state
5. **Cloud Sync**: Optional Google Drive sync for persistence across devices
6. **Offline Support**: Service worker caches data for offline access

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pdfplumber**: PDF text extraction
- **google-auth**: Google OAuth2 authentication
- **google-auth-oauthlib**: OAuth2 flow management
- **google-api-python-client**: Google Drive API integration

### Google Services
- **Google Drive API**: Cloud storage and synchronization
- **Google OAuth2**: User authentication and authorization

### PWA Technologies
- **Service Workers**: Offline functionality and caching
- **Web App Manifest**: PWA installation and behavior

## Deployment Strategy

### Environment Configuration
- Google API credentials via environment variables (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`)
- Fallback configuration for development environments
- Support for both local and cloud deployments

### PWA Deployment
- Configured for standalone mobile app experience
- Offline-first architecture with service worker caching
- Optimized for mobile devices with portrait orientation

### Scalability Considerations
- Modular architecture allows for easy feature additions
- Google Drive integration provides unlimited storage scaling
- Session-based state management for multi-user support

The application prioritizes user experience with a clean, mobile-friendly interface while providing robust PDF processing and cloud synchronization capabilities. The PWA architecture ensures the app works seamlessly across devices and platforms.