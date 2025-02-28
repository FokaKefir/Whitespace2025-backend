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
    fav_courses = relationship("FavoriteCourse", back_populates="user")


# Topic Table
class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Relationships
    courses = relationship("Course", back_populates="topic")


# Course Table
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    description = Column(Text)

    # Relationships
    posts = relationship("Post", back_populates="course")
    topic = relationship("Topic", back_populates="courses")
    fav_courses = relationship("FavoriteCourse", back_populates="course")


# Post Table
class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    preview_md = Column(String, nullable=False)
    content_md = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="posts")
    author = relationship("User")
    comments = relationship("PostComment", back_populates="post")
    likes = relationship("PostLike", back_populates="post")


# Post_Comment Table
class PostComment(Base):
    __tablename__ = "post_comments"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


# Post_Like Table
class PostLike(Base):
    __tablename__ = "post_likes"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), primary_key=True)

    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")


# Favorite_Course Table (Fixed course_id type to match Course.id)
class FavoriteCourse(Base):
    __tablename__ = "fav_courses"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)  # Fixed type

    # Relationships
    user = relationship("User", back_populates="fav_courses")
    course = relationship("Course", back_populates="fav_courses")
