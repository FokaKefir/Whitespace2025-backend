import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from sqlalchemy.orm import Session
from app.models import User, Course, Post
import uuid


# ✅ Setup Test Database
@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for each test."""
    Base.metadata.create_all(bind=engine)  # Create tables
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # Clean up after test


# ✅ Setup Test Client
@pytest.fixture(scope="function")
def client():
    """Creates a FastAPI test client."""
    return TestClient(app)


# ✅ Test Creating a User
def test_create_user(client: TestClient, db_session: Session):
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "userName": "testuser",
        "name": "Test User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }
    
    response = client.post("/create_user", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["userName"] == user_data["userName"]
    assert data["name"] == user_data["name"]


# ✅ Test Creating a Duplicate User (Should Fail)
def test_create_duplicate_user(client: TestClient, db_session: Session):
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "duplicate@example.com",
        "userName": "duplicateuser",
        "name": "Duplicate User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }

    client.post("/create_user", json=user_data)  # First request (should pass)
    response = client.post("/create_user", json=user_data)  # Second request (should fail)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email or Username already exists"


# ✅ Test Creating a Course
def test_create_course(client: TestClient, db_session: Session):
    course_data = {
        "name": "Python Course",
        "description": "Learn Python from scratch."
    }
    
    response = client.post("/create_course", json=course_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == course_data["name"]
    assert data["description"] == course_data["description"]


# ✅ Test Creating a Post
def test_create_post(client: TestClient, db_session: Session):
    # First, create a user
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "postuser@example.com",
        "userName": "postuser",
        "name": "Post User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }
    user_response = client.post("/create_user", json=user_data)
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Then, create a course
    course_data = {
        "name": "FastAPI Course",
        "description": "Learn FastAPI step by step."
    }
    course_response = client.post("/create_course", json=course_data)
    assert course_response.status_code == 200
    course_id = course_response.json()["id"]

    # Now, create a post
    post_data = {
        "course_id": course_id,
        "author_id": user_id,
        "preview_md": "Introduction to FastAPI",
        "content_md": "This is a detailed FastAPI tutorial."
    }

    response = client.post("/create_post", json=post_data)
    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == post_data["course_id"]
    assert data["author_id"] == post_data["author_id"]
    assert data["preview_md"] == post_data["preview_md"]
    assert data["content_md"] == post_data["content_md"]
