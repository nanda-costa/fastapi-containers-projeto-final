import os
import tempfile
from datetime import date
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TMP_DIR = Path(tempfile.gettempdir())
BOOTSTRAP_DB_PATH = TMP_DIR / "fastapi_containers_test_bootstrap.db"
TEST_DB_PATH = TMP_DIR / "fastapi_containers_test_api.db"

os.environ["DATABASE_URL"] = f"sqlite:///{BOOTSTRAP_DB_PATH}"

from app import models, schemas
from app.main import (
    create_bolsista,
    create_item,
    create_projeto,
    create_retirada,
    delete_bolsista,
    delete_item,
    delete_projeto,
    devolver_item,
    get_bolsista,
    get_item,
    get_projeto,
    get_retirada,
    health_check,
    list_bolsistas,
    list_items,
    list_projetos,
    list_retiradas,
    retiradas_por_bolsista,
    update_bolsista,
    update_item,
    update_projeto,
)


TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def teardown_module() -> None:
    for db_path in (BOOTSTRAP_DB_PATH, TEST_DB_PATH):
        if db_path.exists():
            db_path.unlink()


def criar_projeto(db) -> models.Projeto:
    return create_projeto(
        schemas.ProjetoCreate(
            nome_projeto="PDI Track",
            data_inicio=date(2025, 1, 10),
            data_fim=date(2025, 12, 20),
        ),
        db,
    )


def criar_bolsista(db, cpf: str = "12345678901", name: str = "Ana Souza") -> models.Student:
    return create_bolsista(
        schemas.StudentCreate(
            name=name,
            cpf=cpf,
            data_inicio_lab=date(2025, 2, 1),
            data_fim_lab=date(2025, 12, 1),
        ),
        db,
    )


def criar_item(db, idprojeto: int | None = None, active: bool = True) -> models.Item:
    return create_item(
        schemas.ItemCreate(
            name="Notebook Dell",
            description="Uso em laboratorio",
            active=active,
            idprojeto=idprojeto,
        ),
        db,
    )


def test_health_check(db) -> None:
    response = health_check(db)

    assert response == {"status": "ok", "db": "connected"}


def test_projetos_crud_completo(db) -> None:
    projeto = create_projeto(
        schemas.ProjetoCreate(
            nome_projeto="Laboratorio IA",
            data_inicio=date(2025, 1, 1),
            data_fim=date(2025, 12, 31),
        ),
        db,
    )
    projeto_nome_inicial = projeto.nome_projeto

    projetos = list_projetos(db)
    projeto_encontrado = get_projeto(projeto.id, db)
    projeto_atualizado = update_projeto(
        projeto.id,
        schemas.ProjetoCreate(
            nome_projeto="Laboratorio IA Atualizado",
            data_inicio=date(2025, 1, 15),
            data_fim=date(2025, 11, 30),
        ),
        db,
    )
    delete_projeto(projeto.id, db)

    assert projeto_nome_inicial == "Laboratorio IA"
    assert len(projetos) == 1
    assert projeto_encontrado.id == projeto.id
    assert projeto_atualizado.nome_projeto == "Laboratorio IA Atualizado"

    with pytest.raises(HTTPException) as exc:
        get_projeto(projeto.id, db)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Projeto não encontrado"


def test_items_crud_e_validacao_de_projeto(db) -> None:
    projeto = criar_projeto(db)

    with pytest.raises(HTTPException) as exc:
        create_item(
            schemas.ItemCreate(
                name="Mouse",
                description="Sem projeto valido",
                active=True,
                idprojeto=999,
            ),
            db,
        )
    assert exc.value.status_code == 404
    assert exc.value.detail == "Projeto não encontrado"

    item = create_item(
        schemas.ItemCreate(
            name="Notebook",
            description="Patrimonio do projeto",
            active=True,
            idprojeto=projeto.id,
        ),
        db,
    )
    item_nome_inicial = item.name

    items = list_items(skip=0, limit=10, db=db)
    item_encontrado = get_item(item.id, db)
    item_atualizado = update_item(
        item.id,
        schemas.ItemCreate(
            name="Notebook Atualizado",
            description="Com memoria expandida",
            active=False,
            idprojeto=projeto.id,
        ),
        db,
    )
    delete_item(item.id, db)

    assert item_nome_inicial == "Notebook"
    assert len(items) == 1
    assert item_encontrado.id == item.id
    assert item_atualizado.active is False

    with pytest.raises(HTTPException) as exc:
        get_item(item.id, db)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Item não encontrado"


