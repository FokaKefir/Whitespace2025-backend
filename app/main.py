from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, exists
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

BLACKLISTED_IPS = ["111.22.236.7", "178.211.139.120", "130.61.85.118", "23.94.59.211"]

@app.middleware("http")
async def block_bad_ips(request, call_next):
    client_ip = request.client.host
    if client_ip in BLACKLISTED_IPS:
        return JSONResponse(content={"detail": "Blocked"}, status_code=403)
    return await call_next(request)

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

def validate_id(db: Session, model, field: str, value, error_message: str):
    """
    Generic validation function to check if a given ID exists in the database.
    - `model`: SQLAlchemy model (e.g., Post, User, Course, Topic).
    - `field`: Column name to check (e.g., "id").
    - `value`: The value being validated.
    - `error_message`: The error message to return if not found.
    """
    exists = db.query(model).filter(getattr(model, field) == value).first()
    if not exists:
        raise HTTPException(status_code=404, detail=error_message)
    return exists

@app.post("/create_post", response_model=PostAfterCreateResponse, dependencies=[Depends(verify_csrf)])
def create_post(post_data: PostCreate, db: Session = Depends(get_db)) -> PostAfterCreateResponse:
    if not db.query(Course).filter(Course.id == post_data.course_id).first():
        raise HTTPException(status_code=404, detail="Course not found")

    validate_id(db, User, "id", post_data.author_id, "Author not found")
    validate_id(db, Course, "id", post_data.course_id, "Course not found")
    
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
        id=user_data.id,
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
    
    validate_id(db, Topic, "id", course_data.topic_id, "Topic not found")
    
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

@app.get("/topics_with_courses", response_model=list[TopicWithCoursesResponse], dependencies=[Depends(verify_csrf)])
def get_topics_with_courses(user_id: str = Header(..., title="User ID"), db: Session = Depends(get_db)):
    """
    Fetch topics along with courses, marking whether a course is favorited by the user.
    """

    # Get the user's favorite courses
    favorite_course_ids = {
        fav.course_id for fav in db.query(FavoriteCourse).filter(FavoriteCourse.user_id == user_id).all()
    }

    # Fetch all topics with courses
    topics = db.query(Topic).all()
    
    # Format response
    topics_with_courses = []
    for topic in topics:
        topic_data = TopicWithCoursesResponse(
            id=topic.id,
            name=topic.name,
            courses=[
                CourseDetailResponse(
                    id=course.id,
                    name=course.name,
                    description=course.description,
                    is_favorite=course.id in favorite_course_ids  # Mark favorite courses
                )
                for course in topic.courses  # Fetch courses for each topic
            ]
        )
        topics_with_courses.append(topic_data)

    return topics_with_courses


@app.post("/add_favorite_course", dependencies=[Depends(verify_csrf)])
def add_favorite_course(
    user_id: str = Header(..., title="User ID"), 
    course_id: int = Query(..., title="Course ID"), 
    db: Session = Depends(get_db)
):
    """Add a course to favorites"""
    
    validate_id(db, Course, "id", course_id, "Course not found")
    validate_id(db, User, "id", user_id, "User not found")

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing_favorite = db.query(FavoriteCourse).filter(
        FavoriteCourse.user_id == user_id,
        FavoriteCourse.course_id == course_id
    ).first()

    if existing_favorite:
        raise HTTPException(status_code=400, detail="Course already favorited")

    new_favorite = FavoriteCourse(user_id=user_id, course_id=course_id)
    db.add(new_favorite)
    db.commit()

    return {"message": "Course added to favorites"}


@app.delete("/remove_favorite_course", dependencies=[Depends(verify_csrf)])
def remove_favorite_course(
    user_id: str = Header(..., title="User ID"), 
    course_id: int = Query(..., title="Course ID"), 
    db: Session = Depends(get_db)
):
    """Remove a course from favorites"""

    favorite_entry = db.query(FavoriteCourse).filter(
        FavoriteCourse.user_id == user_id,
        FavoriteCourse.course_id == course_id
    ).first()

    if not favorite_entry:
        raise HTTPException(status_code=404, detail="Favorite course not found")

    db.delete(favorite_entry)
    db.commit()

    return {"message": "Course removed from favorites"}


