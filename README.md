# The Knowledge Vault 🎓

An AI-enhanced collaborative learning platform that enables students to create, share, and interact with structured course notes while leveraging a context-aware AI chatbot as a personal teaching assistant.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange)

## 📋 Overview

**The Knowledge Vault** is a mini Moodle-like platform developed during a 48-hour hackathon that revolutionizes student learning through community-based knowledge sharing and AI-powered assistance. The platform combines traditional note-sharing functionality with cutting-edge AI technology to create an interactive, personalized learning experience.

### 🏆 Recognition
- Presented at the **2025 Scientific Student Conference**
- Nominated for the **2027 National Scientific Student Conference**
- Evaluated using the **Technology Acceptance Model (TAM)** with promising results

## ✨ Key Features

### 📝 Collaborative Learning
- **Course Notes Management**: Create, view, and share detailed course notes in Markdown format
- **Topic Organization**: Hierarchical structure with Topics → Courses → Posts
- **Rich Content Support**: Full Markdown support for formatting notes with code blocks, images, and mathematical equations
- **Social Engagement**: Like and comment on posts to foster community discussion
- **Personalized Dashboard**: Favorite courses for quick access to frequently studied materials

### 🤖 AI-Powered Study Assistant
- **Context-Aware Chatbot**: Integrated Google Gemini AI that answers questions based on the currently opened note
- **Real-Time WebSocket Communication**: Instant AI responses without page refreshes
- **Conversation History**: Maintains context across multiple questions for natural dialogue
- **Content-Focused Assistance**: AI tutor stays focused on the study material, providing elaborations, clarifications, and relevant examples

### 👥 Community Features
- **User Profiles**: Authentication system with customizable profiles
- **Content Authorship**: Track who created each note with author attribution
- **Engagement Metrics**: View like counts and engagement levels on posts
- **Comment Threads**: Discuss concepts and ask questions on specific posts

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **FastAPI**: High-performance Python web framework for RESTful API
- **SQLAlchemy**: ORM for database operations with Alembic migrations
- **PostgreSQL**: Robust relational database for data persistence
- **Google Gemini 2.0 Flash**: Advanced AI model for natural language understanding
- **WebSocket**: Real-time bidirectional communication for AI chat

**Frontend:** React (separate repository)

### Database Schema

```
Users ──┬── Posts (author_id)
        ├── PostComments
        ├── PostLikes
        └── FavoriteCourses

Topics ─── Courses ─── Posts ──┬── PostComments
                                └── PostLikes
```

**Core Models:**
- **User**: Authentication, profile, and admin status
- **Topic**: High-level subject categories (e.g., "Computer Science", "Mathematics")
- **Course**: Specific courses within topics (e.g., "Machine Learning", "Linear Algebra")
- **Post**: Individual notes/study materials with Markdown content
- **PostComment**: Discussion threads on posts
- **PostLike**: Engagement tracking
- **FavoriteCourse**: User's bookmarked courses

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Google Gemini API key
- UV package manager (recommended) or pip

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Whitespace2025-backend
```

2. **Set up environment variables**

Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://myuser:mypassword@localhost:6666/mydatabase
GEMINI_API_KEY=your_gemini_api_key_here
```

3. **Install dependencies**

Using UV (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

4. **Set up the database**

Start PostgreSQL and run migrations:
```bash
alembic upgrade head
```

5. **Run the application**
```bash
uvicorn app.main:main --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Authentication
All endpoints require a CSRF token in the header:
```
CSRF-Token: <token>
```

### Core Endpoints

#### User Management
- `POST /create_user` - Register a new user
- Authentication via user ID in headers

#### Content Creation
- `POST /create_topic` - Create a new topic category
- `POST /create_course` - Create a course under a topic
- `POST /create_post` - Create a new study note/post

#### Content Retrieval
- `GET /topics_with_courses` - Get all topics with their courses (includes favorite status)
- `GET /posts?course_id={id}&sort_by_likes=true&limit=10` - Get posts with filtering
- `GET /get_post/{post_id}` - Get specific post details

#### Social Features
- `POST /like_post?post_id={id}` - Like a post
- `DELETE /remove_like?post_id={id}` - Remove like
- `POST /add_comment` - Add comment to post
- `DELETE /remove_comment?comment_id={id}` - Delete own comment
- `GET /get_comments?post_id={id}` - Get all comments on a post

#### Favorites
- `POST /add_favorite_course?course_id={id}` - Bookmark a course
- `DELETE /remove_favorite_course?course_id={id}` - Remove bookmark
- `GET /favorite_courses` - Get user's favorited courses

#### AI Chat
- `WebSocket /chat_ws` - Real-time AI tutor chat

### WebSocket Chat Format

**Connect to:** `ws://localhost:8000/chat_ws`

**Send message:**
```json
{
  "markdown": "# Machine Learning\n\nSupervised learning is...",
  "prompt": "What is the difference between supervised and unsupervised learning?"
}
```

**Receive:** Plain text AI response

## 🧪 Testing

The project includes comprehensive test coverage:

```bash
pytest tests/
```

Test suites include:
- API endpoint validation
- Database operations
- WebSocket communication
- Input validation

## 🔒 Security Features

- **CSRF Protection**: Token-based CSRF validation on all mutations
- **IP Blacklisting**: Configurable IP-based access control
- **CORS Configuration**: Controlled cross-origin resource sharing
- **Input Validation**: Pydantic schemas for request validation
- **User Authentication**: User ID header validation

## 📊 Research & Evaluation

The platform has been academically evaluated using the **Technology Acceptance Model (TAM)**, measuring:
- **Perceived Usefulness**: Student assessment of learning benefits
- **Perceived Ease of Use**: Platform usability metrics
- **User Acceptance**: Willingness to adopt and continue using

Results indicated **promising acceptance** with clear directions for future development identified through open-ended feedback.

## 🛣️ Roadmap

- [ ] Enhanced AI features (code execution, diagram generation)
- [ ] Mobile application
- [ ] Advanced search with AI-powered recommendations
- [ ] Real-time collaborative editing
- [ ] Integration with university LMS systems
- [ ] Spaced repetition flashcard system
- [ ] Peer review system for note quality

## 👥 Team

Developed by a team of three during a 48-hour hackathon (2025)

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)
- Database migrations with [Alembic](https://alembic.sqlalchemy.org/)

---

**Note:** This backend API is designed to work with the React frontend. Ensure both services are running for full functionality.
