from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.models import user, dataset, history  # noqa: F401 (ensures models are registered)
from app.routers import auth, datasets, query, history as history_router, reports

app = FastAPI(title="Supply Chain Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev-friendly; tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(query.router)
app.include_router(history_router.router)
app.include_router(reports.router)
