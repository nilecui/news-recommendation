# News Recommendation System - AI Assistant Guide

## Project Overview

An intelligent news recommendation system with personalized content delivery. The system uses a microservices architecture with FastAPI backend, React frontend, and integrated data processing pipelines.

**Repository**: https://github.com/nilecui/news-recommendation
**Current Version**: V1.0 (MVP + Core Features Implemented)
**Last Updated**: 2025-11-14

---

## 🎯 Quick Reference for AI Assistants

### Project Status: What's Implemented

✅ **Backend (FastAPI)**
- User authentication with JWT (access + refresh tokens)
- News models with categories, tags, and metadata
- Multi-strategy recommendation engine (content-based, collaborative filtering, hot/fresh)
- Behavior tracking API (impression, click, read, like, bookmark, share)
- User profile and preference management
- RESTful API with comprehensive endpoints
- PostgreSQL + Redis + Elasticsearch integration configured
- Structured logging and error handling

✅ **Frontend (React + Vite)**
- Authentication pages (login/register)
- Home page with infinite scroll news feed
- News detail pages with interactions
- User profile and settings
- Reading history and collections
- Category browsing and search
- Modern UI with Ant Design
- Behavior tracking hooks (useTracker, useVisibilityTracker)
- Token management with auto-refresh

✅ **Infrastructure**
- Docker Compose setup for all services
- Database migrations with Alembic
- Development and production Dockerfiles
- Start/stop scripts for development

⚠️ **Partially Implemented / Planned**
- Celery task queue (configured but tasks not implemented)
- News crawlers (SerpAPI integration mentioned in git logs but files missing)
- Elasticsearch full-text search (configured but not utilized)
- MinIO image storage (in requirements but not implemented)
- LightGBM ranking model (basic scoring implemented, ML model planned)
- Sentence-Transformers embeddings (planned, not active)

---

## 📁 Actual Project Structure

