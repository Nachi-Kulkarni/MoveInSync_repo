# CLAUDE.md

This file provides global guidance to Claude Code (claude.ai/code) when working with code in any repository.

## Required MCP Tools Usage

**CRITICAL**: When working on ANY project, you MUST use the following MCP tools:

### For Library Documentation:
- **Context7 MCP**: Use `mcp__context7__resolve-library-id` and `mcp__context7__get-library-docs` for getting accurate, up-to-date documentation for ANY library (LangGraph, FastMCP, KiteConnect, pandas, numpy, scikit-learn, tensorflow, etc.)
- **DeepWiki MCP**: Use `mcp__deepwiki__read_wiki_structure`, `mcp__deepwiki__read_wiki_contents`, and `mcp__deepwiki__ask_question` for understanding GitHub repositories and their documentation

### For Complex Problem Solving:
- **Sequential Thinking MCP**: Use `mcp__sequential-thinking__sequentialthinking` for breaking down complex tasks, multi-step analysis, planning implementations, and working through challenging problems step-by-step

**DO NOT** rely on hallucinated or outdated information about libraries. Always fetch real documentation using these MCP tools before implementing any library-specific code. For complex tasks like architecture design, algorithm development, system integration, or multi-step implementations, use sequential thinking to ensure thorough analysis and planning.

## General Development Guidelines

- Always verify library versions and compatibility before implementation
- Use real documentation sources rather than assumptions about API behavior
- Break down complex problems into manageable steps using sequential thinking
- Leverage GitHub repository insights through DeepWiki for better understanding of project structures and conventions
- Sub-Agents Delegation Feature Implementation Plan

## Overview

This document outlines the comprehensive implementation plan for the `sub_agents` parameter feature requested in GitHub issue #911. This feature will enable true delegation where sub-agents can completely take over execution with no post-processing from the orchestrator.



### Key Components

1. **`sub_agents` Parameter**: Add to Agent constructor for specifying sub-agents
2. **Auto-Generated Tools**: Create `handoff_to_{name}` tools for each sub-agent
3. **Exception Handling**: Event loop catches delegation exceptions and transfers control
4. **Context Transfer**: Seamlessly transfer conversation history and state
5. **Complete Handoff**: Sub-agent's response becomes final response

---

## Movi Transport Agent - Project Overview

**Tech Stack:**
- **Database:** SQLite (single file, zero setup) - NOT PostgreSQL ✅
- **Backend:** FastAPI + SQLAlchemy with async support ✅
- **Multimodal:** Gemini 2.5 Pro via OpenRouter ✅
- **Agent:** LangGraph with Claude Sonnet 4.5 via OpenRouter (to be implemented)
- **Observability:** LangSmith for agent tracing and debugging (to be implemented)
- **Frontend:** React + Vite + TypeScript (to be implemented)

**Implementation Status:**
- ✅ TICKET #1: Database (SQLite with init.sql)
- ✅ TICKET #2: Backend API Foundation (FastAPI + SQLAlchemy + 5 endpoints)
- ✅ TICKET #3: Tool Functions (10 tools + Pydantic schemas + TOOL_REGISTRY)
- ✅ TICKET #4: Multimodal Input Processor (Gemini 2.5 Pro via OpenRouter)
- ⏳ TICKET #5-12: Pending

---

## Movi Transport Agent - Project Structure

