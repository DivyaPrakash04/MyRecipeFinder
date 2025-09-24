# MyRecipeFinder

Personalized Healthy Recipes: React + Flask + Cohere + Tavily (free-tier friendly)

## Project Structure
```
D:/Hackathon/MyRecipeFinder/
├─ backend/
│  ├─ app.py
│  ├─ db.py
│  ├─ models.py
│  ├─ llm.py
│  ├─ recipes.py
│  ├─ requirements.txt
│  └─ .env
└─ frontend/
   ├─ index.html
   ├─ vite.config.js
   ├─ postcss.config.js
   ├─ tailwind.config.js
   ├─ .env
   └─ src/
      ├─ main.jsx
      ├─ App.jsx
      ├─ index.css
      ├─ lib/api.js
      └─ components/
         ├─ HealthProfileCard.jsx
         ├─ RecipeSearch.jsx
         └─ Chatbot.jsx
```

## Quickstart

### 1) Backend (Flask)
1. Open PowerShell
2. Navigate to `D:/Hackathon/MyRecipeFinder/backend`
3. Create and activate venv (first time):
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate`
4. Install deps:
   - `pip install -r requirements.txt`
5. Add your API keys in `backend/.env` (see below)
6. Run API:
   - `python app.py`
7. API runs at http://localhost:4000

### 2) Frontend (React + Vite)
1. Open another terminal
2. Navigate to `D:/Hackathon/MyRecipeFinder/frontend`
3. Install deps:
   - `npm install`
4. Start dev server:
   - `npm run dev`
5. Open the shown URL (usually http://localhost:5173)

## Environment Variables (API Keys)
Edit `backend/.env`:
```
FLASK_ENV=development
PORT=4000
FRONTEND_ORIGIN=http://localhost:5173

# LLM (Cohere)
COHERE_API_KEY=your_cohere_key_here
LLM_PROVIDER=cohere
LLM_MODEL=command-r

# Search (Tavily)
TAVILY_API_KEY=your_tavily_key_here

# Database (SQLite local, Neon Postgres recommended for prod)
DATABASE_URL=sqlite:///./app.db
# DATABASE_URL=postgres://USER:PASS@HOST.neon.tech:5432/DB?sslmode=require

# MCP (optional; leave empty unless you have an MCP server installed)
MCP_TAVILY_CMD=
MCP_TAVILY_ARGS=
```
- LangChain has no API key. It orchestrates calls to Cohere and Tavily.
- Do NOT put API keys in the frontend.

## What’s Included
- Persistent chat sessions storing conversation in SQLite (or Postgres if you set `DATABASE_URL`).
- Health Profile card to capture diet, allergens, and goals used as context.
- Recipe Search via Tavily with lightweight caching in DB.
- Cohere LLM helper (`backend/llm.py`) and a switch point to add LangGraph later.
- Simple, accessible UI with clear call-to-actions.

## Deployment

Deploy to production using free services:

### Option 1: Netlify + Render (Simple)
- **Frontend**: Netlify (React app)
- **Backend**: Render (Flask API)
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions

### Option 2: Vercel + Railway (Recommended)
- **Frontend**: Vercel (React app) - Better performance and analytics
- **Backend**: Railway (Flask API) - Faster Python hosting
- See [VERCEL-DEPLOYMENT.md](./VERCEL-DEPLOYMENT.md) for details

### Quick Deploy Summary
1. Choose your preferred frontend (Vercel recommended)
2. Deploy backend to Railway or Render
3. Update environment variables
4. Test your live app!

## Troubleshooting
- If the backend can’t find keys, confirm you’re running in the same shell where `.venv` is activated and `.env` exists.
- CORS errors: verify `FRONTEND_ORIGIN` matches the frontend URL.
- Free tiers may sleep (Render/Neon). Hit `/health` first to wake.
