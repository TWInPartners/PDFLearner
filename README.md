🎓 StudyGen: Your AI-Powered PDF Flashcard Generator
StudyGen is an innovative web application that transforms your PDF documents into interactive flashcards and multiple-choice quizzes. Powered by AI, it helps you extract key information, organize your study materials, and track your learning progress with a built-in gamification system.

✨ Features
  PDF to Flashcards: Upload any PDF document and let StudyGen's AI extract relevant content to automatically generate a set of flashcards.

  Interactive Quizzes: Generate multiple-choice questions from your PDF content to test your understanding.

  Personalized Study Modes: Choose between flashcard review and quiz modes to suit your learning style.

  Persistent Data Storage: All your uploaded documents, generated flashcards, and quizzes are securely stored in a PostgreSQL database, so your progress is always saved.

  Google Drive Synchronization: Optionally connect your Google Drive account to sync your study materials to the cloud, allowing access from any device.

  Gamification System: Stay motivated with:

    Study Streaks: Track consecutive study days and earn badges.

    Experience Points (XP): Gain XP as you study and level up.

    Achievement Badges: Unlock various badges for reaching study milestones and achievements.

  Comprehensive Dashboard: View detailed statistics about your study habits, including total documents, flashcards, questions, study sessions, and gamification progress.

  Progressive Web App (PWA): Install StudyGen on your mobile device or desktop for an app-like experience, including offline access and quick launch.

  Modern User Interface: Enjoy a clean, intuitive, and responsive design optimized for various screen sizes.

🚀 Technologies Used
StudyGen is built using a robust tech stack:

  Frontend:

    Streamlit: For building the interactive web application.

    Custom CSS: For a modern and engaging user experience.

  Backend:

    Python 3.x

    pdfplumber: For efficient PDF text extraction.

    Custom AI/NLP Logic: For generating flashcards and questions.

  Database:

    PostgreSQL: For persistent data storage.

    SQLAlchemy: Python SQL toolkit and Object Relational Mapper (ORM).

    Alembic: For database migrations.

  Cloud Integration:

    Google Drive API: For cloud synchronization.

    Google OAuth2: For secure user authentication.

  PWA:

    Service Workers: For offline capabilities and caching.

    Web App Manifest: For PWA installation and metadata.

⚙️ Installation & Setup
To run StudyGen locally, follow these steps:

  Clone the Repository:

    git clone <repository_url>
    cd PDFLearner

  Set up Environment Variables:
  StudyGen requires Google API credentials for Google Drive sync and a PostgreSQL database.

    Google API Credentials:

      Go to the Google Cloud Console.

      Create a new project or select an existing one.

      Enable the Google Drive API.

      Create OAuth 2.0 Client IDs credentials (Web application type).

      Add http://localhost:8080/callback to your authorized redirect URIs.

      Set the following environment variables:

        export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
        export GOOGLE_CLIENT_SECRET="your-client-secret"

  PostgreSQL Database:

    Ensure you have a PostgreSQL database running (e.g., locally, Docker, or a cloud provider like Render, Heroku).

    Set the DATABASE_URL environment variable. Example:

      export DATABASE_URL="postgresql://user:password@host:port/database_name"

      (For local development, you might use postgresql://localhost/your_db_name)

  Install Dependencies:
  StudyGen uses uv for dependency management.

    uv pip install -r requirements.txt # (assuming you have a requirements.txt, if not, use the pyproject.toml dependencies)
    # Or, if using pyproject.toml directly:
    uv add pdfplumber google-api-python-client google-auth-httplib2 google-auth-oauthlib psycopg2-binary sqlalchemy alembic

  Run Database Migrations:
  Ensure your database schema is up-to-date. (Alembic setup is usually handled within the app.py or database.py for initial table creation, but for full migration support, you'd typically run alembic upgrade head). For this project, the DatabaseManager in database.py calls Base.metadata.create_all(bind=self.engine) on initialization, which creates tables if they don't exist.

  Start the Application:

    streamlit run app.py --server.port 5000

  The app will typically open in your web browser at http://localhost:5000.

📖 Usage
  Home Page: Get an overview of your study progress, recent documents, and quick actions.

  Upload & Generate: Navigate to the "Upload" section.

    Drag and drop your PDF file or click to select it.

    Once uploaded, preview the extracted text.

    Adjust the number of flashcards and questions you want to generate.

    Click "Generate Study Materials" to create your content.

  Study Mode: Go to the "Study" section.

    Choose between "Flashcards" or "Multiple Choice" mode.

    Use the navigation buttons to move through cards/questions.

    In flashcard mode, click "Reveal Answer" to check your knowledge.

  Badges: Visit the "Badges" page to see your earned achievements, current streak, and level progress.

  Dashboard: The "Dashboard" provides a comprehensive view of all your documents and study statistics.

  Settings & Sync: In the "Settings" section, you can:

    Connect/Disconnect your Google Drive account for cloud sync.

    Manually trigger a sync.

    Manage (clear) your local study data.

📱 PWA Features
StudyGen is designed as a Progressive Web App, offering an enhanced experience:

  Installable: You can "install" StudyGen to your home screen on mobile devices or as a desktop app, making it accessible like a native application.

  Offline Access: Thanks to the service worker, you can access previously loaded content and some app functionalities even without an internet connection.

  Fast Loading: Cached assets ensure quick load times.

🏆 Gamification
StudyGen makes learning fun and motivating:

  Streaks: Study daily to build and maintain your streak. Don't break the chain!

  XP & Levels: Every minute of study and every correct answer earns you Experience Points, helping you level up and track your mastery.

  Badges: Earn unique badges for achieving various milestones, such as studying for a certain number of days, reaching a new level, or completing a specific number of cards/questions.

🤝 Contributing
Contributions are welcome! If you have suggestions for improvements or new features, please feel free to open an issue or submit a pull request.

📄 License
This project is open-source and available under the MIT License.
📄 License
This project is open-source and available under the MIT License.
