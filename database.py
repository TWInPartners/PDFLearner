import os
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy.pool import QueuePool
import streamlit as st
import time
import logging

# Database setup with connection pooling and retry logic
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Enhanced engine configuration for large files and connection stability
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before use
    connect_args={
        "sslmode": "require",
        "connect_timeout": 30
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logger = logging.getLogger(__name__)

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String)
    password_hash = Column(String, nullable=True)  # For email/password login
    salt = Column(String, nullable=True)  # Password salt
    avatar_config = Column(JSON, default={})  # Avatar customization data
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    last_active = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    preferences = Column(JSON, default={})
    
    # Gamification fields
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_study_date = Column(DateTime(timezone=True), nullable=True)
    total_badges = Column(Integer, default=0)
    level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)
    
    # Relationships
    documents = relationship("Document", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")
    badges = relationship("Badge", back_populates="user")
    streak_activities = relationship("StreakActivity", back_populates="user")

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

class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    badge_type = Column(String)  # streak, milestone, achievement
    badge_name = Column(String)  # "Fire Starter", "Study Machine", etc.
    badge_description = Column(Text)
    badge_icon = Column(String)  # emoji or icon code
    requirements = Column(JSON)  # criteria for earning the badge
    earned_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    is_featured = Column(Boolean, default=False)  # show prominently
    
    # Relationships
    user = relationship("User", back_populates="badges")

class StreakActivity(Base):
    __tablename__ = "streak_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    activity_date = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    study_minutes = Column(Integer, default=0)
    cards_studied = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    streak_day_number = Column(Integer, default=1)
    
    # Relationships  
    user = relationship("User", back_populates="streak_activities")

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
    
    def execute_with_retry(self, operation, max_retries=3, delay=1):
        """Execute database operation with retry logic for connection issues"""
        for attempt in range(max_retries):
            try:
                return operation()
            except (OperationalError, DisconnectionError) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Database operation failed after {max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Database connection issue (attempt {attempt + 1}): {str(e)}. Retrying...")
                time.sleep(delay * (attempt + 1))  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected database error: {str(e)}")
                raise
    
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
    
    def get_user_by_email(self, email):
        """Get user by email address"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return None
            
            return {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'google_id': user.google_id,
                'password_hash': user.password_hash,
                'salt': user.salt,
                'avatar_config': user.avatar_config or {},
                'preferences': user.preferences,
                'created_at': user.created_at,
                'last_active': user.last_active,
                'current_streak': user.current_streak,
                'level': user.level,
                'experience_points': user.experience_points
            }
        finally:
            session.close()
    
    def create_user_with_password(self, user_data):
        """Create new user with password authentication"""
        session = self.get_session()
        try:
            user = User(
                email=user_data['email'],
                name=user_data['name'],
                password_hash=user_data['password_hash'],
                salt=user_data['salt'],
                avatar_config=user_data.get('avatar_config', {}),
                preferences=user_data.get('preferences', {})
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            return {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'preferences': user.preferences,
                'created_at': user.created_at,
                'last_active': user.last_active
            }
        finally:
            session.close()
    
    def update_user_last_active(self, user_id):
        """Update user's last active timestamp"""
        session = self.get_session()
        try:
            session.query(User).filter(User.id == user_id).update({
                'last_active': datetime.now(timezone.utc)
            })
            session.commit()
        finally:
            session.close()
    
    def save_document(self, user_id, title, filename, file_size, content_text):
        """Save a processed document with retry logic for large files"""
        def _save_operation():
            session = self.get_session()
            try:
                # For very large content, truncate if necessary to prevent issues
                max_content_length = 1000000  # 1MB of text
                if len(content_text) > max_content_length:
                    truncated_content = content_text[:max_content_length] + "\n\n[Content truncated due to size...]"
                    logger.warning(f"Document content truncated from {len(content_text)} to {len(truncated_content)} characters")
                else:
                    truncated_content = content_text
                
                document = Document(
                    user_id=user_id,
                    title=title,
                    original_filename=filename,
                    file_size=file_size,
                    content_text=truncated_content,
                    word_count=len(truncated_content.split()),
                    processed_at=datetime.now(timezone.utc),
                    is_processed=True
                )
                session.add(document)
                session.commit()
                session.refresh(document)
                return document
            finally:
                session.close()
        
        return self.execute_with_retry(_save_operation)
    
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
            flashcard = session.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
            if flashcard:
                flashcard.times_studied += 1
                flashcard.last_studied = datetime.now(timezone.utc)
                if correct is not None and correct:
                    flashcard.times_correct += 1
                session.commit()
        finally:
            session.close()
    
    def update_question_study(self, question_id, correct=None):
        """Update question study statistics"""
        session = self.get_session()
        try:
            question = session.query(Question).filter(Question.id == question_id).first()
            if question:
                question.times_answered += 1
                question.last_answered = datetime.now(timezone.utc)
                if correct is not None and correct:
                    question.times_correct += 1
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
                
                study_session.ended_at = ended_at
                study_session.cards_studied = stats.get('cards_studied', 0)
                study_session.cards_correct = stats.get('cards_correct', 0)
                study_session.questions_answered = stats.get('questions_answered', 0)
                study_session.questions_correct = stats.get('questions_correct', 0)
                study_session.duration_minutes = duration_minutes
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
            
            # Get gamification stats
            user = session.query(User).filter(User.id == user_id).first()
            badges_count = session.query(Badge).filter(Badge.user_id == user_id).count()
            
            return {
                'documents': doc_count,
                'flashcards': flashcard_count,
                'questions': question_count,
                'study_sessions': len(sessions),
                'total_study_time_minutes': total_study_time,
                'cards_studied': total_cards_studied,
                'questions_answered': total_questions_answered,
                # Gamification stats
                'current_streak': user.current_streak if user else 0,
                'longest_streak': user.longest_streak if user else 0,
                'level': user.level if user else 1,
                'experience_points': user.experience_points if user else 0,
                'badges_count': badges_count
            }
        finally:
            session.close()
    
    def update_user_gamification(self, user_id, study_minutes=0, cards_studied=0, questions_answered=0):
        """Update user's gamification stats and check for new badges"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return
            
            today = datetime.now(timezone.utc).date()
            yesterday = user.last_study_date.date() if user.last_study_date else None
            
            # Calculate experience points
            xp_gained = (study_minutes * 2) + (cards_studied * 1) + (questions_answered * 1)
            user.experience_points += xp_gained
            
            # Update level based on XP (every 100 XP = 1 level)
            new_level = max(1, user.experience_points // 100)
            level_up = new_level > user.level
            user.level = new_level
            
            # Update streak logic
            if yesterday == today:
                # Same day, just update activity
                pass
            elif yesterday and (today - yesterday).days == 1:
                # Consecutive day, extend streak
                user.current_streak += 1
                user.longest_streak = max(user.longest_streak, user.current_streak)
            elif yesterday and (today - yesterday).days > 1:
                # Missed days, reset streak
                user.current_streak = 1
            else:
                # First time or same day
                user.current_streak = max(1, user.current_streak)
            
            user.last_study_date = datetime.now(timezone.utc)
            
            # Record daily activity
            existing_activity = session.query(StreakActivity).filter(
                StreakActivity.user_id == user_id,
                StreakActivity.activity_date >= datetime.combine(today, datetime.min.time().replace(tzinfo=timezone.utc))
            ).first()
            
            if existing_activity:
                existing_activity.study_minutes += study_minutes
                existing_activity.cards_studied += cards_studied
                existing_activity.questions_answered += questions_answered
            else:
                new_activity = StreakActivity(
                    user_id=user_id,
                    study_minutes=study_minutes,
                    cards_studied=cards_studied,
                    questions_answered=questions_answered,
                    streak_day_number=user.current_streak
                )
                session.add(new_activity)
            
            session.commit()
            
            # Check for new badges
            new_badges = self._check_and_award_badges(session, user)
            
            return {
                'level_up': level_up,
                'new_level': user.level,
                'xp_gained': xp_gained,
                'total_xp': user.experience_points,
                'current_streak': user.current_streak,
                'longest_streak': user.longest_streak,
                'new_badges': new_badges
            }
        finally:
            session.close()
    
    def _check_and_award_badges(self, session, user):
        """Check for and award new badges"""
        new_badges = []
        
        # Define badge criteria
        badge_definitions = [
            # Streak badges
            {'type': 'streak', 'name': 'Fire Starter', 'icon': '🔥', 'description': 'Study for 3 days in a row', 'req_streak': 3},
            {'type': 'streak', 'name': 'Committed', 'icon': '💪', 'description': 'Study for 7 days in a row', 'req_streak': 7},
            {'type': 'streak', 'name': 'Study Machine', 'icon': '🚀', 'description': 'Study for 14 days in a row', 'req_streak': 14},
            {'type': 'streak', 'name': 'Unstoppable', 'icon': '⚡', 'description': 'Study for 30 days in a row', 'req_streak': 30},
            {'type': 'streak', 'name': 'Legend', 'icon': '👑', 'description': 'Study for 100 days in a row', 'req_streak': 100},
            
            # Level badges
            {'type': 'level', 'name': 'Rising Star', 'icon': '⭐', 'description': 'Reach level 5', 'req_level': 5},
            {'type': 'level', 'name': 'Expert', 'icon': '🎯', 'description': 'Reach level 10', 'req_level': 10},
            {'type': 'level', 'name': 'Master', 'icon': '🏆', 'description': 'Reach level 25', 'req_level': 25},
            {'type': 'level', 'name': 'Grandmaster', 'icon': '💎', 'description': 'Reach level 50', 'req_level': 50},
            
            # Activity badges
            {'type': 'activity', 'name': 'Bookworm', 'icon': '📚', 'description': 'Study 100 flashcards', 'req_cards': 100},
            {'type': 'activity', 'name': 'Quiz Master', 'icon': '🧠', 'description': 'Answer 200 questions', 'req_questions': 200},
            {'type': 'activity', 'name': 'Time Scholar', 'icon': '⏰', 'description': 'Study for 10 hours total', 'req_minutes': 600},
        ]
        
        for badge_def in badge_definitions:
            # Check if user already has this badge
            existing = session.query(Badge).filter(
                Badge.user_id == user.id,
                Badge.badge_name == badge_def['name']
            ).first()
            
            if existing:
                continue
                
            # Check if user meets requirements
            earned = False
            
            if badge_def['type'] == 'streak' and user.current_streak >= badge_def.get('req_streak', 0):
                earned = True
            elif badge_def['type'] == 'level' and user.level >= badge_def.get('req_level', 0):
                earned = True
            elif badge_def['type'] == 'activity':
                # Get total activity stats
                activities = session.query(StreakActivity).filter(StreakActivity.user_id == user.id).all()
                total_cards = sum(a.cards_studied for a in activities)
                total_questions = sum(a.questions_answered for a in activities) 
                total_minutes = sum(a.study_minutes for a in activities)
                
                if (badge_def.get('req_cards') and total_cards >= badge_def['req_cards']) or \
                   (badge_def.get('req_questions') and total_questions >= badge_def['req_questions']) or \
                   (badge_def.get('req_minutes') and total_minutes >= badge_def['req_minutes']):
                    earned = True
            
            if earned:
                new_badge = Badge(
                    user_id=user.id,
                    badge_type=badge_def['type'],
                    badge_name=badge_def['name'],
                    badge_description=badge_def['description'],
                    badge_icon=badge_def['icon'],
                    requirements=badge_def,
                    is_featured=badge_def['type'] == 'streak' and badge_def.get('req_streak', 0) >= 7
                )
                session.add(new_badge)
                new_badges.append(new_badge)
                user.total_badges += 1
        
        session.commit()
        return [{'name': b.badge_name, 'icon': b.badge_icon, 'description': b.badge_description} for b in new_badges]
    
    def get_user_badges(self, user_id):
        """Get all user badges"""
        session = self.get_session()
        try:
            badges = session.query(Badge).filter(Badge.user_id == user_id).order_by(Badge.earned_at.desc()).all()
            return [{
                'name': b.badge_name,
                'icon': b.badge_icon, 
                'description': b.badge_description,
                'type': b.badge_type,
                'earned_at': b.earned_at,
                'is_featured': b.is_featured
            } for b in badges]
        finally:
            session.close()
    
    def get_user_streak_data(self, user_id, days=30):
        """Get user's recent streak activity"""
        session = self.get_session()
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            activities = session.query(StreakActivity).filter(
                StreakActivity.user_id == user_id,
                StreakActivity.activity_date >= cutoff_date
            ).order_by(StreakActivity.activity_date.desc()).all()
            
            return [{
                'date': a.activity_date.date(),
                'study_minutes': a.study_minutes,
                'cards_studied': a.cards_studied,
                'questions_answered': a.questions_answered,
                'streak_day': a.streak_day_number
            } for a in activities]
        finally:
            session.close()

# Initialize database manager
@st.cache_resource
def get_db_manager():
    return DatabaseManager()