```
movi-transport-agent/
├── README.md                              # TICKET #12
├── .env.example                           # TICKET #1, #2
├── .gitignore                             # TICKET #1
├── docker-compose.yml                     # TICKET #1 (Optional: NOT USED - Using SQLite instead)
│
├── backend/                               # FastAPI Backend ✅
│   ├── requirements.txt                   # ✅ TICKET #2
│   ├── .env                               # ✅ TICKET #2
│   ├── main.py                            # ✅ TICKET #2 (FastAPI app entry point)
│   │
│   ├── app/
│   │   ├── __init__.py                    # ✅ TICKET #2
│   │   │
│   │   ├── core/                          # Core configurations ✅
│   │   │   ├── __init__.py                # ✅ TICKET #2
│   │   │   ├── config.py                  # ✅ TICKET #2 (Environment variables, settings)
│   │   │   └── database.py                # ✅ TICKET #2 (SQLite connection, session management)
│   │   │
│   │   ├── models/                        # SQLAlchemy ORM Models ✅
│   │   │   ├── __init__.py                # ✅ TICKET #2
│   │   │   ├── stop.py                    # ✅ TICKET #2 (Stop model)
│   │   │   ├── path.py                    # ✅ TICKET #2 (Path model)
│   │   │   ├── route.py                   # ✅ TICKET #2 (Route model)
│   │   │   ├── vehicle.py                 # ✅ TICKET #2 (Vehicle model)
│   │   │   ├── driver.py                  # ✅ TICKET #2 (Driver model)
│   │   │   ├── daily_trip.py              # ✅ TICKET #2 (DailyTrip model)
│   │   │   ├── deployment.py              # ✅ TICKET #2 (Deployment model)
│   │   │   └── session.py                 # TICKET #5 (Agent session state persistence)
│   │   │
│   │   ├── schemas/                       # Pydantic models for request/response ✅
│   │   │   ├── __init__.py                # ✅ TICKET #2
│   │   │   ├── trip.py                    # ✅ TICKET #2
│   │   │   ├── route.py                   # ✅ TICKET #2
│   │   │   ├── agent.py                   # TICKET #7 (Agent request/response schemas)
│   │   │   └── tool.py                    # ✅ TICKET #3 (Tool request/response schemas + metadata)
│   │   │
│   │   ├── api/                           # API Routes ✅
│   │   │   ├── __init__.py                # ✅ TICKET #2
│   │   │   ├── deps.py                    # ✅ TICKET #2 (Dependencies: DB session, etc.)
│   │   │   └── v1/
│   │   │       ├── __init__.py            # ✅ TICKET #2
│   │   │       ├── trips.py               # ✅ TICKET #2 (GET /api/trips, etc.)
│   │   │       ├── routes.py              # ✅ TICKET #2 (GET /api/routes, etc.)
│   │   │       ├── stops.py               # ✅ TICKET #2 (GET /api/stops, etc.)
│   │   │       ├── vehicles.py            # ✅ TICKET #2 (GET /api/vehicles/unassigned, etc.)
│   │   │       └── agent.py               # TICKET #7 (POST /api/agent/message, /confirm, etc.)
│   │   │
│   │   ├── agent/                         # LangGraph Agent Logic
│   │   │   ├── __init__.py                # TICKET #5
│   │   │   ├── graph.py                   # TICKET #5 (StateGraph definition, nodes, edges)
│   │   │   ├── state.py                   # TICKET #5 (AgentState TypedDict)
│   │   │   ├── nodes/                     # Individual node implementations
│   │   │   │   ├── __init__.py            # TICKET #5
│   │   │   │   ├── preprocess.py          # TICKET #5 (preprocess_input_node)
│   │   │   │   ├── classify.py            # TICKET #5 (classify_intent_node)
│   │   │   │   ├── consequences.py        # TICKET #5, #10 (check_consequences_node)
│   │   │   │   ├── confirmation.py        # TICKET #5, #10 (request_confirmation_node)
│   │   │   │   ├── execute.py             # TICKET #5, #6 (execute_action_node)
│   │   │   │   └── format.py              # TICKET #5 (format_response_node)
│   │   │   ├── edges.py                   # TICKET #5 (Conditional edge functions)
│   │   │   └── prompts.py                 # TICKET #5 (System prompts for Claude)
│   │   │
│   │   ├── tools/                         # Tool Functions ✅
│   │   │   ├── __init__.py                # ✅ TICKET #3 (TOOL_REGISTRY + exports)
│   │   │   ├── base.py                    # ✅ TICKET #3 (success_response, error_response helpers)
│   │   │   ├── read_tools.py              # ✅ TICKET #3 (4 read operations - 315 lines)
│   │   │   ├── create_tools.py            # ✅ TICKET #3 (4 create operations - 374 lines)
│   │   │   ├── delete_tools.py            # ✅ TICKET #3 (remove_vehicle_from_trip - 93 lines)
│   │   │   └── consequence_tools.py       # ✅ TICKET #3, #10 (Tribal knowledge checker - 294 lines)
│   │   │
│   │   ├── multimodal/                    # Multimodal Processing ✅
│   │   │   ├── __init__.py                # ✅ TICKET #4
│   │   │   ├── gemini_wrapper.py          # ✅ TICKET #4 (Gemini 2.5 Pro integration)
│   │   │   ├── audio_processor.py         # ✅ TICKET #4 (STT handling)
│   │   │   ├── image_processor.py         # ✅ TICKET #4 (Image extraction)
│   │   │   └── video_processor.py         # ✅ TICKET #4 (Video extraction)
│   │   │
│   │   └── utils/                         # Utility functions
│   │       ├── __init__.py                # ✅ TICKET #2
│   │       ├── openrouter.py              # ✅ TICKET #4 (OpenRouter API client)
│   │       ├── retry.py                   # TICKET #6 (Retry logic with backoff)
│   │       └── logger.py                  # ✅ TICKET #2 (Logging configuration)
│   │
│   └── tests/                             # Tests
│       ├── __init__.py                    # TICKET #11
│       ├── test_tools.py                  # TICKET #11
│       ├── test_agent.py                  # TICKET #11
│       └── test_api.py                    # TICKET #11
│
├── frontend/                              # React Frontend
│   ├── package.json                       # TICKET #8
│   ├── package-lock.json                  # TICKET #8
│   ├── tsconfig.json                      # TICKET #8
│   ├── vite.config.ts                     # TICKET #8
│   ├── index.html                         # TICKET #8
│   ├── .env.local                         # TICKET #8
│   │
│   ├── public/
│   │   └── favicon.ico                    # TICKET #8
│   │
│   └── src/
│       ├── main.tsx                       # TICKET #8 (App entry point)
│       ├── App.tsx                        # TICKET #8 (Root component with routing)
│       │
│       ├── pages/                         # Page Components
│       │   ├── Dashboard.tsx              # TICKET #8 (busDashboard page)
│       │   └── ManageRoute.tsx            # TICKET #8 (manageRoute page)
│       │
│       ├── components/                    # Reusable Components
│       │   ├── layout/
│       │   │   ├── Sidebar.tsx            # TICKET #8
│       │   │   └── Header.tsx             # TICKET #8
│       │   │
│       │   ├── dashboard/
│       │   │   ├── TripList.tsx           # TICKET #8
│       │   │   ├── TripCard.tsx           # TICKET #8
│       │   │   └── MapView.tsx            # TICKET #8
│       │   │
│       │   ├── routes/
│       │   │   ├── RouteTable.tsx         # TICKET #8
│       │   │   └── RouteRow.tsx           # TICKET #8
│       │   │
│       │   └── chat/                      # Movi Chat Interface
│       │       ├── ChatInterface.tsx      # TICKET #9 (Main chat component)
│       │       ├── MessageList.tsx        # TICKET #9
│       │       ├── MessageBubble.tsx      # TICKET #9
│       │       ├── ChatInput.tsx          # TICKET #9
│       │       ├── VoiceRecorder.tsx      # TICKET #9
│       │       ├── FileUploader.tsx       # TICKET #9
│       │       └── ConfirmationDialog.tsx # TICKET #9, #10
│       │
│       ├── hooks/                         # Custom React hooks
│       │   ├── useAgent.ts                # TICKET #9 (Hook for agent interaction)
│       │   ├── useVoiceRecorder.ts        # TICKET #9
│       │   └── usePageContext.ts          # TICKET #9
│       │
│       ├── api/                           # API Client
│       │   ├── client.ts                  # TICKET #8 (Axios instance)
│       │   ├── agent.ts                   # TICKET #9 (Agent API calls)
│       │   ├── trips.ts                   # TICKET #8
│       │   ├── routes.ts                  # TICKET #8
│       │   └── types.ts                   # TICKET #8 (TypeScript interfaces)
│       │
│       ├── store/                         # State Management (Context or Zustand)
│       │   ├── agentStore.ts              # TICKET #9 (Agent conversation state)
│       │   └── appStore.ts                # TICKET #8 (App-wide state)
│       │
│       ├── utils/
│       │   ├── audio.ts                   # TICKET #9 (Audio recording utilities)
│       │   └── fileHandler.ts             # TICKET #9 (File upload helpers)
│       │
│       └── styles/
│           ├── index.css                  # TICKET #8 (Global styles)
│           └── tailwind.css               # TICKET #8 (Tailwind imports)
│
├── database/                              # Database Setup (SQLite)
│   ├── init.sql                           # TICKET #1 ✅ COMPLETE (Schema + Seed data combined)
│   └── transport.db                       # TICKET #1 ✅ COMPLETE (SQLite database file - 48KB)
│
├── docs/                                  # Documentation
│   ├── architecture.md                    # TICKET #12 (Architecture explanation)
│   ├── langgraph_design.md                # TICKET #12 (LangGraph state/nodes/edges details)
│   ├── api_documentation.md               # TICKET #12 (API endpoints reference)
│   └── diagrams/
│       ├── agent_flow.mermaid             # TICKET #12 (LangGraph flow diagram)
│       └── system_architecture.png        # TICKET #12
│
├── scripts/                               # Utility Scripts
│   ├── run_backend.sh                     # TICKET #2 (Start backend server)
│   ├── run_frontend.sh                    # TICKET #8 (Start frontend dev server)
│   └── test_integration.sh                # TICKET #11 (Run integration tests)
│
└── demo/                                  # Demo Materials
    ├── demo_video.mp4                     # TICKET #12 (2-5 min demo video)
    ├── screenshots/
    │   ├── dashboard.png                  # TICKET #12
    │   ├── manage_route.png               # TICKET #12
    │   └── chat_interface.png             # TICKET #12
    └── test_images/                       # TICKET #11 (Sample images for testing)
        └── dashboard_screenshot.png       # TICKET #11
```

