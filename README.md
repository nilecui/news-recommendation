# News Recommendation System

A personalized news recommendation system built with FastAPI (backend) and React (frontend).

## Architecture

### Backend (FastAPI)
- **Language**: Python 3.9+
- **Framework**: FastAPI with SQLAlchemy
- **Database**: PostgreSQL + Redis + Elasticsearch
- **Task Queue**: Celery with Redis
- **Authentication**: JWT tokens

### Frontend (React)
- **Framework**: React 18 + Vite
- **State Management**: Zustand
- **UI Library**: Ant Design
- **HTTP Client**: Axios

## Project Structure

```
news-recommendation/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── api/           # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── crawlers/      # News scraping
│   │   ├── config/        # Configuration
│   │   └── utils/         # Utilities
│   ├── tests/             # Backend tests
│   ├── alembic/           # Database migrations
│   └── requirements.txt   # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── store/         # Zustand stores
│   │   ├── services/      # API client
│   │   ├── hooks/         # Custom hooks
│   │   └── utils/         # Utilities
│   ├── public/            # Static assets
│   └── package.json       # Node.js dependencies
├── scripts/               # Deployment and utility scripts
├── docs/                  # Documentation
└── docker-compose.yml     # Development environment
```

## Features

- **User Management**: Registration, login, profile management
- **News Crawling**: Multi-source news collection and processing
- **Recommendation Engine**: Multi-stage recommendation pipeline
- **Behavior Tracking**: User interaction analytics
- **Real-time Updates**: Cached recommendations with Redis
- **Search & Discovery**: Full-text search with Elasticsearch

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL, Redis, Elasticsearch

### Development Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/nilecui/news-recommendation.git
   cd news-recommendation
   ```

2. **Backend Setup**:
   ```bash
   cd backend

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Configure environment
   cp .env.example .env
   # Edit .env and set SECRET_KEY and DATABASE_URL

   # Initialize database
   alembic upgrade head

   # Start backend server
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend

   # Install dependencies
   npm install
   # or: pnpm install

   # Start development server
   npm run dev
   ```

4. **Database Services (Optional but Recommended)**:
   ```bash
   # Start PostgreSQL, Redis, and Elasticsearch
   docker-compose up -d postgres redis elasticsearch
   ```

   **Note**: The app can run with SQLite (default in .env) without Docker.

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License