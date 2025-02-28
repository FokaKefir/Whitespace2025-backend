from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import *
from app.schemas import *
import os

# FastAPI app
app = FastAPI()

origins = [
    "http://localhost:3000",  # React Frontend (Change in production)
    "http://127.0.0.1:3000",
    "*",  # Allow all origins (Use carefully)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Which origins can access the API
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers (including `X-CSRF-Token`)
)

CSRF_TOKEN = "lofasz"

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_csrf(csrf_token: str = Header(None)):
    if csrf_token != CSRF_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid CSRF Token")

@app.post("/create_post", response_model=PostResponse, dependencies=[Depends(verify_csrf)])
def create_post(post_data: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    new_post = Post(
        course_id=post_data.course_id,
        author_id=post_data.author_id,
        title=post_data.title, 
        preview_md=post_data.preview_md,
        content_md=post_data.content_md,
        created_at=datetime.utcnow()
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post) 

    return new_post


@app.post("/create_user", response_model=UserResponse, dependencies=[Depends(verify_csrf)])
def create_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    # Check if email or username already exists
    existing_user: User | None = db.query(User).filter(
        (User.email == user_data.email) | (User.userName == user_data.userName)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email or Username already exists")

    new_user: User = User(
        email=user_data.email,
        userName=user_data.userName,
        name=user_data.name,
        imageUrl=user_data.imageUrl,
        is_admin=user_data.is_admin
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user) 

    return new_user


@app.post("/create_course", response_model=CourseResponse, dependencies=[Depends(verify_csrf)])
def create_course(course_data: CourseCreate, db: Session = Depends(get_db)) -> CourseResponse:
    new_course: Course = Course(
        name=course_data.name,
        description=course_data.description,
        topic_id=course_data.topic_id
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)  # Reload the object to get the generated ID

    return new_course

@app.post("/create_topic", response_model=TopicResponse, dependencies=[Depends(verify_csrf)])
def create_topic(topic_data: TopicCreate, db: Session = Depends(get_db)) -> TopicResponse:
    new_topic: Topic = Topic(
        name=topic_data.name
    )

    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)  # Reload the object to get the generated ID

    return new_topic
