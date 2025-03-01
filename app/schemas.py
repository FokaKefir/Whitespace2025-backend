from pydantic import BaseModel, EmailStr, HttpUrl, Field, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    course_id: Annotated[int, Field(title="Course ID", description="ID of the related course")]
    author_id: Annotated[str, Field(title="Author ID", description="User ID of the post author")]
    title: Annotated[str, Field(title="Title of Post", min_length=3, max_length=100)]
    preview_md: Annotated[str, Field(title="Preview Content", min_length=10, max_length=500)]
    content_md: Annotated[str, Field(title="Post Content", min_length=10, max_length=5000)]


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

    model_config = ConfigDict(from_attributes=True)


class TopicWithCoursesResponse(BaseModel):
    id: int
    name: str
    courses: List[CourseDetailResponse]  # Updated reference to the new course schema

    model_config = ConfigDict(from_attributes=True)