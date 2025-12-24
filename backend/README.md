# Document Summarizer - Backend

This is the FastAPI-based backend for the SummarAI project.

## Features
- **User Authentication**: Simple JWT-based login and registration.
- **File Handling**: Processes PDFs, Word docs, and text files.
- **AI Integration**: Connects to Hugging Face Transformers for summarization.
- **Data Storage**: Uses SQLite to keep track of users, documents, and summaries.

## Backend Tech
- **FastAPI**: Main web framework.
- **SQLite**: Local database.
- **SQLAlchemy**: Database ORM.
- **Pydantic**: Data validation.
- **PyTorch/Transformers**: ML inference.

## Setup
1. Create a `.env` file based on your local settings (Secret keys, etc.).
2. Install requirements: `pip install -r requirements.txt`.
3. Run with uvicorn: `uvicorn app.main:app --reload`.

## API Routes
- `/auth`: Register and Login.
- `/documents`: Upload and manage your files.
- `/summaries`: Generate and view AI summaries.

Check out the interactive docs at `http://localhost:8000/docs` once the server is running.