### Ticket-to-Component Mapping

- **TICKET #1**: ✅ COMPLETE - SQLite database (single init.sql file with schema + seed data, no migrations, no Docker)
- **TICKET #2**: ✅ COMPLETE - Backend foundation, FastAPI setup, SQLAlchemy models, 5 API endpoints
- **TICKET #3**: ✅ COMPLETE - 10 tool functions + Pydantic schemas + TOOL_REGISTRY + TOOL_METADATA_REGISTRY (read/create/delete operations)
- **TICKET #4**: ✅ COMPLETE - Multimodal input processing with Gemini 2.5 Pro via OpenRouter
- **TICKET #5**: ⏳ PENDING - LangGraph agent core (6 nodes, state management, graph definition)
- **TICKET #6**: Agent-tool integration, orchestration, retry logic
- **TICKET #7**: Agent API endpoints for frontend interaction
- **TICKET #8**: React UI foundation (2 pages: Dashboard, ManageRoute)
- **TICKET #9**: Chat interface with voice/text/file upload
- **TICKET #10**: Consequence checking and confirmation flow (tribal knowledge)
- **TICKET #11**: End-to-end integration testing
- **TICKET #12**: Demo video and comprehensive documentation

---

## Implementation Notes

### TICKET #1: Database Setup (COMPLETED)

