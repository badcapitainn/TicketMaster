from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all models so SQLAlchemy registers them before create_all
from app.models import user, ticket, comment, ticket_history  # noqa: F401
from app.database import engine, Base
from app.routers import auth, tickets, users, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TicketMaster API",
    description=(
        "A role-based ticketing system with JWT authentication.\n\n"
        "**Roles:** `standard_user` · `agent` · `admin`\n\n"
        "Use `POST /api/auth/login` to obtain a bearer token, then click **Authorize 🔒**."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(users.router)
app.include_router(stats.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "TicketMaster API is running"}
