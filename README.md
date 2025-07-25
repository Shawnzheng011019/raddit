# Raddit - A Reddit-like Forum with Recommendation System

Raddit is a Reddit-like forum system with an integrated recommendation engine. It uses a Two-Tower model for candidate generation and a Wide & Deep model for ranking, with Milvus as the vector database for efficient similarity search.

## Project Structure

```
raddit/
├── frontend/           # React frontend
├── backend/            # FastAPI backend
├── wide-deep/          # Recommendation models (Wide & Deep + Two-Tower)
├── docker/             # Docker configuration
├── scripts/            # Utility scripts
└── data/               # Data storage
```

## Features

1. **Frontend (React)**
   - Home page with recommended posts
   - Post detail view
   - User interaction tracking (clicks, views, upvotes)

2. **Backend (FastAPI)**
   - RESTful API for recommendations
   - User and post management
   - User event tracking

3. **Recommendation System**
   - Two-Tower model for candidate generation (recall)
   - Wide & Deep model for ranking
   - Milvus vector database for efficient similarity search

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 16+

### Running with Docker (Recommended)

```bash
# Clone the repository
git clone wide-deep;
git clone &lt;repository-url&gt;
cd raddit

# Start all services
docker-compose up -d

# The frontend will be available at http://localhost:3000
# The backend API will be available at http://localhost:8000
```

### Running Locally

#### Backend

```bash
cd backend
pip install -r requirements.txt
python scripts/init_db.py
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `GET /api/recommend/home?user_id={id}` - Get home page recommendations
- `POST /api/user/event` - Record user event (click, view, upvote)
- `GET /api/post/{id}` - Get post details
- `POST /api/post/` - Create a new post

## Data Models

### Users
- id (int)
- username (string)
- email (string)
- created_at (datetime)

### Posts
- id (int)
- title (string)
- content (text)
- author_id (foreign key to users)
- created_at (datetime)

### User Events
- id (int)
- user_id (foreign key to users)
- post_id (foreign key to posts)
- event_type (string: click, view, upvote)
- timestamp (datetime)

## Recommendation Pipeline

1. **Recall Stage**: Two-Tower model generates candidate posts based on user embeddings
2. **Ranking Stage**: Wide & Deep model re-ranks candidates based on detailed features
3. **Storage**: Post embeddings are stored in Milvus for efficient similarity search

## Development

### Adding New Features

1. Backend API endpoints go in `backend/app/api/`
2. Database models go in `backend/app/models/`
3. Business logic goes in `backend/app/services/`
4. Frontend components go in `frontend/src/components/`
5. Frontend pages go in `frontend/src/pages/`

### Model Training

The recommendation models can be trained using the scripts in the `wide-deep` directory:

```bash
cd wide-deep
python train/train_two_tower.py
python train/train_wide_deep.py
```