```
news-recommendation/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── api.py              # Main API router
│   │   │       └── endpoints/
│   │   │           ├── auth.py         # Authentication endpoints
│   │   │           ├── users.py        # User management
│   │   │           ├── news.py         # News CRUD and interactions
│   │   │           ├── recommendations.py  # Recommendation engine
│   │   │           └── tracking.py     # Behavior tracking
│   │   ├── config/
│   │   │   ├── settings.py            # App configuration
│   │   │   └── database.py            # Database setup
│   │   ├── models/
│   │   │   ├── user.py                # User model
│   │   │   ├── profile.py             # UserProfile model
│   │   │   ├── news.py                # News + NewsCategory models
│   │   │   └── behavior.py            # UserBehavior model
│   │   ├── schemas/
│   │   │   ├── auth.py                # Auth Pydantic schemas
│   │   │   ├── user.py                # User schemas
│   │   │   ├── news.py                # News schemas
│   │   │   ├── recommendation.py      # Recommendation schemas
│   │   │   └── tracking.py            # Tracking schemas
│   │   ├── services/
│   │   │   ├── auth/
│   │   │   │   ├── auth_service.py    # JWT, password hashing
│   │   │   │   └── dependencies.py    # get_current_user
│   │   │   ├── user/
│   │   │   │   └── user_service.py    # User CRUD, history, collections
│   │   │   ├── news/
│   │   │   │   └── news_service.py    # News CRUD, like, collect, share
│   │   │   ├── recommendation/
│   │   │   │   └── recommendation_service.py  # Multi-strategy recall + ranking
│   │   │   └── tracking/
│   │   │       └── tracking_service.py  # Behavior tracking logic
│   │   └── main.py                    # FastAPI app entry point
│   ├── alembic/                       # Database migrations
│   ├── tests/                         # Pytest test suite
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Production Docker image
│   └── init_database.py              # Database initialization script
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/               # Shared components
│   │   │   │   ├── ProtectedRoute.tsx
│   │   │   │   ├── InfiniteScrollWrapper.tsx
│   │   │   │   └── LoadingScreen.tsx
│   │   │   ├── layout/
│   │   │   │   ├── MainLayout.tsx    # Main app layout with sidebar
│   │   │   │   └── AuthLayout.tsx    # Auth pages layout
│   │   │   └── news/
│   │   │       └── NewsCard.tsx      # News card component
│   │   ├── pages/
│   │   │   ├── auth/                 # Login, Register
│   │   │   ├── home/                 # HomePage with recommendations
│   │   │   ├── news/                 # NewsDetailPage, CategoryPage, SearchPage
│   │   │   └── profile/              # ProfilePage
│   │   ├── services/
│   │   │   ├── apiClient.ts          # Axios instance with interceptors
│   │   │   ├── authService.ts        # Auth API calls
│   │   │   ├── userService.ts        # User API calls
│   │   │   ├── newsService.ts        # News API calls
│   │   │   ├── recommendationService.ts
│   │   │   └── trackingService.ts    # Behavior tracking API
│   │   ├── hooks/
│   │   │   ├── useTracker.ts         # Behavior tracking hook
│   │   │   ├── useVisibilityTracker.ts  # Intersection Observer
│   │   │   └── useInfiniteNews.ts    # Infinite scroll
│   │   ├── store/
│   │   │   └── authStore.ts          # Zustand auth state
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript interfaces
│   │   ├── utils/
│   │   │   ├── tokenStorage.ts       # Local storage for tokens
│   │   │   └── errorHandling.ts      # Error utilities
│   │   ├── App.tsx                   # Main app component
│   │   └── main.tsx                  # React entry point
│   ├── package.json                  # Node dependencies
│   ├── vite.config.ts                # Vite configuration
│   ├── Dockerfile                    # Production Docker image
│   └── Dockerfile.dev                # Development Docker image
│
├── scripts/
│   └── init.sql                      # Database initialization SQL
│
├── docker-compose.yml                # Full stack orchestration
├── docker-compose-simple.yml         # Simplified setup
├── start-dev.sh                      # Development startup script
├── stop-dev.sh                       # Stop development services
├── .env.example                      # Environment variables template
├── README.md                         # User-facing documentation
└── CLAUDE.md                         # This file

```

---

## 🗄️ Database Schema (Actual Implementation)

### Users
```sql
Table: users
- id (PK, Integer)
- email (String, unique, indexed)
- username (String, unique, nullable)
- full_name (String, nullable)
- password_hash (String)
- is_active (Boolean, default=True)
- is_superuser (Boolean, default=False)
- email_verified (Boolean, default=False)
- phone_number (String, nullable)
- avatar_url (String, nullable)
- created_at (DateTime with TZ)
- updated_at (DateTime with TZ)
- last_login (DateTime with TZ, nullable)
```

### User Profiles
```sql
Table: user_profiles
- id (PK, Integer)
- user_id (FK -> users.id, unique)
- bio (Text)
- interests (ARRAY[String])
- location (String)
- preferred_language (String, default='zh')
- timezone (String, default='Asia/Shanghai')
- preferred_categories (JSON)  # {category_id: weight}
- preferred_tags (JSON)  # {tag: weight}
- reading_history_count (Integer, default=0)
- total_reading_time (Integer, default=0)  # seconds
- average_session_duration (Integer, default=0)  # seconds
- favorite_sources (ARRAY[String])
- quality_threshold (Float, default=0.5)
- diversity_preference (Float, default=0.5)
- freshness_preference (Float, default=0.5)
- is_cold_start_user (Boolean, default=True)
- onboarding_completed (Boolean, default=False)
- created_at, updated_at (DateTime with TZ)
```

### News Categories
```sql
Table: news_categories
- id (PK, Integer)
- name (String, unique, indexed)
- name_zh (String, nullable)
- description (Text)
- parent_id (FK -> news_categories.id, nullable)
- icon (String, nullable)
- color (String, nullable)  # Hex color
- sort_order (Integer, default=0)
- is_active (Boolean, default=True)
- created_at, updated_at (DateTime with TZ)
```

