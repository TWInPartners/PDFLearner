# replit.md

## Overview

This is a comprehensive PDF Flashcard Generator application built with Streamlit that allows users to upload PDF documents and automatically generate flashcards and quiz questions from the content. The app features PostgreSQL database integration for persistent data storage, Google Drive synchronization, and is designed as a Progressive Web App (PWA) for mobile-friendly usage across devices.

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
- **Main Application**: Modern Streamlit app (`app.py`) with page-based routing and enhanced UX
- **Database Layer**: PostgreSQL with SQLAlchemy ORM for persistent data storage (`database.py`)
- **Modular Utils**: Separate utility modules for specific functionalities
- **Session Management**: Streamlit session state integrated with database persistence

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

1. **PDF Upload**: User uploads PDF through enhanced Streamlit interface
2. **Text Extraction**: PDFProcessor extracts and cleans text content
3. **Database Storage**: Document and content saved to PostgreSQL database
4. **Flashcard Generation**: FlashcardGenerator creates structured flashcards and questions
5. **Persistent Storage**: All data saved to database with user association
6. **Session Management**: Real-time session state synchronized with database
7. **Study Tracking**: Progress and statistics tracked in database
8. **Cloud Sync**: Optional Google Drive backup for cross-platform access
9. **Offline Support**: Service worker caches for offline functionality

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pdfplumber**: PDF text extraction
- **google-auth**: Google OAuth2 authentication
- **google-auth-oauthlib**: OAuth2 flow management
- **google-api-python-client**: Google Drive API integration
- **sqlalchemy**: Database ORM and connection management
- **psycopg2-binary**: PostgreSQL database adapter
- **alembic**: Database migration management

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

## Recent Changes (January 2025)

### Database Integration
- Added PostgreSQL database with comprehensive data models
- Implemented user management with automatic demo user creation
- Created persistent storage for documents, flashcards, questions, and study sessions
- Added study progress tracking and statistics collection
- Built database manager class with full CRUD operations

### Enhanced UX Design  
- Complete interface redesign with modern gradient styling and Inter font
- Implemented page-based navigation with clean routing system
- Added comprehensive dashboard with database-driven statistics
- Enhanced flashcard study interface with progress tracking
- Improved upload experience with visual feedback and file information
- Added recent documents section with quick study access

### New Features
- Database dashboard showing all user documents and statistics
- Study session tracking with time and accuracy metrics
- Random study mode for mixed document review
- Document preview and individual statistics
- Enhanced settings page with data management options

The application now provides enterprise-level data persistence with a consumer-friendly interface, ensuring seamless study experiences across sessions and devices while maintaining comprehensive progress tracking.

## Recent Updates (July 2025)

### User Authentication System (Latest)
- **NEW: Complete user authentication system** - Users can now create accounts and login to track progress across sessions
- Added secure password hashing with salt for user registration and login
- Implemented authentication manager with login/logout functionality
- Enhanced database with user authentication fields (password_hash, salt)
- Added login page with registration tab and demo mode option
- Integrated user session management with automatic redirect to login when not authenticated
- User progress and study materials are now tied to individual accounts
- Demo mode still available for users who want to try without registering

### Content Validation and Selection
- **Content validation and selection system** - Users can review extracted PDF content and select/deselect specific sections before generating study materials
- Split PDF text into manageable chunks with visual preview interface
- Bulk selection controls (Select All, Deselect All, Reset Selection)
- Real-time selection summary showing word count and section statistics
- Only selected content is used for flashcard and quiz generation

### Comprehensive Gamification System
- Implemented complete streak tracking system with badge rewards
- Added experience point (XP) system with level progression
- Created activity badges for study milestones and achievements
- Built dedicated badges page with progress visualization
- Added streak calendar view showing daily study activity
- Integrated session tracking during study modes with real-time metrics

### Enhanced User Experience
- Fixed navigation button styling for better readability and single-line text display
- Improved button responsiveness with proper container width utilization
- Enhanced study session tracking with automatic XP earning and level notifications
- Added achievement notifications with visual feedback (balloons, success messages)
- Implemented automatic streak bonus calculations and badge awarding

### Database and Server Issues Resolved
- Fixed SQLAlchemy database update method incompatibilities that were causing LSP errors
- Replaced bulk update operations with individual object modifications for better compatibility
- Resolved Streamlit server startup failures and configuration issues
- Fixed workflow configuration to properly start the application on port 5000
- Application now runs successfully with all core features functional

### Advanced Features Implementation
- Added OCR capabilities for extracting text from PDF images and figures
- Implemented comprehensive error handling system with user-friendly messages
- Enhanced PDF processing with graceful fallback for image text extraction
- Added file validation and size limits for better performance
- Integrated centralized error management throughout the application

### Technical Improvements
- Added comprehensive gamification data models (badges, streak_activities tables)
- Enhanced database manager with streak tracking and badge management methods
- Improved error handling in database operations with graceful degradation
- Streamlit server now runs reliably with proper configuration
- All dependencies properly installed and compatible
- Created robust error handling framework with user-friendly feedback
- Enhanced database connection with retry logic and connection pooling for large files
- Added content truncation (1MB limit) to prevent database timeouts and connection issues
- Implemented intelligent text chunking system for content selection interface
- **NEW: Authentication infrastructure** - Secure password-based user management with session tracking