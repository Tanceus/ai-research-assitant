# Troubleshooting Connection Issues

## Common Connection Problems

### 1. "Unable to connect to backend" Error

This error means the frontend cannot reach the backend API.

#### If using Docker:
1. Check if Docker Desktop is running
2. Verify all services are up:
   ```bash
   docker-compose ps
   ```
3. Check backend logs:
   ```bash
   docker-compose logs backend
   ```
4. Ensure backend is accessible at http://localhost:8000
5. Try restarting:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

#### If running locally:

**Step 1: Start PostgreSQL (if not using Docker)**
```bash
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=research_assistant -p 5432:5432 postgres:15-alpine
```

**Step 2: Start Backend**
Open a terminal and run:
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

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Step 3: Start Frontend (in a new terminal)**
```bash
cd frontend
npm install
npm run dev
```

**Step 4: Verify Backend is Running**
Open http://localhost:8000/docs in your browser. You should see the API documentation.

### 2. Port Already in Use

If you get "port already in use" errors:

**Windows:**
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
# Find what's using port 8000
lsof -ti:8000
# Kill the process
kill -9 $(lsof -ti:8000)
```

### 3. CORS Errors

If you see CORS errors in the browser console, make sure:
- Backend CORS_ORIGINS includes your frontend URL
- Backend is configured to allow requests from http://localhost:3000 or http://localhost:5173

### 4. Database Connection Errors

If you see database connection errors:
1. Make sure PostgreSQL is running
2. Check DATABASE_URL in your environment
3. Verify PostgreSQL is accessible on port 5432

### 5. Frontend Can't Find Backend

The frontend uses the Vite proxy when running locally. If this doesn't work:
1. Check vite.config.js has the proxy configuration
2. Make sure backend is running on http://localhost:8000
3. Try accessing http://localhost:8000/api/health directly in your browser

## Quick Diagnostic Steps

1. **Test backend directly:**
   ```
   curl http://localhost:8000/api/health
   ```
   Should return: `{"status":"healthy"}`

2. **Check backend logs** for errors

3. **Check browser console** (F12) for detailed error messages

4. **Verify all services are running:**
   - Backend: http://localhost:8000/docs
   - Frontend: http://localhost:3000
   - Database: Check with `docker ps` or `pg_isready`

## Still Having Issues?

1. Check all logs for error messages
2. Verify all dependencies are installed
3. Make sure Python 3.11+ and Node.js 18+ are installed
4. Try a fresh start:
   ```bash
   # Stop everything
   docker-compose down
   # Remove volumes (WARNING: deletes data)
   docker-compose down -v
   # Start fresh
   docker-compose up --build
   ```

