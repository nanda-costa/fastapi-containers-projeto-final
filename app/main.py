import logging
import time
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)


class ColorFormatter(logging.Formatter):
    """Formatter simples com ANSI colors para logs no terminal."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    METHOD_COLORS = {
        "GET": "\033[34m",
        "POST": "\033[32m",
        "PUT": "\033[33m",
        "PATCH": "\033[35m",
        "DELETE": "\033[31m",
    }

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        level_color = self.COLORS.get(record.levelname, self.RESET)
        level = f"{level_color}{self.BOLD}{record.levelname:<8}{self.RESET}"

        method = getattr(record, "method", None)
        path = getattr(record, "path", None)
        status_code = getattr(record, "status_code", None)
        duration_ms = getattr(record, "duration_ms", None)
        client_ip = getattr(record, "client_ip", None)

        if method:
            method_color = self.METHOD_COLORS.get(method, self.RESET)
            method_text = f"{method_color}{method}{self.RESET}"
        else:
            method_text = None

        parts = [f"[{timestamp}]", level, record.getMessage()]

        if method_text and path:
            parts.append(f"{method_text} {path}")
        if status_code is not None:
            parts.append(f"status={status_code}")
        if duration_ms is not None:
            parts.append(f"duration={duration_ms}ms")
        if client_ip:
            parts.append(f"ip={client_ip}")

        return " | ".join(parts)


handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(handler)
logger.propagate = False

app = FastAPI(
    title="Gestor PD&I Track",
    description="API FastAPI + PostgreSQL containerizada com Docker Compose",
    version="1.1.0",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "Request processada",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else None,
        },
    )
    return response


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        logger.info("Health check OK")
        return {"status": "ok", "db": "connected"}
    except Exception as exc:
        logger.error(f"Health check FAILED: {exc}")
        raise HTTPException(status_code=503, detail=f"DB unavailable: {exc}")


@app.post(
    "/projetos",
    response_model=schemas.ProjetoOut,
    status_code=201,
    tags=["Projetos"],
)
def create_projeto(projeto: schemas.ProjetoCreate, db: Session = Depends(get_db)):
    db_projeto = models.Projeto(**projeto.model_dump())
    db.add(db_projeto)
    db.commit()
    db.refresh(db_projeto)
    logger.info(f"Projeto criado: id={db_projeto.id}")
    return db_projeto


@app.get("/projetos", response_model=List[schemas.ProjetoOut], tags=["Projetos"])
def list_projetos(db: Session = Depends(get_db)):
    return db.query(models.Projeto).all()


@app.get(
    "/projetos/{projeto_id}",
    response_model=schemas.ProjetoOut,
    tags=["Projetos"],
)
def get_projeto(projeto_id: int, db: Session = Depends(get_db)):
    projeto = db.query(models.Projeto).filter(models.Projeto.id == projeto_id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return projeto


@app.put(
    "/projetos/{projeto_id}",
    response_model=schemas.ProjetoOut,
    tags=["Projetos"],
)
def update_projeto(
    projeto_id: int,
    projeto: schemas.ProjetoCreate,
    db: Session = Depends(get_db),
):
    db_projeto = (
        db.query(models.Projeto).filter(models.Projeto.id == projeto_id).first()
    )
    if not db_projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    for key, value in projeto.model_dump().items():
        setattr(db_projeto, key, value)

    db.commit()
    db.refresh(db_projeto)
    logger.info(f"Projeto atualizado: id={db_projeto.id}")
    return db_projeto


@app.delete("/projetos/{projeto_id}", status_code=204, tags=["Projetos"])
def delete_projeto(projeto_id: int, db: Session = Depends(get_db)):
    db_projeto = (
        db.query(models.Projeto).filter(models.Projeto.id == projeto_id).first()
    )
    if not db_projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    for item in db_projeto.items:
        item.idprojeto = None

    db.delete(db_projeto)
    db.commit()
    logger.info(f"Projeto removido: id={projeto_id}")


@app.post(
    "/items",
    response_model=schemas.ItemOut,
    status_code=201,
    tags=["Items"],
)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    if item.idprojeto is not None:
        projeto = (
            db.query(models.Projeto).filter(models.Projeto.id == item.idprojeto).first()
        )
        if not projeto:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")

    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    logger.info(f"Item criado: id={db_item.id}, nome={db_item.name}")
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

    if item.idprojeto is not None:
        projeto = (
            db.query(models.Projeto).filter(models.Projeto.id == item.idprojeto).first()
        )
        if not projeto:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")

    for key, value in item.model_dump().items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    logger.info(f"Item atualizado: id={db_item.id}")
    return db_item


@app.delete("/items/{item_id}", status_code=204, tags=["Items"])
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    retirada_aberta = (
        db.query(models.Withdrawal)
        .filter(
            models.Withdrawal.item_id == item_id,
            models.Withdrawal.devolvido_em.is_(None),
        )
        .first()
    )
    if retirada_aberta:
        raise HTTPException(
            status_code=409,
            detail="Item possui retirada em aberto e não pode ser removido",
        )

    db.delete(db_item)
    db.commit()
    logger.info(f"Item removido: id={item_id}")


@app.post(
    "/bolsistas",
    response_model=schemas.StudentOut,
    status_code=201,
    tags=["Bolsistas"],
)
def create_bolsista(bolsista: schemas.StudentCreate, db: Session = Depends(get_db)):
    existente = (
        db.query(models.Student).filter(models.Student.cpf == bolsista.cpf).first()
    )
    if existente:
        raise HTTPException(status_code=409, detail="CPF já cadastrado")

    db_bolsista = models.Student(**bolsista.model_dump())
    db.add(db_bolsista)
    db.commit()
    db.refresh(db_bolsista)
    logger.info(f"Bolsista cadastrado: cpf={db_bolsista.cpf}")
    return db_bolsista


@app.get("/bolsistas", response_model=List[schemas.StudentOut], tags=["Bolsistas"])
def list_bolsistas(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@app.get(
    "/bolsistas/{cpf}",
    response_model=schemas.StudentOut,
    tags=["Bolsistas"],
)
def get_bolsista(cpf: str, db: Session = Depends(get_db)):
    bolsista = db.query(models.Student).filter(models.Student.cpf == cpf).first()
    if not bolsista:
        raise HTTPException(status_code=404, detail="Bolsista não encontrado")
    return bolsista


@app.put(
    "/bolsistas/{bolsista_id}",
    response_model=schemas.StudentOut,
    tags=["Bolsistas"],
)
def update_bolsista(
    bolsista_id: int,
    bolsista: schemas.StudentCreate,
    db: Session = Depends(get_db),
):
    db_bolsista = (
        db.query(models.Student).filter(models.Student.id == bolsista_id).first()
    )
    if not db_bolsista:
        raise HTTPException(status_code=404, detail="Bolsista não encontrado")

    if bolsista.cpf != db_bolsista.cpf:
        conflito = (
            db.query(models.Student).filter(models.Student.cpf == bolsista.cpf).first()
        )
        if conflito:
            raise HTTPException(status_code=409, detail="CPF já cadastrado")

    for key, value in bolsista.model_dump().items():
        setattr(db_bolsista, key, value)

    db.commit()
    db.refresh(db_bolsista)
    logger.info(f"Bolsista atualizado: id={db_bolsista.id}")
    return db_bolsista


@app.delete("/bolsistas/{bolsista_id}", status_code=204, tags=["Bolsistas"])
def delete_bolsista(bolsista_id: int, db: Session = Depends(get_db)):
    db_bolsista = (
        db.query(models.Student).filter(models.Student.id == bolsista_id).first()
    )
    if not db_bolsista:
        raise HTTPException(status_code=404, detail="Bolsista não encontrado")

    retirada_aberta = (
        db.query(models.Withdrawal)
        .filter(
            models.Withdrawal.student_id == bolsista_id,
            models.Withdrawal.devolvido_em.is_(None),
        )
        .first()
    )
    if retirada_aberta:
        raise HTTPException(
            status_code=409,
            detail="Bolsista possui retiradas em aberto e não pode ser removido",
        )

    db.delete(db_bolsista)
    db.commit()
    logger.info(f"Bolsista removido: id={bolsista_id}")


@app.post(
    "/retiradas",
    response_model=schemas.WithdrawalOut,
    status_code=201,
    tags=["Retiradas"],
)
def create_retirada(
    retirada: schemas.WithdrawalCreate,
    db: Session = Depends(get_db),
):
    item = db.query(models.Item).filter(models.Item.id == retirada.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    if not item.active:
        raise HTTPException(
            status_code=409,
            detail="Item inativo e não pode ser retirado",
        )

    bolsista = (
        db.query(models.Student).filter(models.Student.cpf == retirada.cpf).first()
    )
    if not bolsista:
        raise HTTPException(
            status_code=404,
            detail="Bolsista não encontrado para esse CPF",
        )

    retirada_aberta = (
        db.query(models.Withdrawal)
        .filter(
            models.Withdrawal.item_id == retirada.item_id,
            models.Withdrawal.devolvido_em.is_(None),
        )
        .first()
    )
    if retirada_aberta:
        raise HTTPException(
            status_code=409,
            detail=f"Item já retirado pelo CPF {retirada.cpf}",
        )

    db_retirada = models.Withdrawal(item_id=item.id, student_id=bolsista.id)
    db.add(db_retirada)
    db.commit()
    db.refresh(db_retirada)
    logger.info(f"Retirada criada: id={db_retirada.id}")
    return db_retirada


@app.get(
    "/retiradas",
    response_model=List[schemas.WithdrawalOut],
    tags=["Retiradas"],
)
def list_retiradas(
    apenas_abertas: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(models.Withdrawal)
    if apenas_abertas:
        query = query.filter(models.Withdrawal.devolvido_em.is_(None))
    return query.all()


@app.get(
    "/retiradas/{retirada_id}",
    response_model=schemas.WithdrawalOut,
    tags=["Retiradas"],
)
def get_retirada(retirada_id: int, db: Session = Depends(get_db)):
    retirada = (
        db.query(models.Withdrawal).filter(models.Withdrawal.id == retirada_id).first()
    )
    if not retirada:
        raise HTTPException(status_code=404, detail="Retirada não encontrada")
    return retirada


@app.get(
    "/retiradas/bolsista/{cpf}",
    response_model=List[schemas.WithdrawalOut],
    tags=["Retiradas"],
)
def retiradas_por_bolsista(cpf: str, db: Session = Depends(get_db)):
    bolsista = db.query(models.Student).filter(models.Student.cpf == cpf).first()
    if not bolsista:
        raise HTTPException(status_code=404, detail="Bolsista não encontrado")

    return (
        db.query(models.Withdrawal)
        .filter(models.Withdrawal.student_id == bolsista.id)
        .all()
    )


@app.patch(
    "/retiradas/{retirada_id}/devolver",
    response_model=schemas.WithdrawalOut,
    tags=["Retiradas"],
)
def devolver_item(retirada_id: int, db: Session = Depends(get_db)):
    retirada = (
        db.query(models.Withdrawal).filter(models.Withdrawal.id == retirada_id).first()
    )
    if not retirada:
        raise HTTPException(status_code=404, detail="Retirada não encontrada")

    if retirada.devolvido_em is not None:
        raise HTTPException(status_code=409, detail="Item já foi devolvido")

    retirada.devolvido_em = datetime.utcnow()
    db.commit()
    db.refresh(retirada)
    logger.info(f"Item devolvido: retirada_id={retirada.id}")
    return retirada