import sys
import os
import random
import uuid
from datetime import datetime
from faker import Faker
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import User, Topic, Course, Post, PostComment, PostLike, FavoriteCourse

# Ensure the script can find the `app` package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

fake = Faker()


# ✅ **Function to delete all existing data before generating new fake data**
def delete_all_data(db: Session):
    """Deletes all data from tables in the correct order to prevent constraint errors."""
    print("Deleting all existing data...")
    
    db.execute(PostLike.__table__.delete())
    db.execute(PostComment.__table__.delete())
    db.execute(Post.__table__.delete())
    db.execute(FavoriteCourse.__table__.delete())
    db.execute(Course.__table__.delete())
    db.execute(Topic.__table__.delete())
    db.execute(User.__table__.delete())

    db.commit()
    print("All data deleted!")


# ✅ **Generate Fake Users**
def create_fake_users(db: Session, num_users=10):
    print("Generating users...")
    users = []
    for _ in range(num_users):
        user = User(
            id=str(uuid.uuid4()),
            email=fake.unique.email(),
            userName=fake.unique.user_name(),
            name=fake.name(),
            imageUrl=fake.image_url(),
            is_admin=random.choice([True, False])
        )
        db.add(user)
        users.append(user)
    db.commit()
    return users


# ✅ **Generate Fake Topics**
def create_fake_topics(db: Session, num_topics=5):
    print("Generating topics...")
    topics = []
    for _ in range(num_topics):
        topic = Topic(
            name=fake.word().capitalize()
        )
        db.add(topic)
        topics.append(topic)
    db.commit()
    return topics


# ✅ **Generate Fake Courses**
def create_fake_courses(db: Session, topics, num_courses=10):
    print("Generating courses...")
    courses = []
    for _ in range(num_courses):
        course = Course(
            name=fake.sentence(nb_words=3),
            topic_id=random.choice(topics).id,
            description=fake.paragraph()
        )
        db.add(course)
        courses.append(course)
    db.commit()
    return courses


# ✅ **Generate Fake Posts**
def create_fake_posts(db: Session, users, courses, num_posts=20):
    print("Generating posts...")
    posts = []
    for _ in range(num_posts):
        post = Post(
            id=str(uuid.uuid4()),
            course_id=random.choice(courses).id,
            author_id=random.choice(users).id,
            title=fake.sentence(),
            preview_md=fake.sentence(),
            content_md=fake.text(),
            created_at=datetime.utcnow()
        )
        db.add(post)
        posts.append(post)
    db.commit()
    return posts


# ✅ **Generate Fake Comments (Avoiding Duplicates)**
def create_fake_comments(db: Session, users, posts, num_comments=50):
    print("Generating comments...")
    existing_pairs = set()
    comments = []

    for _ in range(num_comments):
        user = random.choice(users)
        post = random.choice(posts)

        if (user.id, post.id) in existing_pairs:
            continue  # Avoid duplicate comments for the same user-post pair

        existing_pairs.add((user.id, post.id))

        comment = PostComment(
            user_id=user.id,
            post_id=post.id,
            content=fake.sentence(),
            created_at=datetime.utcnow()
        )
        db.add(comment)
        comments.append(comment)
    
    db.commit()
    return comments


# ✅ **Generate Fake Post Likes (Avoiding Duplicates)**
def create_fake_likes(db: Session, users, posts, num_likes=50):
    print("Generating likes...")
    existing_pairs = set()
    likes = []

    for _ in range(num_likes):
        user = random.choice(users)
        post = random.choice(posts)

        if (user.id, post.id) in existing_pairs:
            continue  # Avoid duplicate likes for the same user-post pair

        existing_pairs.add((user.id, post.id))

        like = PostLike(
            user_id=user.id,
            post_id=post.id
        )
        db.add(like)
        likes.append(like)
    
    db.commit()
    return likes


# ✅ **Generate Fake Favorite Courses (Avoiding Duplicates)**
def create_fake_favorites(db: Session, users, courses, num_favorites=20):
    print("Generating favorite courses...")
    existing_pairs = set()
    favorites = []

    for _ in range(num_favorites):
        user = random.choice(users)
        course = random.choice(courses)

        if (user.id, course.id) in existing_pairs:
            continue  # Avoid duplicate favorites

        existing_pairs.add((user.id, course.id))

        favorite = FavoriteCourse(
            user_id=user.id,
            course_id=course.id
        )
        db.add(favorite)
        favorites.append(favorite)
    
    db.commit()
    return favorites


# ✅ **Main Function to Generate Data**
def generate_fake_data():
    db = SessionLocal()

    # ✅ Delete existing data before inserting new fake data
    delete_all_data(db)

    users = create_fake_users(db, num_users=20)
    topics = create_fake_topics(db, num_topics=5)
    courses = create_fake_courses(db, topics, num_courses=10)
    posts = create_fake_posts(db, users, courses, num_posts=30)
    create_fake_comments(db, users, posts, num_comments=50)
    create_fake_likes(db, users, posts, num_likes=50)
    create_fake_favorites(db, users, courses, num_favorites=30)

    print("✅ Fake data generated successfully!")


# Run the script
if __name__ == "__main__":
    generate_fake_data()