### News
```sql
Table: news
- id (PK, Integer)
- title (String, indexed)
- title_zh (String, nullable)
- content (Text)
- summary (Text)
- summary_zh (Text, nullable)
- source (String, indexed)
- source_url (String, unique)
- author (String, nullable)
- image_url (String, nullable)
- video_url (String, nullable)
- category_id (FK -> news_categories.id, indexed)
- tags (ARRAY[String])
- language (String, default='zh')
- word_count (Integer, default=0)
- reading_time (Integer, default=0)  # minutes
- quality_score (Float, default=0.0)  # 0-1
- sentiment_score (Float, default=0.0)  # -1 to 1
- view_count (Integer, default=0)
- like_count (Integer, default=0)
- share_count (Integer, default=0)
- comment_count (Integer, default=0)
- click_through_rate (Float, default=0.0)
- popularity_score (Float, default=0.0)
- trending_score (Float, default=0.0)
- embedding_vector (JSON, nullable)
- is_published (Boolean, default=True)
- is_featured (Boolean, default=False)
- is_breaking (Boolean, default=False)
- published_at (DateTime with TZ, indexed)
- created_at (DateTime with TZ, indexed)
- updated_at (DateTime with TZ)
- slug (String, unique, nullable)  # URL-friendly identifier
```

### User Behaviors
```sql
Table: user_behaviors
- id (PK, Integer)
- user_id (FK -> users.id, indexed)
- news_id (FK -> news.id, indexed)
- behavior_type (String, indexed)  # 'impression', 'click', 'read', 'like', 'bookmark', 'share'
- timestamp (DateTime with TZ, indexed)
- session_id (String, nullable)
- context (JSON, nullable)  # Device, position, etc.
- duration (Integer, default=0)  # seconds, for 'read' behavior
- read_percentage (Float, default=0.0)  # 0-1
- scroll_depth (Float, default=0.0)  # 0-1
- device_type (String, nullable)
- referrer (String, nullable)
```

**Key Relationships:**
- User 1:1 UserProfile
- User 1:N UserBehavior
- News N:1 NewsCategory
- News 1:N UserBehavior
- NewsCategory (self-referential for parent/children)

---

## 🚀 Development Workflows

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/nilecui/news-recommendation.git
cd news-recommendation

# 2. Start infrastructure services
docker-compose up -d postgres redis elasticsearch

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 4. Initialize database
cd backend
python init_database.py

# 5. Start development servers
# Option A: Use scripts (recommended)
cd ..
chmod +x start-dev.sh
./start-dev.sh

# Option B: Manual start
# Terminal 1 - Backend
cd backend
source ../venv/bin/activate  # or create: python -m venv ../venv
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### Access Points
- **Frontend**: http://localhost:5173 (or 3000 in Docker)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

### Running Tests

```bash
# Backend tests
cd backend
pytest                          # Run all tests
pytest tests/test_auth.py      # Specific test file
pytest -v                      # Verbose output
pytest --cov=app              # Coverage report

# Frontend tests (if configured)
cd frontend
npm test
npm run test:coverage
```

### Database Operations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Reinitialize database (WARNING: destroys data)
python init_database.py
```

### Docker Operations

```bash
# Full stack
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose logs -f backend  # Follow backend logs
docker-compose restart backend  # Restart specific service

# Rebuild after code changes
docker-compose build backend
docker-compose up -d backend

# Database only
docker-compose up -d postgres redis elasticsearch

