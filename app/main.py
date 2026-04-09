import time
import logging
import json

from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.database import get_db, engine
from app import models, schemas

models.Base.metadata.create_all(bind=engine)

# ──────────────────────────────────────────────
# Logging estruturado (JSON)
# ──────────────────────────────────────────────
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log.update(record.extra)
        return json.dumps(log)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

app = FastAPI(
    title="Fundamentos de Containers — Projeto Final",
    description="API FastAPI + PostgreSQL containerizada com Docker Compose",
    version="1.0.0",
)


# ──────────────────────────────────────────────
# Middleware — log de cada request
# ──────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    logger.info(
        f"{request.method} {request.url.path} → {response.status_code}",
        extra={
            "extra": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
            }
        },
    )
    return response


# ──────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        logger.info("Health check OK", extra={"extra": {"db": "connected"}})
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        logger.error("Health check FAILED", extra={"extra": {"error": str(e)}})
        raise HTTPException(status_code=503, detail=f"DB unavailable: {str(e)}")


# ──────────────────────────────────────────────
# Itens (CRUD completo)
# ──────────────────────────────────────────────
@app.post("/items", response_model=schemas.ItemOut, status_code=201, tags=["Items"])
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    logger.info("Item criado", extra={"extra": {"item_id": db_item.id, "name": db_item.name}})
    return db_item


@app.get("/items", response_model=List[schemas.ItemOut], tags=["Items"])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Item).offset(skip).limit(limit).all()


@app.get("/items/{item_id}", response_model=schemas.ItemOut, tags=["Items"])
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


@app.put("/items/{item_id}", response_model=schemas.ItemOut, tags=["Items"])
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/items/{item_id}", status_code=204, tags=["Items"])
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(db_item)
    db.commit()
    logger.info("Item removido", extra={"extra": {"item_id": item_id}})
