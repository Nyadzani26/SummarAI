# SummarAI - AI-Powered Document Summarizer

This is a personal learning project I built as an ICT student at Sol Plaatje University. I wanted to see if I could build a full-stack web app that uses a Machine Learning model to summarize different types of documents.

## What it does
- **Upload Documents**: Supports PDF, DOCX, and TXT files.
- **AI Summaries**: Uses the `bart-large-cnn` model to generate summaries.
- **User Accounts**: Basic login and registration so you can see your own history.
- **Dashboard**: A simple UI to manage your files and view generated summaries.

## The Tech Stack
- **Backend**: Python with **FastAPI**
- **Database**: **SQLite** (SQLAlchemy ORM)
- **ML Model**: **Hugging Face Transformers** (BART)
- **Frontend**: **Alpine.js** & **TailwindCSS**

## Why I Built This
Building this project helped me learn how to:
1. Integrate an ML model into a Python API.
2. Work with asynchronous tasks in FastAPI.
3. Manage a frontend without using heavy frameworks like React.

**Interesting Lesson:** While testing, I found that the model often refers to the author as "she" even when it's me. This gave me a real-world look at how data bias in ML models works.

---

## How to Run Locally

### 1. Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
The API runs at `http://localhost:8000`

### 2. Frontend
```bash
cd frontend
python -m http.server 3000
```
Open your browser to `http://localhost:3000`

---

## Project Structure
- `backend/`: FastAPI source code and local file uploads.
- `frontend/`: HTML and Alpine.js dashboard files.
- `models/`: Where the pre-trained BART model is stored locally.

---

**Built by Gift Nemakonde**
GitHub: [Nyadzani26](https://github.com/Nyadzani26)
