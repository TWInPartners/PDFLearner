import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import streamlit as st

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    last_active = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    preferences = Column(JSON, default={})
    
    # Relationships
    documents = relationship("Document", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String)
    original_filename = Column(String)
    file_size = Column(Integer)  # in bytes
    content_text = Column(Text)
    word_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True), nullable=True)
    is_processed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    flashcards = relationship("Flashcard", back_populates="document")
    questions = relationship("Question", back_populates="document")

class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    question = Column(Text)
    answer = Column(Text)
    card_type = Column(String)  # concept, definition, fact, process, etc.
    difficulty = Column(Integer, default=1)  # 1-5 scale
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Study tracking
    times_studied = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    last_studied = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="flashcards")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    question_text = Column(Text)
    options = Column(JSON)  # Array of options
    correct_answer = Column(String)
    question_type = Column(String)  # multiple_choice, fill_blank, etc.
    difficulty = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Study tracking
    times_answered = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    last_answered = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="questions")

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    session_type = Column(String)  # flashcards, questions, mixed
    started_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True), nullable=True)
    cards_studied = Column(Integer, default=0)
    cards_correct = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")

# Database helper class
class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.create_tables()
    
    def create_tables(self):
        """Create all tables if they don't exist"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def get_or_create_user(self, email=None, google_id=None, name=None):
        """Get existing user or create new one - returns dict to avoid session issues"""
        session = self.get_session()
        try:
            # Try to find existing user
            user = None
            if email:
                user = session.query(User).filter(User.email == email).first()
            elif google_id:
                user = session.query(User).filter(User.google_id == google_id).first()
            
            if not user:
                # Create new user
                user = User(
                    email=email,
                    google_id=google_id,
                    name=name or "Anonymous User",
                    preferences={"study_mode": "flashcards", "auto_reveal": False}
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            else:
                # Update last active
                session.query(User).filter(User.id == user.id).update({
                    'last_active': datetime.now(timezone.utc)
                })
                session.commit()
            
            # Return as dict to avoid session issues
            return {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'google_id': user.google_id,
                'preferences': user.preferences,
                'created_at': user.created_at,
                'last_active': user.last_active
            }
        finally:
            session.close()
    
    def save_document(self, user_id, title, filename, file_size, content_text):
        """Save a processed document"""
        session = self.get_session()
        try:
            document = Document(
                user_id=user_id,
                title=title,
                original_filename=filename,
                file_size=file_size,
                content_text=content_text,
                word_count=len(content_text.split()),
                processed_at=datetime.now(timezone.utc),
                is_processed=True
            )
            session.add(document)
            session.commit()
            session.refresh(document)
            return document
        finally:
            session.close()
    
    def save_flashcards(self, document_id, flashcards_data):
        """Save flashcards to database"""
        session = self.get_session()
        try:
            flashcards = []
            for card_data in flashcards_data:
                flashcard = Flashcard(
                    document_id=document_id,
                    question=card_data['question'],
                    answer=card_data['answer'],
                    card_type=card_data.get('type', 'general')
                )
                session.add(flashcard)
                flashcards.append(flashcard)
            
            session.commit()
            return flashcards
        finally:
            session.close()
    
    def save_questions(self, document_id, questions_data):
        """Save questions to database"""
        session = self.get_session()
        try:
            questions = []
            for question_data in questions_data:
                question = Question(
                    document_id=document_id,
                    question_text=question_data['question'],
                    options=question_data['options'],
                    correct_answer=question_data['correct_answer'],
                    question_type=question_data.get('type', 'multiple_choice')
                )
                session.add(question)
                questions.append(question)
            
            session.commit()
            return questions
        finally:
            session.close()
    
    def get_user_documents(self, user_id):
        """Get all documents for a user"""
        session = self.get_session()
        try:
            documents = session.query(Document).filter(
                Document.user_id == user_id
            ).order_by(Document.created_at.desc()).all()
            return documents
        finally:
            session.close()
    
    def get_document_flashcards(self, document_id):
        """Get all flashcards for a document"""
        session = self.get_session()
        try:
            flashcards = session.query(Flashcard).filter(
                Flashcard.document_id == document_id
            ).all()
            return flashcards
        finally:
            session.close()
    
    def get_document_questions(self, document_id):
        """Get all questions for a document"""
        session = self.get_session()
        try:
            questions = session.query(Question).filter(
                Question.document_id == document_id
            ).all()
            return questions
        finally:
            session.close()
    
    def update_flashcard_study(self, flashcard_id, correct=None):
        """Update flashcard study statistics"""
        session = self.get_session()
        try:
            update_data = {
                'times_studied': Flashcard.times_studied + 1,
                'last_studied': datetime.now(timezone.utc)
            }
            if correct is not None and correct:
                update_data['times_correct'] = Flashcard.times_correct + 1
            
            session.query(Flashcard).filter(Flashcard.id == flashcard_id).update(update_data, synchronize_session='fetch')
            session.commit()
        finally:
            session.close()
    
    def update_question_study(self, question_id, correct=None):
        """Update question study statistics"""
        session = self.get_session()
        try:
            update_data = {
                'times_answered': Question.times_answered + 1,
                'last_answered': datetime.now(timezone.utc)
            }
            if correct is not None and correct:
                update_data['times_correct'] = Question.times_correct + 1
            
            session.query(Question).filter(Question.id == question_id).update(update_data, synchronize_session='fetch')
            session.commit()
        finally:
            session.close()
    
    def start_study_session(self, user_id, document_id, session_type):
        """Start a new study session"""
        session = self.get_session()
        try:
            study_session = StudySession(
                user_id=user_id,
                document_id=document_id,
                session_type=session_type
            )
            session.add(study_session)
            session.commit()
            session.refresh(study_session)
            return study_session
        finally:
            session.close()
    
    def end_study_session(self, session_id, stats):
        """End a study session with statistics"""
        session = self.get_session()
        try:
            study_session = session.query(StudySession).filter(StudySession.id == session_id).first()
            if study_session:
                ended_at = datetime.now(timezone.utc)
                duration = ended_at - study_session.started_at
                duration_minutes = int(duration.total_seconds() / 60)
                
                update_data = {
                    'ended_at': ended_at,
                    'cards_studied': stats.get('cards_studied', 0),
                    'cards_correct': stats.get('cards_correct', 0),
                    'questions_answered': stats.get('questions_answered', 0),
                    'questions_correct': stats.get('questions_correct', 0),
                    'duration_minutes': duration_minutes
                }
                
                session.query(StudySession).filter(StudySession.id == session_id).update(update_data, synchronize_session='fetch')
                session.commit()
        finally:
            session.close()
    
    def get_user_stats(self, user_id):
        """Get comprehensive user statistics"""
        session = self.get_session()
        try:
            # Get document count
            doc_count = session.query(Document).filter(Document.user_id == user_id).count()
            
            # Get flashcard count
            flashcard_count = session.query(Flashcard).join(Document).filter(
                Document.user_id == user_id
            ).count()
            
            # Get question count  
            question_count = session.query(Question).join(Document).filter(
                Document.user_id == user_id
            ).count()
            
            # Get study session stats
            sessions = session.query(StudySession).filter(StudySession.user_id == user_id).all()
            total_study_time = sum((s.duration_minutes if s.duration_minutes is not None else 0) for s in sessions)
            total_cards_studied = sum(s.cards_studied for s in sessions)
            total_questions_answered = sum(s.questions_answered for s in sessions)
            
            return {
                'documents': doc_count,
                'flashcards': flashcard_count,
                'questions': question_count,
                'study_sessions': len(sessions),
                'total_study_time_minutes': total_study_time,
                'cards_studied': total_cards_studied,
                'questions_answered': total_questions_answered
            }
        finally:
            session.close()

# Initialize database manager
@st.cache_resource
def get_db_manager():
    return DatabaseManager()