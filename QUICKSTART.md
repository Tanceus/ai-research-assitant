# Quick Start Guide

## Option 1: Docker (Easiest - Recommended)

1. **Start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Wait for services to start** (this may take a few minutes the first time as it downloads images and installs dependencies)

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Upload a PDF** and start querying!

---

## Option 2: Local Development

### Step 1: Start PostgreSQL Database
```bash
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=research_assistant -p 5432:5432 postgres:15-alpine
```

### Step 2: Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Frontend Setup (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```

---

## First Steps After Starting

1. Open http://localhost:3000 in your browser
2. Upload a PDF research paper (click "Choose PDF File")
3. Wait for processing to complete
4. Enter a query like "What is the main contribution of this paper?"
5. Click "Search" to see relevant results

## Troubleshooting

- **Port conflicts**: Make sure ports 3000, 8000, and 5432 are not in use
- **Docker issues**: Make sure Docker Desktop is running
- **Database connection**: Wait for PostgreSQL to fully start before starting backend

