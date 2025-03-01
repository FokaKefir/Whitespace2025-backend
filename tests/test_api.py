import os 

os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "postgresql://myuser:mypassword@localhost:6666/test_database"

import pytest
import uuid
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal, Base, engine
from app.main import CSRF_TOKEN

def test_check_env():
    assert os.getenv("TESTING") == "1"

@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for each test."""
    Base.metadata.create_all(bind=engine)  # Create tables
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # Clean up after test


@pytest.fixture(scope="function")
def client():
    """Creates a FastAPI test client."""
    return TestClient(app)



def test_create_user(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "userName": "testuser",
        "name": "Test User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }

    response = client.post(
        "/create_user", 
        json=user_data, 
        headers={"CSRF-Token": csrf_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["userName"] == user_data["userName"]
    assert data["name"] == user_data["name"]

def test_create_topic(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    topic_data = {
        "name": "Machine Learning"
    }

    response = client.post(
        "/create_topic", 
        json=topic_data, 
        headers={"CSRF-Token": csrf_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == topic_data["name"]
    assert isinstance(data["id"], int)  # Ensure ID is returned and is an integer


def test_create_course(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    # First, create a topic
    topic_data = {
        "name": "Programming"
    }

    topic_response = client.post(
        "/create_topic",
        json=topic_data,
        headers={"CSRF-Token": csrf_token}
    )

    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]

    # Now, create a course under the topic
    course_data = {
        "name": "Python Course",
        "description": "Learn Python from scratch.",
        "topic_id": topic_id
    }

    response = client.post(
        "/create_course", 
        json=course_data, 
        headers={"CSRF-Token": csrf_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == course_data["name"]
    assert data["description"] == course_data["description"]
    assert data["topic_id"] == topic_id


def test_create_post(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    # First, create a user
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "postuser@example.com",
        "userName": "postuser",
        "name": "Post User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }
    user_response = client.post("/create_user", json=user_data, headers={"CSRF-Token": csrf_token})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Create a topic
    topic_data = {
        "name": "Web Development"
    }
    topic_response = client.post(
        "/create_topic",
        json=topic_data,
        headers={"CSRF-Token": csrf_token}
    )
    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]

    # Create a course under the topic
    course_data = {
        "name": "FastAPI Course",
        "description": "Learn FastAPI step by step.",
        "topic_id": topic_id
    }
    course_response = client.post("/create_course", json=course_data, headers={"CSRF-Token": csrf_token})
    assert course_response.status_code == 200
    course_id = course_response.json()["id"]

    # Now, create a post (including the missing "title" field)
    post_data = {
        "course_id": course_id,
        "author_id": user_id,
        "title": "Getting Started with FastAPI",  
        "preview_md": "Introduction to FastAPI",
        "content_md": "This is a detailed FastAPI tutorial."
    }

    response = client.post(
        "/create_post",
        json=post_data,
        headers={"CSRF-Token": csrf_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["course_id"] == post_data["course_id"]
    assert data["author_id"] == post_data["author_id"]
    assert data["title"] == post_data["title"]  
    assert data["preview_md"] == post_data["preview_md"]
    assert data["content_md"] == post_data["content_md"]

def test_get_topics_with_courses(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    """Test the `/topics_with_courses` endpoint"""
    
    # Create a topic
    topic_data = {
        "name": "Artificial Intelligence"
    }
    topic_response = client.post(
        "/create_topic",
        json=topic_data,
        headers={"CSRF-Token": csrf_token}
    )
    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]

    # Create courses under the topic
    course_data_1 = {
        "name": "Machine Learning Basics",
        "description": "Introduction to ML concepts",
        "topic_id": topic_id
    }
    course_data_2 = {
        "name": "Deep Learning with PyTorch",
        "description": "Building deep neural networks",
        "topic_id": topic_id
    }

    course_response_1 = client.post("/create_course", json=course_data_1, headers={"CSRF-Token": csrf_token})
    course_response_2 = client.post("/create_course", json=course_data_2, headers={"CSRF-Token": csrf_token})

    assert course_response_1.status_code == 200
    assert course_response_2.status_code == 200

    # Fetch topics with courses
    response = client.get("/topics_with_courses", headers={"CSRF-Token": csrf_token})
    assert response.status_code == 200

    data = response.json()
    
    # Check if the topic is in the response
    assert len(data) > 0
    topic_found = next((topic for topic in data if topic["id"] == topic_id), None)
    
    assert topic_found is not None
    assert topic_found["name"] == topic_data["name"]
    
    # Check if the courses are listed correctly
    course_names = {course["name"] for course in topic_found["courses"]}
    assert "Machine Learning Basics" in course_names
    assert "Deep Learning with PyTorch" in course_names