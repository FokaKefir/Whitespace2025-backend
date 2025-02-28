import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, nullable=False)
    userName = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    imageUrl = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)

    # Relationships
    comments = relationship("PostComment", back_populates="user")
    likes = relationship("PostLike", back_populates="user")

# Course Table
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    # Relationships
    posts = relationship("Post", back_populates="course")

# Post Table
class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)  # ✅ Fix: Use String for UUID
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)  
    preview_md = Column(String, nullable=False)
    content_md = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # ✅ Fix: Use DateTime

    # Relationships
    course = relationship("Course", back_populates="posts")
    author = relationship("User")
    comments = relationship("PostComment", back_populates="post")
    likes = relationship("PostLike", back_populates="post")

# Post_Comment Table
class PostComment(Base):
    __tablename__ = "post_comments"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), primary_key=True)  # ✅ Fix: Match `Post.id` type
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

# Post_Like Table
class PostLike(Base):
    __tablename__ = "post_likes"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), primary_key=True)  # ✅ Fix: Match `Post.id` type

    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
