# 🚀 Quick Start - Fix Connection Issues

## The Problem
You're seeing "connection failed" because the **backend server is not running**.

## ✅ Solution: Start the Backend

### Option A: Quick Start (Recommended - Use Docker for Database)

**1. Start PostgreSQL Database:**
```powershell
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=research_assistant -p 5432:5432 postgres:15-alpine
```

**2. Start Backend Server:**
Open a new terminal/command prompt and run:
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait until you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**3. Start Frontend (in another terminal):**
```powershell
cd frontend
npm install
npm run dev
```

**4. Open your browser:**
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

---

### Option B: Use Docker Compose (All-in-One)

If you have Docker Desktop running:

```powershell
docker-compose up --build
```

This starts everything automatically. Then open http://localhost:3000

---

## ✅ Verify Backend is Running

1. Open http://localhost:8000/docs - You should see API documentation
2. Or test with: `curl http://localhost:8000/api/health`

If you see errors, check the terminal where the backend is running for error messages.

---

## 📝 Important Notes

- **Keep the backend terminal open** - Don't close it while using the app
- The backend needs to be running before the frontend can connect
- First time setup may take a few minutes (downloading dependencies)

## 🐛 Still Having Issues?

See `TROUBLESHOOTING.md` for detailed help.

