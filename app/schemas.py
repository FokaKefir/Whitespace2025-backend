from pydantic import BaseModel, EmailStr, HttpUrl, Field
from datetime import datetime
from typing import Annotated, Optional


class UserCreate(BaseModel):
    id: Annotated[str, Field(title="User ID", description="A unique identifier for the user")]
    email: Annotated[EmailStr, Field(title="Email", description="Valid email address")]
    userName: Annotated[str, Field(title="Username", min_length=3, max_length=50)]
    name: Annotated[str, Field(title="Full Name", min_length=3, max_length=100)]
    imageUrl: Annotated[HttpUrl, Field(title="Profile Image URL", description="Valid image URL")]
    is_admin: Annotated[bool, Field(title="Admin Status", description="Indicates if the user is an admin", default=False)]


class UserResponse(UserCreate):
    id: Annotated[str, Field(title="User ID", description="A unique identifier for the user")]

    class Config:
        orm_mode = True


class CourseCreate(BaseModel):
    name: Annotated[str, Field(title="Course Name", min_length=3, max_length=100)]
    description: Annotated[Optional[str], Field(title="Course Description", max_length=500, default=None)]


class CourseResponse(CourseCreate):
    id: Annotated[int, Field(title="Course ID", description="Unique identifier for the course")]

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    course_id: Annotated[int, Field(title="Course ID", description="ID of the related course")]
    author_id: Annotated[str, Field(title="Author ID", description="User ID of the post author")]
    preview_md: Annotated[str, Field(title="Preview Content", min_length=10, max_length=500)]
    content_md: Annotated[str, Field(title="Post Content", min_length=10, max_length=5000)]


class PostResponse(PostCreate):
    id: Annotated[int, Field(title="Post ID", description="Unique identifier for the post")]
    created_at: Annotated[datetime, Field(title="Creation Timestamp", description="Timestamp of when the post was created")]

    class Config:
        orm_mode = True
