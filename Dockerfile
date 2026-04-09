# ── Estágio único — imagem oficial Python slim ──────────────────────────────
FROM python:3.12-slim

# Metadados
LABEL maintainer="Fundamentos de Containers"
LABEL description="API FastAPI + PostgreSQL — Projeto Final Aula 08"

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# psycopg2-binary já inclui os binários do libpq — nenhuma dep de sistema necessária

# Copia e instala dependências Python primeiro (cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Cria usuário não-root ──────────────────────────────────────────────────────
RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --no-create-home appuser

# Copia o código da aplicação
COPY app/ ./app/

# Ajusta permissões
RUN chown -R appuser:appgroup /app

# Troca para usuário não-root
USER appuser

# Expõe a porta
EXPOSE 8000

# Healthcheck interno do container
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]