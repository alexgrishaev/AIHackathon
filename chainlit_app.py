"""
Direct entrypoint for Chainlit application.
This file is used for deployment on Render.com.
"""

import os
import sys
import uuid

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Chainlit packages first
import chainlit as cl
from chainlit.types import AskFileResponse
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from typing import Dict, List

# Load environment variables
load_dotenv()

# Now we can import from the app package
from app.models.models import User, Conversation, Message
from app.database.connection import get_db


# Get database session
db_generator = get_db()
db: Session = next(db_generator)

# Global variable for current conversation - only use in development!
# In production, you would use proper user authentication and session management
CURRENT_CONVERSATION_ID = None
CURRENT_USER_ID = None


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session when a user starts a conversation."""
    global CURRENT_CONVERSATION_ID, CURRENT_USER_ID
    
    # Get user count from database
    try:
        user_count = db.query(User).count()
        conversation_count = db.query(Conversation).count()
        message_count = db.query(Message).count()
        db_stats = f"Current system stats: {user_count} users, {conversation_count} conversations, {message_count} total messages."
    except Exception as e:
        db_stats = f"Could not retrieve database statistics: {str(e)}"
    
    # Send initial message with user count
    await cl.Message(
        content=f"Welcome to AIHackathon! How can I help you today?\n\n_System: {db_stats}_",
        author="AIHackathon Bot"
    ).send()
    
    # Initialize conversation in database
    try:
        # In a real app, you'd get the user from auth context
        user = db.query(User).filter(User.username == 'demo_user').first()
        if not user:
            user = User(username='demo_user', email='demo@example.com')
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create a unique conversation title with timestamp
        import datetime
        conversation_title = f"Conversation {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        conversation = Conversation(user_id=user.id, title=conversation_title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        # Store conversation ID in global variable (for development only)
        CURRENT_CONVERSATION_ID = conversation.id
        CURRENT_USER_ID = user.id
        
        print(f"Started new conversation with ID: {CURRENT_CONVERSATION_ID}")
        
    except Exception as e:
        print(f"Error initializing conversation: {e}")
        # Log error but continue with chat


@cl.on_message
async def on_message(message):
    """Handle incoming user messages."""
    global CURRENT_CONVERSATION_ID
    
    # Check if we have a current conversation
    if not CURRENT_CONVERSATION_ID:
        # If missing, create a new conversation
        try:
            user = db.query(User).filter(User.username == 'demo_user').first()
            if not user:
                user = User(username='demo_user', email='demo@example.com')
                db.add(user)
                db.commit()
                db.refresh(user)
            
            conversation = Conversation(user_id=user.id, title=f"Recovered conversation {uuid.uuid4().hex[:8]}")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            CURRENT_CONVERSATION_ID = conversation.id
            print(f"Created recovery conversation with ID: {CURRENT_CONVERSATION_ID}")
        except Exception as e:
            print(f"Error creating recovery conversation: {e}")
            await cl.Message(
                content="Error creating conversation. Please refresh the page and try again.",
                author="System"
            ).send()
            return
    
    # Debug message objects
    print(f"Message type: {type(message)}")
    
    # Safely extract message content
    if isinstance(message, str):
        message_content = message
    elif hasattr(message, 'content'):
        message_content = message.content
    else:
        message_content = str(message)
    
    print(f"Extracted message content: {message_content[:50]}...")
    
    # Store message in database with proper transaction handling
    try:
        # Start a fresh transaction
        db.rollback()  # Roll back any failed transaction
        
        db_message = Message(
            conversation_id=CURRENT_CONVERSATION_ID,
            role="user",
            content=message_content
        )
        db.add(db_message)
        db.commit()
    except Exception as e:
        db.rollback()  # Important: Roll back on error
        print(f"Error storing message: {e}")
    
    # Process the message (in a real app, you'd call your AI model here)
    response_content = f"You said: {message_content}\n\nThis is a demo response. In a real application, this would be processed by an AI model."
    
    # Send response
    response = cl.Message(content=response_content)
    await response.send()
    
    # Store response in database with proper transaction handling
    try:
        # Ensure we're in a clean transaction state
        db.rollback()  # Roll back any failed transaction
        
        db_response = Message(
            conversation_id=CURRENT_CONVERSATION_ID,
            role="assistant",
            content=response_content
        )
        db.add(db_response)
        db.commit()
    except Exception as e:
        db.rollback()  # Important: Roll back on error
        print(f"Error storing response: {e}")


# Register a cleanup function using atexit to ensure DB connection is closed
import atexit

def cleanup_db_session():
    """Clean up database connections when the application exits."""
    try:
        db.close()
        print("Database session closed successfully")
    except Exception as e:
        print(f"Error closing database session: {e}")

# Register the cleanup function
atexit.register(cleanup_db_session)