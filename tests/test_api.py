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

def test_add_and_remove_favorite_course(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    """Test adding and removing a course from favorites"""

    # Create a user
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "userName": "testuser",
        "name": "Test User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }
    user_response = client.post("/create_user", json=user_data, headers={"CSRF-Token": csrf_token})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Create a topic
    topic_data = {"name": "Machine Learning"}
    topic_response = client.post("/create_topic", json=topic_data, headers={"CSRF-Token": csrf_token})
    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]

    # Create a course under the topic
    course_data = {"name": "Deep Learning", "description": "Learn Deep Learning", "topic_id": topic_id}
    course_response = client.post("/create_course", json=course_data, headers={"CSRF-Token": csrf_token})
    assert course_response.status_code == 200
    course_id = course_response.json()["id"]

    # Add course to favorites
    favorite_response = client.post(
        "/add_favorite_course",
        params={"course_id": course_id},  
        headers={"CSRF-Token": csrf_token, "User-ID": user_id}
    )
    assert favorite_response.status_code == 200
    assert favorite_response.json()["message"] == "Course added to favorites"

    # Try adding the same course again (should fail)
    duplicate_favorite_response = client.post(
        "/add_favorite_course",  
        params={"course_id": course_id}, 
        headers={"CSRF-Token": csrf_token, "User-ID": user_id}
    )
    assert duplicate_favorite_response.status_code == 400
    assert duplicate_favorite_response.json()["detail"] == "Course already favorited"

    # Remove course from favorites
    remove_favorite_response = client.delete(
        "/remove_favorite_course",  
        params={"course_id": course_id}, 
        headers={"CSRF-Token": csrf_token, "User-ID": user_id}
    )
    assert remove_favorite_response.status_code == 200
    assert remove_favorite_response.json()["message"] == "Course removed from favorites"

    # Try removing again (should fail)
    remove_favorite_fail_response = client.delete(
        "/remove_favorite_course",  
        params={"course_id": course_id}, 
        headers={"CSRF-Token": csrf_token, "User-ID": user_id}
    )
    assert remove_favorite_fail_response.status_code == 404
    assert remove_favorite_fail_response.json()["detail"] == "Favorite course not found"


def test_get_favorite_courses(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    """Test retrieving a list of favorite courses for a user."""

    # Create a user
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "testuser@example.com",
        "userName": "testuser",
        "name": "Test User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }
    user_response = client.post("/create_user", json=user_data, headers={"CSRF-Token": csrf_token})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Create a topic
    topic_data = {"name": "Web Development"}
    topic_response = client.post("/create_topic", json=topic_data, headers={"CSRF-Token": csrf_token})
    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]

    # Create two courses under the topic
    course_data_1 = {
        "name": "FastAPI Masterclass",
        "description": "Learn FastAPI from scratch",
        "topic_id": topic_id
    }
    course_response_1 = client.post("/create_course", json=course_data_1, headers={"CSRF-Token": csrf_token})
    assert course_response_1.status_code == 200
    course_id_1 = course_response_1.json()["id"]

    course_data_2 = {
        "name": "Advanced Python",
        "description": "Deep dive into Python features",
        "topic_id": topic_id
    }
    course_response_2 = client.post("/create_course", json=course_data_2, headers={"CSRF-Token": csrf_token})
    assert course_response_2.status_code == 200
    course_id_2 = course_response_2.json()["id"]

    # Add courses to favorites
    client.post("/add_favorite_course", params={"course_id": course_id_1}, headers={"CSRF-Token": csrf_token, "User-ID": user_id})
    client.post("/add_favorite_course", params={"course_id": course_id_2}, headers={"CSRF-Token": csrf_token, "User-ID": user_id})

    # Fetch favorite courses
    favorite_response = client.get("/favorite_courses", headers={"CSRF-Token": csrf_token, "User-ID": user_id})
    
    assert favorite_response.status_code == 200
    favorite_courses = favorite_response.json()
    
    assert len(favorite_courses) == 2
    assert favorite_courses[0]["name"] in ["FastAPI Masterclass", "Advanced Python"]
    assert favorite_courses[1]["name"] in ["FastAPI Masterclass", "Advanced Python"]