# Check service status
docker-compose ps
```

---

## 🔑 API Endpoints Reference

### Authentication (`/api/v1/auth`)
- `POST /register` - Register new user
- `POST /login` - Login (returns access + refresh tokens)
- `POST /logout` - Logout (invalidate tokens)
- `POST /refresh` - Refresh access token

### Users (`/api/v1/users`)
- `GET /me` - Get current user info
- `PUT /me` - Update user info
- `DELETE /me` - Delete account
- `GET /me/profile` - Get user profile
- `PUT /me/profile` - Update user profile
- `GET /me/history` - Get reading history (paginated)
- `GET /me/collections` - Get bookmarked news (paginated)

### News (`/api/v1/news`)
- `GET /latest` - Get latest news (paginated)
- `GET /trending` - Get trending news (paginated)
- `GET /category/{category_id}` - Get news by category (paginated)
- `GET /{news_id}` - Get news details
- `POST /search` - Search news (body: query, filters)
- `POST /{news_id}/like` - Toggle like
- `POST /{news_id}/collect` - Toggle bookmark
- `POST /{news_id}/share` - Record share event

### Recommendations (`/api/v1/recommendations`)
- `GET /` - Get personalized recommendations (uses multi-strategy)
- `GET /cold-start` - Get cold start recommendations
- `GET /discovery` - Get discovery recommendations
- `GET /popular` - Get popular news
- `GET /similar/{news_id}` - Get similar news
- `POST /feedback` - Submit recommendation feedback

### Tracking (`/api/v1/tracking`)
- `GET /stats` - Get tracking statistics
- `POST /impression` - Record impression
- `POST /click` - Record click
- `POST /read` - Record read (with duration)
- `POST /behaviors` - Batch record behaviors

**Standard Response Format:**
```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": 1234567890
}
```

**Pagination:**
- Query params: `page` (default: 1), `page_size` (default: 20)
- Response includes: `items`, `total`, `page`, `page_size`, `total_pages`

**Authentication:**
- Header: `Authorization: Bearer <access_token>`
- Access token expires in 15 minutes
- Refresh token expires in 7 days

---

## 🎨 Frontend Architecture

### State Management
- **Zustand** for global state (auth)
- **React Query** for server state (not yet implemented, uses native fetch)
- **Local state** with useState for component-specific state

### Routing
```typescript
// App.tsx routes
/login         -> LoginPage (public)
/register      -> RegisterPage (public)
/              -> HomePage (protected)
/news/:id      -> NewsDetailPage (protected)
/category/:id  -> CategoryPage (protected)
/search        -> SearchPage (protected)
/profile       -> ProfilePage (protected)
/history       -> HistoryPage (protected, via ProfilePage)
/favorites     -> FavoritesPage (protected, via ProfilePage)
```

### Custom Hooks
- `useTracker(behaviorType, newsId)` - Track user behaviors
- `useVisibilityTracker(newsId)` - Track impressions with Intersection Observer
- `useInfiniteNews(endpoint, params)` - Infinite scroll for news lists
- `useAuth()` - Access auth state and methods

### API Client Pattern
```typescript
// All API calls go through apiClient.ts
import apiClient from '@/services/apiClient';

const response = await apiClient.get('/news/latest', { params: { page: 1 } });

// apiClient automatically:
// - Adds Authorization header
// - Refreshes token if expired
// - Handles errors consistently
// - Redirects to login on 401
```

### Behavior Tracking Pattern
```typescript
// In any component
import { useTracker } from '@/hooks/useTracker';
import { useVisibilityTracker } from '@/hooks/useVisibilityTracker';

function NewsCard({ news }) {
  const { trackBehavior } = useTracker();
  const cardRef = useVisibilityTracker(news.id);  // Auto-tracks impressions

  const handleClick = () => {
    trackBehavior('click', news.id);
    navigate(`/news/${news.id}`);
  };

  return <div ref={cardRef} onClick={handleClick}>...</div>;
}
```

---

## 🧩 Backend Architecture

### Service Layer Pattern
Controllers (endpoints) → Services → Models (ORM)

**Example Flow:**
```
GET /api/v1/recommendations/
  → endpoints/recommendations.py::get_recommendations()
    → services/recommendation/recommendation_service.py::get_recommendations()
      → Multi-strategy recall (hot, content, collaborative, fresh)
      → Ranking algorithm
      → Redis caching
      → Return formatted results
