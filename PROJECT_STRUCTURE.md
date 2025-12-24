# SummarAI Project Structure

## Directory Overview

```
document-summarizer/
├── backend/              # FastAPI backend application
│   ├── app/             # Main application code
│   │   ├── models/      # Database models (SQLAlchemy)
│   │   ├── schemas/     # Pydantic schemas for validation
│   │   ├── routers/     # API route handlers
│   │   ├── services/    # Business logic (auth, summarization)
│   │   ├── utils/       # Helper functions (security, document parsing)
│   │   ├── config.py    # Application configuration
│   │   ├── database.py  # Database connection setup
│   │   └── main.py      # FastAPI app entry point
│   ├── tests/           # Test scripts
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Environment variables template
│   └── README.md        # Backend documentation
│
├── frontend/            # Frontend application (to be developed)
├── DEPLOYMENT.md        # Deployment instructions
├── PROJECT_STRUCTURE.md # This file
└── README.md            # Main project documentation

## Key Files

### Backend Configuration
- **requirements.txt**: All Python dependencies with pinned versions
- **.env.example**: Template for environment variables
- **app/config.py**: Centralized configuration management

### Database
- **app/models/**: SQLAlchemy ORM models
  - user.py: User authentication model
  - document.py: Document storage model
  - summary.py: AI summary model

### API Routes
- **app/routers/auth.py**: Authentication endpoints
- **app/routers/documents.py**: Document management
- **app/routers/summaries.py**: AI summarization

### Services
- **app/services/auth_services.py**: User authentication logic
- **app/services/summarization_service.py**: AI model integration

## Technology Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Production database)
- JWT (Authentication)
- BART/DistilBART (AI summarization)
- PyTorch & Transformers (ML framework)

### Document Processing
- PyPDF2 (PDF extraction)
- python-docx (Word documents)

### Security
- Passlib & Bcrypt (Password hashing)
- python-jose (JWT tokens)

## Environment Setup

1. Create virtual environment
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Copy .env.example to .env
4. Configure environment variables
5. Run: `uvicorn app.main:app --reload`

## Testing

Run tests from backend/tests/:
- test_api.py: Full API test suite
- test_summary_only.py: Summary generation only

## Deployment Ready

- Database auto-initialization
- Environment-based configuration
- Cloud-optimized file paths
- Graceful AI model fallback
- CORS configured
- Production-ready error handling