def test_like_and_remove_like(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    """Test liking and unliking a post."""
    
    # Create a user
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "testuser@example.com",
        "userName": "testuser",
        "name": "Test User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }
    user_response = client.post("/create_user", json=user_data, headers={"CSRF-Token": csrf_token})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Create a topic
    topic_data = {"name": "Backend Development"}
    topic_response = client.post("/create_topic", json=topic_data, headers={"CSRF-Token": csrf_token})
    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]

    # Create a course
    course_data = {
        "name": "FastAPI Masterclass",
        "description": "Learn FastAPI from scratch",
        "topic_id": topic_id
    }
    course_response = client.post("/create_course", json=course_data, headers={"CSRF-Token": csrf_token})
    assert course_response.status_code == 200
    course_id = course_response.json()["id"]

    # Create a post
    post_data = {
        "course_id": course_id,
        "author_id": user_id,
        "title": "Introduction to FastAPI",
        "preview_md": "What is FastAPI?",
        "content_md": "FastAPI is a modern web framework for building APIs."
    }
    post_response = client.post("/create_post", json=post_data, headers={"CSRF-Token": csrf_token})
    assert post_response.status_code == 200
    post_id = post_response.json()["id"]

    # Like the post (using `params` instead of `json`)
    like_response = client.post(
        "/like_post", 
        params={"post_id": post_id},
        headers={"CSRF-Token": csrf_token, "User-ID": user_id}
    )
    assert like_response.status_code == 200
    assert like_response.json()["message"] == "Post liked successfully"

    # Unlike the post (using `params` instead of `json`)
    unlike_response = client.delete(
        "/remove_like",
        params={"post_id": post_id},
        headers={"CSRF-Token": csrf_token, "User-ID": user_id}
    )
    assert unlike_response.status_code == 200
    assert unlike_response.json()["message"] == "Like removed successfully"


