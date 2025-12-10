# India Job Map - Backend

FastAPI backend for the India Job Map agentic system.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

- `GET /` - Health check
- `GET /pins` - Get job markers for map display

first run backend 
cd backend
.\venv\Scripts\activate     # Windows
uvicorn app.main:app --reload --port 8000
 
then run frontend 
npm run dev