@app.get("/favorite_courses", response_model=list[CourseResponse], dependencies=[Depends(verify_csrf)])
def get_favorite_courses(user_id: str = Header(..., title="User ID"), db: Session = Depends(get_db)):
    """Returns a list of courses that are favorited by the user, marking them explicitly as favorites."""
    
    validate_id(db, User, "id", user_id, "User not found")

    favorite_courses = db.query(Course).join(FavoriteCourse, Course.id == FavoriteCourse.course_id).filter(
        FavoriteCourse.user_id == user_id
    ).all()

    return [
        CourseResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            topic_id=course.topic_id,
            is_favorite=True  
        )
        for course in favorite_courses
    ]


@app.post("/like_post", dependencies=[Depends(verify_csrf)])
def like_post(
    post_id: str = Query(..., title="Post ID"),
    db: Session = Depends(get_db), 
    user_id: str = Header(..., title="User ID")
):
    """Allows a user to like a post if they haven't already."""
    
    validate_id(db, Post, "id", post_id, "Post not found")
    validate_id(db, User, "id", user_id, "User not found")

    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if user has already liked the post
    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id, PostLike.user_id == user_id
    ).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="User has already liked this post")

    new_like = PostLike(user_id=user_id, post_id=post_id)
    db.add(new_like)
    db.commit()

    return {"message": "Post liked successfully"}

@app.delete("/remove_like", dependencies=[Depends(verify_csrf)])
def remove_like(
    post_id: str = Query(..., title="Post ID"),
    db: Session = Depends(get_db), 
    user_id: str = Header(..., title="User ID")
):
    """Allows a user to remove their like from a post."""
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    like = db.query(PostLike).filter(
        PostLike.post_id == post_id, PostLike.user_id == user_id
    ).first()

    if not like:
        raise HTTPException(status_code=400, detail="User has not liked this post")

    db.delete(like)
    db.commit()

    return {"message": "Like removed successfully"}


@app.get("/get_post/{post_id}", response_model=PostResponse, dependencies=[Depends(verify_csrf)])
def get_post(post_id: str, db: Session = Depends(get_db), user_id: str = Header(..., title="User ID")) -> PostResponse:
    """Fetch a post by ID, count likes, check if the user liked it, and return author name."""
    
    post = validate_id(db, Post, "id", post_id, "Post not found")

    author = db.query(User.name).filter(User.id == post.author_id).scalar()
    author_name = author if author else "Unknown User"

    like_count = db.query(func.count(PostLike.user_id)).filter(PostLike.post_id == post_id).scalar()
    liked_by_user = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == user_id).first() is not None

    return PostResponse(
        id=post.id,
        course_id=post.course_id,
        author_id=post.author_id,
        author_name=author_name,
        title=post.title,
        preview_md=post.preview_md,
        content_md=post.content_md,
        created_at=post.created_at,
        like_count=like_count,
        liked_by_user=liked_by_user
    )