```

### Recommendation Engine Strategy

**For Cold Start Users:**
- 60% Hot news (trending in last 24h)
- 20% Featured news
- 20% Fresh news (latest)

**For Warm Users:**
- 40% Content-based (user preferences match)
- 30% Collaborative filtering (similar users)
- 20% Hot news
- 10% Fresh news (exploration)

**Ranking Algorithm:**
```python
score = strategy_weight
      + popularity_score * 0.3
      + trending_score * 0.3
      + quality_score * 0.2
      + freshness_score * 0.2
      + (1.5x if breaking)
      + (1.2x if featured)

# With diversity re-ranking using MMR algorithm
```

### Dependency Injection
```python
from app.services.auth.dependencies import get_current_user

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user is automatically validated from JWT
    # db is a database session
```

### Error Handling
- Custom exceptions in each service
- Global exception handler in main.py
- Validation errors return 422 with details
- Auth errors return 401
- Resource not found returns 404
- Server errors return 500 (details hidden in production)

---

## 🛠️ Common Development Tasks

### Adding a New API Endpoint

1. **Define Schema** (`app/schemas/`)
```python
# app/schemas/new_feature.py
from pydantic import BaseModel

class FeatureRequest(BaseModel):
    param: str

class FeatureResponse(BaseModel):
    result: str
```

2. **Implement Service** (`app/services/new_feature/`)
```python
# app/services/new_feature/feature_service.py
class FeatureService:
    def __init__(self, db: Session):
        self.db = db

    def do_something(self, param: str) -> str:
        # Business logic here
        return "result"
