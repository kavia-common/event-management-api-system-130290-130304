# Event Management API Backend

FastAPI backend providing public RESTful endpoints for managing events and attendees with input validation and enforcement of business rules.

Features
- Public API (no authentication required)
- CRUD for Events (create, list, get, update, delete)
- Manage Attendees per event (register, list, remove)
- Business rules:
  - Event end_time must be after start_time
  - Event capacity cannot be set below current number of attendees
  - Each attendee email can only register once per event
- SQLite storage by default (SQLAlchemy)
- CORS configured and OpenAPI docs at /docs

Project structure
- src/api/core: config, database
- src/api/routers: route modules for events, attendees
- src/api/schemas.py: Pydantic request/response models
- src/api/models.py: SQLAlchemy ORM models
- src/api/main.py: App entrypoint

Quick start
1) Create virtual environment and install dependencies
   - pip install -r requirements.txt
2) Configure environment (optional)
   - cp .env.example .env
   - Edit .env to set DATABASE_URL
3) Run
   - uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

Events
- POST /api/events
- GET /api/events?q=&skip=0&limit=20
- GET /api/events/{id}
- PATCH /api/events/{id}
- DELETE /api/events/{id}

Attendees
- POST /api/events/{event_id}/attendees
- GET /api/events/{event_id}/attendees?skip=0&limit=20
- DELETE /api/events/{event_id}/attendees/{attendee_id}

Environment variables
- See .env.example. The orchestrator will set actual values in deployment.

Notes
- For switch to Postgres/MySQL, update DATABASE_URL accordingly (and install proper driver).