def test_bolsistas_crud_e_conflito_de_cpf(db) -> None:
    bolsista = create_bolsista(
        schemas.StudentCreate(
            name="Maria Clara",
            cpf="11122233344",
            data_inicio_lab=date(2025, 3, 1),
            data_fim_lab=date(2025, 10, 1),
        ),
        db,
    )
    bolsista_nome_inicial = bolsista.name

    with pytest.raises(HTTPException) as exc_duplicate:
        create_bolsista(
            schemas.StudentCreate(
                name="Outra Pessoa",
                cpf="11122233344",
                data_inicio_lab=date(2025, 4, 1),
                data_fim_lab=date(2025, 11, 1),
            ),
            db,
        )
    assert exc_duplicate.value.status_code == 409
    assert exc_duplicate.value.detail == "CPF já cadastrado"

    bolsistas = list_bolsistas(db)
    bolsista_por_cpf = get_bolsista("11122233344", db)

    segundo_bolsista = criar_bolsista(db, cpf="99988877766", name="Joao Pedro")

    with pytest.raises(HTTPException) as exc_conflito:
        update_bolsista(
            segundo_bolsista.id,
            schemas.StudentCreate(
                name="Joao Pedro",
                cpf="11122233344",
                data_inicio_lab=date(2025, 4, 1),
                data_fim_lab=date(2025, 12, 1),
            ),
            db,
        )
    assert exc_conflito.value.status_code == 409

    bolsista_atualizado = update_bolsista(
        bolsista.id,
        schemas.StudentCreate(
            name="Maria Clara Santos",
            cpf="11122233344",
            data_inicio_lab=date(2025, 3, 5),
            data_fim_lab=date(2025, 12, 20),
        ),
        db,
    )
    delete_bolsista(segundo_bolsista.id, db)

    assert len(bolsistas) == 1
    assert bolsista_nome_inicial == "Maria Clara"
    assert bolsista_por_cpf.cpf == "11122233344"
    assert bolsista_atualizado.name == "Maria Clara Santos"

    with pytest.raises(HTTPException) as exc_missing:
        get_bolsista("99988877766", db)
    assert exc_missing.value.status_code == 404
    assert exc_missing.value.detail == "Bolsista não encontrado"


def test_retiradas_fluxo_completo_e_regras_de_negocio(db) -> None:
    projeto = criar_projeto(db)
    bolsista = criar_bolsista(db, cpf="55566677788", name="Carlos Lima")
    item_ativo = criar_item(db, idprojeto=projeto.id, active=True)
    item_inativo = criar_item(db, idprojeto=projeto.id, active=False)

    with pytest.raises(HTTPException) as exc_item_inativo:
        create_retirada(
            schemas.WithdrawalCreate(item_id=item_inativo.id, cpf=bolsista.cpf),
            db,
        )
    assert exc_item_inativo.value.status_code == 409
    assert exc_item_inativo.value.detail == "Item inativo e não pode ser retirado"

    with pytest.raises(HTTPException) as exc_bolsista_inexistente:
        create_retirada(
            schemas.WithdrawalCreate(item_id=item_ativo.id, cpf="00000000000"),
            db,
        )
    assert exc_bolsista_inexistente.value.status_code == 404
    assert exc_bolsista_inexistente.value.detail == "Bolsista não encontrado para esse CPF"

    retirada = create_retirada(
        schemas.WithdrawalCreate(item_id=item_ativo.id, cpf=bolsista.cpf),
        db,
    )

    with pytest.raises(HTTPException) as exc_retirada_repetida:
        create_retirada(
            schemas.WithdrawalCreate(item_id=item_ativo.id, cpf=bolsista.cpf),
            db,
        )
    assert exc_retirada_repetida.value.status_code == 409
    assert "Item já retirado pelo CPF" in exc_retirada_repetida.value.detail

    retiradas = list_retiradas(apenas_abertas=False, db=db)
    retiradas_abertas = list_retiradas(apenas_abertas=True, db=db)
    retirada_encontrada = get_retirada(retirada.id, db)
    retirada_do_bolsista = retiradas_por_bolsista(bolsista.cpf, db)

    with pytest.raises(HTTPException) as exc_delete_bloqueado:
        delete_bolsista(bolsista.id, db)
    assert exc_delete_bloqueado.value.status_code == 409
    assert (
        exc_delete_bloqueado.value.detail
        == "Bolsista possui retiradas em aberto e não pode ser removido"
    )

    retirada_devolvida = devolver_item(retirada.id, db)

    with pytest.raises(HTTPException) as exc_devolucao_repetida:
        devolver_item(retirada.id, db)
    assert exc_devolucao_repetida.value.status_code == 409
    assert exc_devolucao_repetida.value.detail == "Item já foi devolvido"

    delete_bolsista(bolsista.id, db)

    assert retirada.item_id == item_ativo.id
    assert retirada.student_id == bolsista.id
    assert len(retiradas) == 1
    assert len(retiradas_abertas) == 1
    assert retirada_encontrada.id == retirada.id
    assert len(retirada_do_bolsista) == 1
    assert retirada_devolvida.devolvido_em is not None

    with pytest.raises(HTTPException) as exc_missing:
        get_retirada(999, db)
    assert exc_missing.value.status_code == 404
    assert exc_missing.value.detail == "Retirada não encontrada"
