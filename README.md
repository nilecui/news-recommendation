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

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Database Setup**:
   ```bash
   docker-compose up -d postgres redis elasticsearch
   alembic upgrade head
   ```

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License