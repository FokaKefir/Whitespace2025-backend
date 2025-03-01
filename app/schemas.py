from pydantic import BaseModel, EmailStr, HttpUrl, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Annotated, Optional, List


class UserCreate(BaseModel):
    id: Annotated[str, Field(title="User ID", description="A unique identifier for the user")]
    email: Annotated[EmailStr, Field(title="Email", description="Valid email address")]
    userName: Annotated[str, Field(title="Username", min_length=3, max_length=50)]
    name: Annotated[str, Field(title="Full Name", min_length=3, max_length=100)]
    imageUrl: Annotated[str, Field(title="Profile Image URL", description="Valid image URL")]
    is_admin: Annotated[bool, Field(title="Admin Status", description="Indicates if the user is an admin", default=False)]


class UserResponse(UserCreate):
    id: Annotated[str, Field(title="User ID", description="A unique identifier for the user")]

    model_config = ConfigDict(from_attributes=True)



class CourseCreate(BaseModel):
    name: Annotated[str, Field(title="Course Name", min_length=3, max_length=100)]
    description: Annotated[Optional[str], Field(title="Course Description", max_length=500, default=None)]
    topic_id: Annotated[int, Field(title="Topic ID", description="The ID of the related topic")]


class CourseResponse(CourseCreate):
    id: Annotated[int, Field(title="Course ID", description="Unique identifier for the course")]
    is_favorite: bool = False

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    course_id: Annotated[int, Field(title="Course ID", description="ID of the related course")]
    author_id: Annotated[str, Field(title="Author ID", description="User ID of the post author")]
    title: Annotated[str, Field(title="Title of Post", min_length=3, max_length=100)]
    preview_md: Annotated[str, Field(title="Preview Content", min_length=10, max_length=500)]
    content_md: Annotated[str, Field(title="Post Content", min_length=10, max_length=5000)]
    
    @field_validator("course_id")
    def validate_course(cls, v):
        if v <= 0:
            raise ValueError("Invalid course ID")
        return v

    @field_validator("author_id")
    def validate_author(cls, v):
        if not v or len(v) < 5:
            raise ValueError("Invalid author ID")
        return v

class PostAfterCreateResponse(BaseModel):
    id: str  
    course_id: int
    author_id: str
    title: str
    preview_md: str
    content_md: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PostResponse(BaseModel):
    id: str
    course_id: int
    author_id: str
    author_name: str  # Added author name
    title: str
    preview_md: str
    content_md: str
    created_at: datetime
    like_count: int  # Total number of likes
    liked_by_user: bool  # Whether the logged-in user liked the post

    model_config = ConfigDict(from_attributes=True)


class TopicCreate(BaseModel):
    name: Annotated[str, Field(title="Topic Name", min_length=3, max_length=100)]

class TopicResponse(TopicCreate):
    id: Annotated[int, Field(title="Topic ID", description="Unique identifier for the topic")]

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_favorite: bool = False  

    model_config = ConfigDict(from_attributes=True)



class TopicWithCoursesResponse(BaseModel):
    id: int
    name: str
    courses: List[CourseDetailResponse]  # Updated reference to the new course schema

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    post_id: str
    content: str

class CommentResponse(BaseModel):
    id: int
    post_id: str
    user_id: str
    user_name: str  
    content: str
    created_at: datetime
    is_written_by_user: bool  