def test_get_post(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    """Test fetching a post along with its like count and user like status."""
    
    # Create a user
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "testuser@example.com",
        "userName": "testuser",
        "name": "Test User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }
    user_response = client.post("/create_user", json=user_data, headers={"CSRF-Token": csrf_token})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Create a second user (who won't like the post)
    user_data2 = {
        "id": str(uuid.uuid4()),
        "email": "otheruser@example.com",
        "userName": "otheruser",
        "name": "Other User",
        "imageUrl": "https://example.com/image2.jpg",
        "is_admin": False
    }
    user_response2 = client.post("/create_user", json=user_data2, headers={"CSRF-Token": csrf_token})
    assert user_response2.status_code == 200
    other_user_id = user_response2.json()["id"]

    # Create a topic
    topic_data = {"name": "Software Engineering"}
    topic_response = client.post("/create_topic", json=topic_data, headers={"CSRF-Token": csrf_token})
    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]

    # Create a course
    course_data = {
        "name": "REST API Development",
        "description": "Learn to build APIs with FastAPI",
        "topic_id": topic_id
    }
    course_response = client.post("/create_course", json=course_data, headers={"CSRF-Token": csrf_token})
    assert course_response.status_code == 200
    course_id = course_response.json()["id"]

    # Create a post
    post_data = {
        "course_id": course_id,
        "author_id": user_id,
        "title": "Building APIs with FastAPI",
        "preview_md": "Introduction to FastAPI",
        "content_md": "This tutorial explains FastAPI in detail."
    }
    post_response = client.post("/create_post", json=post_data, headers={"CSRF-Token": csrf_token})
    assert post_response.status_code == 200
    post_id = post_response.json()["id"]

    # Add a like from the first user
    client.post(
        "/like_post",
        params={"post_id": post_id},
        headers={"CSRF-Token": csrf_token, "User-ID": user_id}
    )

    # Fetch the post **as the user who liked it**
    response = client.get(f"/get_post/{post_id}", headers={"CSRF-Token": csrf_token, "User-ID": user_id})
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == "Building APIs with FastAPI"
    assert data["preview_md"] == "Introduction to FastAPI"
    assert data["content_md"] == "This tutorial explains FastAPI in detail."
    assert data["like_count"] == 1  # Post has one like
    assert data["liked_by_user"] is True  # User liked it

    # Fetch the post **as another user who didn't like it**
    response = client.get(f"/get_post/{post_id}", headers={"CSRF-Token": csrf_token, "User-ID": other_user_id})
    assert response.status_code == 200

    data = response.json()
    assert data["like_count"] == 1  # Total likes remain the same
    assert data["liked_by_user"] is False  # This user didn't like the post


def test_get_all_posts(client: TestClient, db_session: Session, csrf_token: str = CSRF_TOKEN):
    """Test retrieving all posts with sorting and limit options."""

    # Create a user
    user_data = {
        "id": str(uuid.uuid4()),
        "email": "testuser@example.com",
        "userName": "testuser",
        "name": "Test User",
        "imageUrl": "https://example.com/image.jpg",
        "is_admin": False
    }
    user_response = client.post("/create_user", json=user_data, headers={"CSRF-Token": csrf_token})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    # Create a topic
    topic_data = {"name": "Web Development"}
    topic_response = client.post("/create_topic", json=topic_data, headers={"CSRF-Token": csrf_token})
    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]

    # Create a course
    course_data = {
        "name": "FastAPI Course",
        "description": "Learn FastAPI step by step.",
        "topic_id": topic_id
    }
    course_response = client.post("/create_course", json=course_data, headers={"CSRF-Token": csrf_token})
    assert course_response.status_code == 200
    course_id = course_response.json()["id"]

    # Create multiple posts
    post_ids = []
    for i in range(5):
        post_data = {
            "course_id": course_id,
            "author_id": user_id,
            "title": f"Post {i+1}",
            "preview_md": f"Preview {i+1} one two three",
            "content_md": f"Content of post {i+1}",
        }
        post_response = client.post("/create_post", json=post_data, headers={"CSRF-Token": csrf_token})
        assert post_response.status_code == 200
        post_ids.append(post_response.json()["id"])

    # Like the first post twice
    client.post("/like_post", params={"post_id": post_ids[0]}, headers={"CSRF-Token": csrf_token, "User-ID": user_id})
    client.post("/like_post", params={"post_id": post_ids[0]}, headers={"CSRF-Token": csrf_token, "User-ID": user_id})

    # Fetch all posts (default sorting by time)
    posts_response = client.get("/posts", headers={"CSRF-Token": csrf_token, "User-ID": user_id})
    assert posts_response.status_code == 200
    posts = posts_response.json()
    assert len(posts) == 5

    # Check order by created_at (newest first)
    assert posts[0]["created_at"] >= posts[1]["created_at"]

    # Fetch posts sorted by likes
    posts_response_likes = client.get("/posts?sort_by_likes=true", headers={"CSRF-Token": csrf_token, "User-ID": user_id})
    assert posts_response_likes.status_code == 200
    posts_sorted_by_likes = posts_response_likes.json()

    # Check if sorting by likes works
    assert posts_sorted_by_likes[0]["like_count"] >= posts_sorted_by_likes[1]["like_count"]

    # Fetch only 3 posts (limit)
    posts_response_limited = client.get("/posts?limit=3", headers={"CSRF-Token": csrf_token, "User-ID": user_id})
    assert posts_response_limited.status_code == 200
    posts_limited = posts_response_limited.json()
    assert len(posts_limited) == 3