@app.get("/posts", response_model=list[PostResponse], dependencies=[Depends(verify_csrf)])
def get_all_posts(
    user_id: str = Header(..., title="User ID"),
    course_id: Optional[int] = Query(None, description="Filter posts by course ID"),  # New optional filter
    sort_by_likes: bool = Query(False, description="Sort posts by like count"),
    limit: int = Query(None, description="Limit the number of returned posts"),
    db: Session = Depends(get_db)
):
    """
    Retrieves posts along with like counts, author names, and whether the user has liked them.
    - Defaults to ordering by `created_at` (newest first).
    - If `sort_by_likes=true`, orders by like count instead.
    - If `course_id` is provided, only posts from that course are returned.
    - If `limit` is provided, only the first `limit` posts are returned.
    """

    if course_id:
        validate_id(db, Course, "id", course_id, "Course not found")

    # Subquery for like count
    subquery_like_count = db.query(
        PostLike.post_id, func.count(PostLike.user_id).label("like_count")
    ).group_by(PostLike.post_id).subquery()

    # Subquery for checking if the user has liked a post
    subquery_liked_by_user = db.query(
        PostLike.post_id
    ).filter(PostLike.user_id == user_id).subquery()

    # Query for posts
    query = (
        db.query(
            Post,
            User.name.label("author_name"),  # Fetch author name
            func.coalesce(subquery_like_count.c.like_count, 0).label("like_count"),
            exists().where(subquery_liked_by_user.c.post_id == Post.id).label("liked_by_user"),
        )
        .join(User, User.id == Post.author_id)
        .outerjoin(subquery_like_count, Post.id == subquery_like_count.c.post_id)
    )

    # Apply course_id filter if provided
    if course_id is not None:
        query = query.filter(Post.course_id == course_id)

    # Sorting logic
    if sort_by_likes:
        query = query.order_by(func.coalesce(subquery_like_count.c.like_count, 0).desc())  # Order by likes
    else:
        query = query.order_by(Post.created_at.desc())  # Default: order by timestamp

    # Apply limit if provided
    if limit is not None:
        query = query.limit(limit)

    posts = query.all()

    return [
        PostResponse(
            id=post.id,
            course_id=post.course_id,
            author_id=post.author_id,
            author_name=author_name,  # Return author name
            title=post.title,
            preview_md=post.preview_md,
            content_md=post.content_md,
            created_at=post.created_at,
            like_count=like_count,
            liked_by_user=liked_by_user
        )
        for post, author_name, like_count, liked_by_user in posts
    ]


@app.post("/add_comment", response_model=CommentResponse, dependencies=[Depends(verify_csrf)])
def add_comment(comment_data: CommentCreate, user_id: str = Header(..., title="User ID"), db: Session = Depends(get_db)):
    """Allows a user to add a comment to a post."""

    validate_id(db, User, "id", user_id, "User not found")
    validate_id(db, Post, "id", comment_data.post_id, "Post not found")

    # Create new comment
    new_comment = PostComment(
        post_id=comment_data.post_id,
        user_id=user_id,
        content=comment_data.content,
        created_at=datetime.utcnow()
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # Fetch user_name from the User table
    user_name = db.query(User.userName).filter(User.id == user_id).scalar()

    return CommentResponse(
        id=new_comment.id,
        post_id=new_comment.post_id,
        user_id=new_comment.user_id,
        user_name=user_name,  # Include user_name in the response
        content=new_comment.content,
        created_at=new_comment.created_at,
        is_written_by_user=True  # Since the user just created it, they must be the author
    )



@app.delete("/remove_comment", dependencies=[Depends(verify_csrf)])
def remove_comment(comment_id: int = Query(..., title="Comment ID"), user_id: str = Header(..., title="User ID"), db: Session = Depends(get_db)):
    """Allows a user to remove their own comment."""

    comment = db.query(PostComment).filter(PostComment.id == comment_id, PostComment.user_id == user_id).first()

    if not comment:
        raise HTTPException(status_code=403, detail="Comment not found or you do not have permission to delete it")

    db.delete(comment)
    db.commit()

    return {"message": "Comment removed successfully"}


@app.get("/get_comments", response_model=list[CommentResponse], dependencies=[Depends(verify_csrf)])
def get_comments(
    post_id: str = Query(..., title="Post ID"),
    user_id: str = Header(..., title="User ID"),
    db: Session = Depends(get_db)
):
    """Retrieve all comments for a given post, including user_name for each comment author."""

    validate_id(db, Post, "id", post_id, "Post not found")

    # Fetch comments along with user_name by joining PostComment with User
    comments = (
        db.query(
            PostComment.id,
            PostComment.post_id,
            PostComment.user_id,
            User.userName.label("user_name"),  # Get username
            PostComment.content,
            PostComment.created_at
        )
        .join(User, User.id == PostComment.user_id)  # Join User table to get user_name
        .filter(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.asc())  # Order by timestamp, oldest first
        .all()
    )

    # Format response with username and is_written_by_user flag
    return [
        CommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            user_id=comment.user_id,
            user_name=comment.user_name,  # Extract user_name from query
            content=comment.content,
            created_at=comment.created_at,
            is_written_by_user=(comment.user_id == user_id)  # True if the comment belongs to the requester
        )
        for comment in comments
    ]
