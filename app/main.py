from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import *
from app.schemas import *

# FastAPI app
app = FastAPI()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@app.post("/create_post", response_model=PostResponse)
def create_post(post_data: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    new_post: Post = Post(
        course_id=post_data.course_id,
        author_id=post_data.author_id,
        preview_md=post_data.preview_md,
        content_md=post_data.content_md,
        created_at=datetime.utcnow()
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post) 

    return new_post


@app.post("/create_user", response_model=UserResponse)
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
    db.refresh(new_user)  # Reload the object to get the generated ID

    return new_user


@app.post("/create_course", response_model=CourseResponse)
def create_course(course_data: CourseCreate, db: Session = Depends(get_db)) -> CourseResponse:
    new_course: Course = Course(
        name=course_data.name,
        description=course_data.description
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)  # Reload the object to get the generated ID

    return new_course