import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.database import Base, engine
from app.routers import users

logger = logging.getLogger("uvicorn.error")


def wait_for_db(retries: int = 10, delay: float = 2.0) -> None:
    """Espera o Postgres aceitar conexões antes de criar as tabelas."""
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError:
            logger.warning("Postgres indisponível (tentativa %s/%s)...", attempt, retries)
            time.sleep(delay)
    raise RuntimeError("Não foi possível conectar ao Postgres")


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas/verificadas com sucesso")
    yield


app = FastAPI(
    title="CRUD de Usuários",
    description="API simples em FastAPI + PostgreSQL com GET, POST, PUT, PATCH e DELETE.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)


@app.get("/", tags=["health"], summary="Raiz")
def root():
    return {"mensagem": "API de usuários no ar", "docs": "/docs"}


@app.get("/health", tags=["health"], summary="Healthcheck")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "up"}
    except OperationalError:
        return {"status": "degraded", "database": "down"}
