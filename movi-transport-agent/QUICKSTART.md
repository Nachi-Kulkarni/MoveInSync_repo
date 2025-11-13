# Movi Transport Agent - Quick Start Guide

## ✅ Setup Complete!

Your environment is now using **Python 3.11.5** which is fully compatible with Gradio.

## 🚀 Running the Demo

### Option 1: Quick Start (Recommended)

```bash
cd movi-transport-agent
./START_DEMO.sh
```

This will:
1. Start the backend on http://localhost:8000
2. Start the Gradio UI on http://localhost:7860
3. Open your browser to the UI

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd movi-transport-agent
source venv/bin/activate
cd backend
python3 -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd movi-transport-agent
source venv/bin/activate
cd frontend
python3 gradio_app.py
```

Then open: http://localhost:7860

### Stopping the Demo

```bash
./STOP_DEMO.sh
```

Or press `Ctrl+C` in both terminals.

---

## 📋 What's Working

✅ **Backend (Python 3.11)**
- All 10 transport tools functional
- LangGraph agent fully operational
- Multimodal input processing (Gemini 2.5 Pro)
- Session management with persistence
- Consequence checking and confirmation flow

✅ **Frontend (Python 3.11)**
- Gradio UI with 2 tabs (Dashboard + ManageRoute)
- Real-time data display from backend
- Interactive map with stop locations
- Route filtering
- Chat interface placeholder (TICKET #9)

---

## 🧪 Quick Tests

### Test Backend API:
```bash
# Check health
curl http://localhost:8000/health

# Get trips
curl http://localhost:8000/api/v1/trips

# Test agent
curl -X POST http://localhost:8000/api/v1/agent/message \
  -H "Content-Type: application/json" \
  -d '{"user_input":"How many unassigned vehicles?","session_id":"demo","context":{"page":"busDashboard"}}'
```

### Test Frontend:
- Open http://localhost:7860
- Switch between "🚌 Bus Dashboard" and "🛣️ Manage Routes" tabs
- Click refresh buttons
- Filter routes by status

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:7860 | xargs kill -9  # Frontend
```

### Backend Not Responding
```bash
# Check logs
tail -f backend/server.log
```

### Frontend Errors
```bash
# Check Gradio version
source venv/bin/activate
python3 -c "import gradio; print(gradio.__version__)"
# Should show: 5.23.1 or similar
```

---

## 📦 Environment Info

- **Python Version**: 3.11.5
- **Backend**: FastAPI + SQLAlchemy + LangGraph
- **Frontend**: Gradio 5.23.1
- **Database**: SQLite (transport.db)
- **AI Models**:
  - Claude Sonnet 4.5 (via OpenRouter)
  - Gemini 2.5 Pro (via OpenRouter)

---

## 📝 Next Steps for Interview

Your TICKET #8 (Gradio UI) is **COMPLETE** and working!

**Ready to demo:**
- ✅ Dashboard with trips and map
- ✅ Route management with filtering
- ✅ Backend API fully functional
- ✅ All data loading correctly

**Next (TICKET #9):**
- Chat interface integration
- Multimodal input (text, voice, image)
- Text-to-Speech output

---

## 🔗 Useful URLs

- Frontend: http://localhost:7860
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

**Ready for your interview! 🚀**
