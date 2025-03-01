import os

# Set up test environment variables
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "postgresql://myuser:mypassword@localhost:6666/test_database"

import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app, get_db, CSRF_TOKEN
from app.database import SessionLocal, Base, engine
from app.models import *
from sqlalchemy.orm import Session

# Test client
client = TestClient(app)

@pytest.fixture(scope="session")
def db_session():
    """Creates the database schema once per test session."""
    Base.metadata.drop_all(bind=engine)  # Cleanup
    Base.metadata.create_all(bind=engine)  # Create fresh tables
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # Cleanup


# ========== Helper Functions ==========

def create_user(db: Session):
    """Creates and returns a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="testuser@example.com",
        userName="testuser",
        name="Test User",
        imageUrl="https://example.com/image.jpg",
        is_admin=False
    )
    db.add(user)
    db.commit()
    return user

def create_topic(db: Session):
    """Creates and returns a test topic."""
    topic = Topic(name="Test Topic")
    db.add(topic)
    db.commit()
    return topic

def create_course(db: Session, topic_id: int):
    """Creates and returns a test course under the given topic."""
    course = Course(name="Test Course", description="A test course", topic_id=topic_id)
    db.add(course)
    db.commit()
    return course

def create_post(db: Session, course_id: int, author_id: str):
    """Creates and returns a test post."""
    post = Post(
        course_id=course_id,
        author_id=author_id,
        title="Test Post",
        preview_md="Preview content",
        content_md="Full content"
    )
    db.add(post)
    db.commit()
    return post

@pytest.fixture(scope="function")
def setup_data(db_session):
    """Setup initial data for tests: user, topic, course, post"""
    user = create_user(db_session)
    topic = create_topic(db_session)
    course = create_course(db_session, topic.id)
    post = create_post(db_session, course.id, user.id)
    return {
        "user": user,
        "topic": topic,
        "course": course,
        "post": post
    }

# ========== TESTS ==========

def test_get_post_valid(setup_data):
    """Test fetching a valid post"""
    response = client.get(
        f"/get_post/{setup_data['post'].id}",
        headers={"CSRF-Token": CSRF_TOKEN, "User-ID": setup_data["user"].id}
    )
    assert response.status_code == 200
    assert response.json()["id"] == setup_data["post"].id

def test_get_post_invalid():
    """Test fetching a non-existing post"""
    response = client.get(
        "/get_post/invalid-post-id",
        headers={"CSRF-Token": CSRF_TOKEN, "User-ID": "some-user-id"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"



def test_get_all_posts_invalid_course():
    """Test fetching posts with an invalid course_id filter"""
    response = client.get(
        "/posts?course_id=99999",
        headers={"CSRF-Token": CSRF_TOKEN, "User-ID": "some-user-id"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_like_post_invalid():
    """Test liking an invalid post"""
    response = client.post(
        "/like_post?post_id=invalid-post-id",
        headers={"CSRF-Token": CSRF_TOKEN, "User-ID": "some-user-id"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