**Technology Decision:** SQLite instead of PostgreSQL
- **Rationale:** Zero setup, single file database, perfect for prototype
- **File:** `database/init.sql` (combined schema + seed data)
- **Database:** `database/transport.db` (48KB)

**Schema:**
- 7 tables: stops, paths, routes, vehicles, drivers, daily_trips, deployments
- Foreign key relationships properly defined
- Paths store ordered stop IDs as JSON text: `"[1,3,5,7]"`
- Routes reference paths and include time/status
- Daily trips have booking_percentage (0-100)
- Deployments link trips to vehicles/drivers

**Seed Data:**
- 10 stops (Gavipuram, Peenya, Temple, BTM, Hebbal, Madiwala, Jayanagar, Koramangala, Electronic City, Whitefield)
- 4 paths with ordered stop sequences
- 12 routes (11 active, 1 deactivated)
- 6 vehicles (3 Bus, 3 Cab)
- 5 drivers
- 8 daily trips (including critical "Bulk - 00:01" at 25% booking for consequence testing)
- 3 deployments (some trips have vehicles, some don't)

**Initialization:**
```bash
cd movi-transport-agent
sqlite3 database/transport.db < database/init.sql
```

**Verification Queries:**
```bash
# Count records
sqlite3 database/transport.db "SELECT COUNT(*) FROM daily_trips;"

# Check consequence scenario
sqlite3 database/transport.db "SELECT * FROM daily_trips WHERE display_name='Bulk - 00:01';"

# Count unassigned vehicles
sqlite3 database/transport.db "SELECT COUNT(*) FROM vehicles v LEFT JOIN deployments d ON v.vehicle_id = d.vehicle_id WHERE d.deployment_id IS NULL;"
```

**Key Testing Features:**
- "Bulk - 00:01" trip has 25% booking and assigned vehicle (HIGH_RISK for removal)
- 3 unassigned vehicles available for deployment
- Mix of active/deactivated routes
- Proper foreign key relationships for JOIN queries

**Database Design Pattern:**
- Stop → Path → Route → Trip hierarchy properly implemented
- Deployments as link table between trips and vehicles/drivers
- JSON storage for ordered stop IDs (avoids junction table complexity)
- Booking percentage enables consequence flow testing

---

### TICKET #2: Backend API Foundation (COMPLETED)

**Technology Stack:**
- **Framework:** FastAPI (async/await support)
- **ORM:** SQLAlchemy 2.0 with async support (aiosqlite)
- **Validation:** Pydantic v2 for request/response schemas
- **Server:** Uvicorn with auto-reload

**Project Structure:**
```
backend/
├── requirements.txt          # Dependencies with >= versions for Python 3.14 compatibility
├── .env                      # Environment variables
├── main.py                   # FastAPI app entry point with CORS
└── app/
    ├── core/
    │   ├── config.py         # Settings with absolute database path resolution
    │   └── database.py       # Async SQLAlchemy engine and session
    ├── models/               # 7 SQLAlchemy ORM models
    │   ├── stop.py
    │   ├── path.py
    │   ├── route.py
    │   ├── vehicle.py
    │   ├── driver.py
    │   ├── daily_trip.py
    │   └── deployment.py
    ├── schemas/              # Pydantic response models
    │   ├── trip.py           # TripResponse, TripConsequence
    │   └── route.py          # RouteResponse, StopResponse
    └── api/
        ├── deps.py           # Database session dependency
        └── v1/               # API v1 endpoints
            ├── trips.py      # 2 endpoints
            ├── routes.py     # 1 endpoint
            ├── stops.py      # 1 endpoint
            └── vehicles.py   # 1 endpoint
```

**7 SQLAlchemy ORM Models:**
All models use async-compatible Base class and map to existing database tables:
1. **Stop** - Geographic locations (stop_id, name, latitude, longitude)
2. **Path** - Ordered stop sequences (path_id, path_name, ordered_stop_ids as TEXT/JSON)
3. **Route** - Path + Time combinations (route_id, path_id, shift_time, direction, status)
4. **Vehicle** - Transport assets (vehicle_id, license_plate, type, capacity)
5. **Driver** - Human resources (driver_id, name, phone_number)
6. **DailyTrip** - Daily route instances (trip_id, route_id, booking_percentage, live_status)
7. **Deployment** - Vehicle/Driver assignments (deployment_id, trip_id, vehicle_id, driver_id)

**5 API Endpoints (All Working ✅):**

1. **GET /api/v1/trips** (backend/app/api/v1/trips.py:145)
   - Returns: List of all daily trips with booking percentages
   - Test: `curl http://localhost:8000/api/v1/trips`
   - Response: 8 trips including "Bulk - 00:01" at 25% booking

2. **GET /api/v1/routes** (backend/app/api/v1/routes.py:106)
   - Returns: List of all routes with path references
   - Test: `curl http://localhost:8000/api/v1/routes`
   - Response: 12 routes (11 active, 1 deactivated)

3. **GET /api/v1/stops** (backend/app/api/v1/stops.py:125)
   - Returns: List of all stops with coordinates
   - Test: `curl http://localhost:8000/api/v1/stops`
   - Response: 10 stops across Bangalore

4. **GET /api/v1/vehicles/unassigned** (backend/app/api/v1/vehicles.py:206)
   - Returns: Count of vehicles without deployments
   - Test: `curl http://localhost:8000/api/v1/vehicles/unassigned`
   - Response: `{"unassigned_count": 3}`

5. **GET /api/v1/trips/{trip_id}/consequences** (backend/app/api/v1/trips.py:153)
   - Returns: Risk analysis for trip actions (tribal knowledge)
   - Test: `curl http://localhost:8000/api/v1/trips/1/consequences`
   - Response: HIGH RISK - "Trip is 25% booked. Removing vehicle will cancel bookings..."

**Key Implementation Details:**

**Database Path Resolution** (backend/app/core/config.py:6-8):
- Fixed SQLite connection using absolute path resolution
- Computed at module level: `BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent`
- Prevents "unable to open database file" errors when running from different directories

**Async Database Session** (backend/app/core/database.py):
- `AsyncSessionLocal` factory using `async_sessionmaker`
- `get_db()` dependency for dependency injection
- Properly closes sessions after requests

**CORS Configuration** (backend/main.py):
- Enabled for `localhost:3000` (React) and `localhost:5173` (Vite)
- Allows credentials, all methods, all headers

**Dependencies:**
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy[asyncio]>=2.0.36
aiosqlite>=0.20.0
pydantic>=2.10.0
pydantic-settings>=2.6.0
python-dotenv>=1.0.1
```

**Server Startup:**
```bash
cd backend
../venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Testing Results:**
- ✅ All 5 endpoints returning correct data
- ✅ Database queries working with async SQLAlchemy
- ✅ Foreign key relationships properly resolved
- ✅ Consequence logic correctly identifies high-risk trips
- ✅ Server auto-reload working on code changes

**Critical Fix:**
- Initial issue: Relative database path failed when running from backend/ directory
- Solution: Absolute path computation using `Path(__file__).resolve()`
- Result: Database connection works regardless of execution directory

---

### TICKET #4: Multimodal Input Processor (COMPLETED)

**Technology Stack:**
- **API:** OpenRouter (https://openrouter.ai)
- **Model:** Gemini 2.5 Pro (`google/gemini-2.5-pro`)
- **HTTP Client:** httpx (async support)
- **File Formats:**
  - Images: JPEG, PNG, WebP, GIF
  - Audio: WAV, MP3
  - Video: MP4, MPEG, MOV, WebM

**Components Implemented:**

1. **OpenRouter API Client** (`app/utils/openrouter.py`)
   - `OpenRouterClient`: Async HTTP client for chat completions
   - `create_text_content()`: Text message formatting
   - `create_image_content()`: Image URL or base64 formatting
   - `create_audio_content()`: Audio base64 formatting (URLs not supported)
   - `create_video_content()`: Video URL or base64 formatting

2. **Gemini Multimodal Processor** (`app/multimodal/gemini_wrapper.py`)
   - `GeminiMultimodalProcessor`: Core processor for all modalities
   - `MultimodalInput`: Input data class
   - **Features:**
     - Context-aware processing (knows current UI page)
     - Structured entity extraction (trip IDs, vehicle IDs, action intents)
     - Transport-specific system prompt
     - JSON output with markdown cleanup

3. **Audio Processor** (`app/multimodal/audio_processor.py`)
   - `transcribe_audio()`: Transcribe audio to text with entity extraction
   - `process_voice_command()`: Process voice commands for transport operations

4. **Image Processor** (`app/multimodal/image_processor.py`)
   - `analyze_screenshot()`: Analyze UI screenshots
   - `extract_ui_elements()`: Extract specific UI elements
   - `process_annotated_screenshot()`: Process screenshots with visual indicators (arrows, circles)

5. **Video Processor** (`app/multimodal/video_processor.py`)
   - `analyze_video()`: Analyze video with temporal context
   - `extract_key_frames()`: Extract key frames from video
   - `process_ui_demo_video()`: Process UI demo videos
   - `stream_video_analysis()`: Handle longer videos (>30s)

**Structured Output Format:**
```python
{
    "original_text": str,
    "modality": "text|audio|image|video|mixed",
    "comprehension": str,  # What Gemini understood
    "extracted_entities": {
        "trip_ids": ["Bulk - 00:01", ...],
        "vehicle_ids": ["MH-12-3456", ...],
        "stop_names": ["Gavipuram", ...],
        "path_names": ["Path-1", ...],
        "route_names": ["Path2 - 19:45", ...],
        "visual_indicators": ["arrow pointing to row", ...],
        "action_intent": "remove_vehicle|assign_vehicle|create_stop|list_trips|..."
    },
    "confidence": "high|medium|low"
}
```

**Configuration:**
```bash
# .env file
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**Dependencies Added:**
```
httpx>=0.27.0
```

**Testing:**
```bash
cd movi-transport-agent/backend
python3 -m pip install -r requirements.txt
python3 test_multimodal.py
```

**Test Results (All Passing ✅):**
1. ✅ Text-only input: Correctly identified `list_unassigned_vehicles` intent
2. ✅ Image URL processing: Correctly handled non-transport images
3. ✅ Mixed input (text + image): Successfully combined modalities
4. ✅ Structured output validation: Correctly extracted:
   - Input: "Remove vehicle MH-12-3456 from Bulk - 00:01 trip"
   - Action Intent: `remove_vehicle`
   - Trip IDs: `['Bulk - 00:01']`
   - Vehicle IDs: `['MH-12-3456']`

**Key Features:**
- **Context Awareness:** Knows current page (busDashboard vs manageRoute)
- **Transport-Specific Prompts:** Understands Stop → Path → Route → Trip flow
- **Multimodal Support:** Text, audio, image, video in any combination
- **Entity Extraction:** Structured data extraction for downstream processing
- **Error Handling:** Graceful fallbacks for JSON parsing errors
- **Markdown Cleanup:** Automatically strips ```json code blocks from responses

**Integration Point for LangGraph (TICKET #5):**
The multimodal processor will be integrated as a preprocessing node:
```
User Input → [preprocess_input_node] → [classify_intent_node] → ...
                     ↓
            (Uses GeminiMultimodalProcessor
             to handle all input types)
```

**Files Created:**
- `backend/app/utils/openrouter.py`
- `backend/app/multimodal/__init__.py`
- `backend/app/multimodal/gemini_wrapper.py`
- `backend/app/multimodal/audio_processor.py`
- `backend/app/multimodal/image_processor.py`
- `backend/app/multimodal/video_processor.py`
- `backend/test_multimodal.py`
- `backend/TICKET4_IMPLEMENTATION.md`

---

## LangSmith Observability Setup

**Purpose:** Enable comprehensive tracing and debugging for LangGraph agents.

### Configuration (TICKET #5)

**Environment Variables:**
```bash
# Add to backend/.env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=movi-transport-agent
```

**Get API Key:**
1. Create account at https://smith.langchain.com/
2. Navigate to Settings → API Keys
3. Create new API key
4. Add to `.env` file

### What LangSmith Provides:

1. **Agent Flow Visualization**
   - See entire graph execution path
   - Node-by-node state transitions
   - Conditional edge decisions visualized

2. **LLM Call Tracking**
   - All Claude/Gemini API calls logged
   - Token usage per call
   - Latency metrics
   - Prompt and response content

3. **Debugging Tools**
   - Trace specific runs by ID
   - Compare different executions
   - Identify bottlenecks
   - Error tracking with stack traces

4. **Performance Monitoring**
   - Average latency per node
   - Token consumption analysis
   - Success/failure rates
   - User feedback integration

### Integration in Code (TICKET #5):

```python
# backend/app/agent/graph.py
import os
from langsmith import traceable

# Set environment variables (from .env)
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "movi-transport-agent")

# Decorate nodes for automatic tracing
@traceable(run_type="chain", name="preprocess_input")
async def preprocess_input_node(state: AgentState):
    # Node implementation
    pass

@traceable(run_type="chain", name="classify_intent")
async def classify_intent_node(state: AgentState):
    # Node implementation with LLM calls
    # All Claude API calls automatically traced
    pass
```

### Viewing Traces:

1. Run your agent
2. Navigate to https://smith.langchain.com/
3. Select project: `movi-transport-agent`
4. View traces in real-time
5. Click on any trace to see:
   - Full execution graph
   - State at each node
   - LLM prompts and responses
   - Token usage
   - Latency per step

### Benefits for This Project:

- **Consequence Flow Debugging:** See exactly when and why confirmation is triggered
- **Multimodal Processing:** Trace how Gemini processes images/audio
- **Intent Classification:** Debug Claude's entity extraction
- **Tool Execution:** Monitor which tools are called and their results
- **State Management:** Track state changes through the graph
- **Performance Optimization:** Identify slow nodes or excessive token usage