```

3. **Create Endpoint** (`app/api/v1/endpoints/`)
```python
# app/api/v1/endpoints/new_feature.py
from fastapi import APIRouter, Depends
from app.services.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/action")
async def action(
    request: FeatureRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = FeatureService(db)
    result = service.do_something(request.param)
    return {"result": result}
```

4. **Register Router** (`app/api/v1/api.py`)
```python
from app.api.v1.endpoints import new_feature

api_router.include_router(
    new_feature.router,
    prefix="/new-feature",
    tags=["new-feature"]
)
```

### Adding a New Database Model

1. **Define Model** (`app/models/`)
```python
# app/models/new_model.py
from sqlalchemy import Column, Integer, String
from app.config.database import Base

class NewModel(Base):
    __tablename__ = "new_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
```

2. **Import in models/__init__.py**
```python
from .new_model import NewModel
```

3. **Create Migration**
```bash
cd backend
alembic revision --autogenerate -m "Add new_model table"
alembic upgrade head
```

### Adding a Frontend Page

1. **Create Page Component** (`src/pages/`)
```typescript
// src/pages/new-page/NewPage.tsx
import React from 'react';

export const NewPage: React.FC = () => {
  return <div>New Page Content</div>;
};
```

2. **Add Route** (`src/App.tsx`)
```typescript
import { NewPage } from '@/pages/new-page/NewPage';

// In Routes
<Route path="/new-page" element={
  <ProtectedRoute>
    <NewPage />
  </ProtectedRoute>
} />
```

3. **Add Navigation** (`src/components/layout/MainLayout.tsx`)
```typescript
// Add menu item
{
  key: '/new-page',
  icon: <IconComponent />,
  label: 'New Page'
}
```

---

## 🧪 Testing Guidelines

### Backend Testing

**Test Structure:**
```python
# tests/test_feature.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_feature_success():
    response = client.post(
        "/api/v1/feature/action",
        json={"param": "value"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["result"] == "expected"

def test_feature_validation_error():
    response = client.post("/api/v1/feature/action", json={})
    assert response.status_code == 422
```

**Fixtures** (`tests/conftest.py`):
- `db_session` - Test database session
- `test_user` - Create test user
- `auth_token` - Get auth token for test user

**Run Specific Tests:**
```bash
pytest tests/test_auth.py::test_login_success
pytest -k "test_recommendation"
pytest -m "slow"  # If using markers
```

### Frontend Testing (To Implement)

**Recommended Tools:**
- Vitest for unit tests
- React Testing Library for component tests
- Playwright for E2E tests

---

## 🚢 Deployment

### Environment Variables

**Backend (.env):**
```bash
DEBUG=False
SECRET_KEY=<generate-secure-key>
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
ELASTICSEARCH_URL=http://host:9200
CELERY_BROKER_URL=redis://host:6379/1
CELERY_RESULT_BACKEND=redis://host:6379/2
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_HOSTS=https://yourdomain.com,http://localhost:3000
```

**Frontend (.env.production):**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
NODE_ENV=production
```

### Docker Production Build

```bash
# Build images
docker-compose -f docker-compose.yml build

# Start production stack
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale celery_worker=4
```

### Manual Deployment

**Backend:**
```bash
cd backend
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

**Frontend:**
```bash
cd frontend
npm run build
# Serve dist/ folder with nginx or similar
```

---

## 🎯 Code Conventions & Best Practices

### Python (Backend)

1. **Type Hints**: Always use type hints
```python
def get_user(user_id: int) -> User:
    ...
```

2. **Pydantic Schemas**: Use for request/response validation
```python
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
```

3. **Error Handling**: Use HTTPException
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)
```

4. **Async/Await**: Use for I/O operations
```python
async def get_recommendations(user_id: int):
    redis = await self.get_redis()
    cached = await redis.get(f"rec:{user_id}")
```

5. **Docstrings**: Use for complex functions
```python
def calculate_score(news: News, strategy: str) -> float:
    """
    Calculate recommendation score for a news item.

    Args:
        news: News object to score
        strategy: Recall strategy used ('hot', 'content', etc.)

    Returns:
        Float score between 0 and infinity
    """
```

### TypeScript (Frontend)

1. **Interface Definitions**: Define in `types/index.ts`
```typescript
export interface News {
  id: number;
  title: string;
  summary: string;
  // ...
}
```

2. **Component Props**: Always type
```typescript
interface NewsCardProps {
  news: News;
  onLike?: (newsId: number) => void;
}

export const NewsCard: React.FC<NewsCardProps> = ({ news, onLike }) => {
  ...
};
```

3. **API Calls**: Use service layer
```typescript
// Don't call axios directly in components
// Do this:
import { getLatestNews } from '@/services/newsService';

const news = await getLatestNews(page);
```

4. **Error Handling**: Use try-catch with user feedback
```typescript
try {
  await someAction();
  message.success('Success!');
} catch (error) {
  message.error(error.message || 'Something went wrong');
}
```

### Git Commit Messages

Follow conventional commits:
```
feat: Add user notification system
fix: Resolve login token refresh issue
docs: Update API documentation
style: Format code with prettier
refactor: Simplify recommendation algorithm
test: Add tests for auth endpoints
chore: Update dependencies
```

---

## 📚 Key Files for AI Assistants

When making changes, always reference these files:

**Backend:**
- `app/main.py` - Application entry, middleware, CORS
- `app/api/v1/api.py` - API router registration
- `app/config/settings.py` - Configuration (read-only, use .env)
- `app/models/*.py` - Database schema (generate migrations after changes)
- `app/services/*/` - Business logic (main implementation area)

**Frontend:**
- `src/App.tsx` - Routing configuration
- `src/services/apiClient.ts` - HTTP client setup
- `src/store/authStore.ts` - Auth state management
- `src/components/layout/MainLayout.tsx` - App layout and navigation

**Infrastructure:**
- `docker-compose.yml` - Service orchestration
- `.env.example` - Environment variables template
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies

---

## 🐛 Troubleshooting Common Issues

### Backend Issues

**Import Error: No module named 'app'**
```bash
# Make sure you're in backend/ directory
cd backend
# Make sure venv is activated
source ../venv/bin/activate
```

**Database Connection Error**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres
# Check DATABASE_URL in .env
# Try: psql postgresql://user:pass@localhost:5432/dbname
```

**Alembic Migration Conflicts**
```bash
# View migration heads
alembic heads
# Stamp to specific revision
alembic stamp <revision>
# Or drop and recreate
python init_database.py
```

### Frontend Issues

**CORS Error**
- Check `ALLOWED_HOSTS` in backend `.env`
- Should include `http://localhost:5173` (or your frontend port)

**401 Unauthorized on Protected Routes**
- Check if token is stored: `localStorage.getItem('access_token')`
- Check token expiration
- Try logging out and back in

**Build Errors**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### Docker Issues

**Port Already in Use**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Container Won't Start**
```bash
# View logs
docker-compose logs backend
# Rebuild container
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

## 📊 Monitoring & Observability

**Structured Logging:**
- Backend uses `structlog` for JSON logging
- Logs include: method, url, status_code, process_time
- View logs: `docker-compose logs -f backend`

**Health Checks:**
- `GET /health` - Basic health check
- Returns: `{"status": "healthy", "timestamp": ...}`

**Metrics (Planned):**
- Prometheus endpoint: `/metrics` (not yet implemented)
- Key metrics: request_duration, request_count, db_query_time

**Celery Monitoring (When Implemented):**
- Flower: http://localhost:5555
- View tasks, workers, queues

---

## 🔮 Roadmap & Next Steps

### High Priority (Blocking Features)

1. **Implement Celery Tasks**
   - Create `app/celery_app.py`
   - Implement news crawling tasks
   - Add periodic tasks (trending calculation, cache warming)
   - File: Referenced in `docker-compose.yml` but missing

2. **Fix Missing Crawler Endpoint**
   - Create `app/api/v1/endpoints/crawler.py`
   - Currently imported in `api.py` but file doesn't exist
   - Implement SerpAPI news crawling
   - Trigger manual and scheduled crawls

3. **Implement Elasticsearch Integration**
   - Connect to configured ES instance
   - Index news on creation
   - Implement full-text search in `news_service.py`
   - Add vector search for embeddings

### Medium Priority (Enhancements)

1. **ML Model Integration**
   - Train LightGBM ranking model
   - Replace rule-based scoring with ML predictions
   - Implement model versioning and A/B testing

2. **Content Embeddings**
   - Generate embeddings with Sentence-Transformers
   - Store in `embedding_vector` column
   - Implement vector similarity search

3. **MinIO Integration**
   - Set up MinIO for image storage
   - Implement image upload API
   - CDN integration

4. **Frontend Improvements**
   - Implement React Query for data fetching
   - Add optimistic updates
   - Improve error boundaries
   - Add loading skeletons

### Low Priority (Nice-to-Have)

1. **Advanced Features**
   - Real-time notifications (WebSocket)
   - Social features (follow users, comments)
   - Personalized newsletters
   - Mobile app (React Native)

2. **Operational**
   - Kubernetes deployment configs
   - CI/CD pipeline (GitHub Actions)
   - Automated testing in CI
   - Performance monitoring (APM)

---

## 🤝 Contributing Guidelines

When working on this codebase:

1. **Always read existing code** before adding new features
2. **Follow established patterns** (service layer, schemas, etc.)
3. **Write tests** for new functionality
4. **Update this file** if you add new patterns or conventions
5. **Use descriptive commit messages** (conventional commits)
6. **Keep dependencies updated** but test thoroughly
7. **Document breaking changes** in commit messages and PR descriptions

---

## 📞 Getting Help

**Documentation:**
- API Docs: http://localhost:8000/api/v1/docs
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- Ant Design: https://ant.design
- SQLAlchemy: https://docs.sqlalchemy.org

**Project Docs:**
- `README.md` - User-facing setup guide
- `QUICK_START.md` - Quick start instructions (Chinese)
- `backend/COMPLETE_API_TEST_REPORT.md` - API test results
- `DASHBOARD_OPTIMIZATION_REPORT.md` - UI optimization notes

**Issues:**
- GitHub Issues: Report bugs and request features
- Check existing issues before creating new ones

---

**Last Updated**: 2025-11-14
**Maintained By**: AI Assistant with periodic human review
**License**: MIT
