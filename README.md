<h1 align="center">📑 Gestor PD&I Track</h1>

<p align="center">
  <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExc3VlaWwzcGs2dWhzZmo4bTk3YXpzemNvOWpidTlweXQ5bW93aTY4aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/aBNx9CPiYX5NdsJvS6/giphy.gif" width="260">
</p>

<p align="center">
  Sistema web para apoio à administração de projetos de <strong>Pesquisa, Desenvolvimento e Inovação (PD&amp;I)</strong>,<br>
  com foco no <strong>controle de itens recebidos e adquiridos</strong>, facilitando a organização, o acompanhamento e a futura prestação de contas.<br>
</p>



<h2 align="center">🤖 Tecnologias Utilizadas</h2>

<p align="center">
  <a href="https://www.python.org"><img alt="Python" src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python"></a>
  <a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi"></a>
  <a href="https://www.postgresql.org/"><img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql"></a>
  <a href="https://www.sqlalchemy.org/"><img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge"></a>
  <a href="https://www.docker.com/"><img alt="Docker" src="https://img.shields.io/badge/Docker-Containerizado-2496ED?style=for-the-badge&logo=docker"></a>
  <a href="https://docs.docker.com/compose/"><img alt="Docker Compose" src="https://img.shields.io/badge/Docker_Compose-Orquestra%C3%A7%C3%A3o-1D63ED?style=for-the-badge&logo=docker"></a>
</p>

---

<h2 align="center">📝 Descrição do Projeto</h2>

O <strong>Gestor PD&amp;I Track</strong> é uma aplicação backend desenvolvida para apoiar a gestão administrativa de projetos de PD&amp;I, oferecendo uma base simples e funcional para o controle de itens relacionados ao projeto.

A proposta do sistema é centralizar o cadastro e a consulta de materiais, equipamentos, insumos ou demais itens vinculados às atividades do projeto, permitindo que essas informações permaneçam organizadas ao longo da execução. Dessa forma, a solução contribui para o acompanhamento interno e também para processos de conferência e prestação de contas ao final do projeto.

Nesta versão, o sistema implementa uma <strong>API REST</strong> com operações de cadastro, listagem, busca, atualização e remoção de itens, utilizando <strong>FastAPI</strong>, <strong>PostgreSQL</strong> e execução containerizada com <strong>Docker Compose</strong>.

---

<h2 align="center">🎯 Objetivo do Projeto</h2>

- Oferecer uma base digital para o controle de itens recebidos ou comprados em projetos de PD&amp;I;
- Facilitar a organização administrativa das informações relacionadas aos itens do projeto;
- Apoiar o acompanhamento de registros que podem ser úteis em etapas de conferência e prestação de contas;
- Demonstrar uma solução backend containerizada, simples de executar e manter;
- Disponibilizar uma API pronta para futura expansão com novas regras de negócio.

---

<h2 align="center">🧩 Contexto de Uso</h2>

Em projetos de pesquisa e desenvolvimento, é comum haver o recebimento ou a aquisição de diferentes itens ao longo da execução, como materiais de consumo, equipamentos, acessórios ou recursos de apoio. Quando essas informações ficam descentralizadas, o acompanhamento administrativo se torna mais difícil, especialmente em momentos de auditoria, encerramento do projeto ou prestação de contas.

O <strong>Gestor PD&amp;I Track</strong> surge como uma proposta de sistema para organizar esse controle de forma estruturada. Embora esta versão seja enxuta, ela já estabelece a base necessária para registrar itens e manter um histórico operacional mínimo no banco de dados, servindo como ponto de partida para evoluções futuras.

---

<h2 align="center">⚙️ Funcionalidades Disponíveis</h2>

| Funcionalidade | Descrição |
| --- | --- |
| Health check | Verifica se a API e o banco estão disponíveis |
| Cadastro de itens | Registra um novo item no sistema |
| Listagem de itens | Retorna os itens cadastrados |
| Consulta por ID | Busca um item específico |
| Atualização de item | Altera os dados de um item existente |
| Remoção de item | Exclui um item do sistema |

---

<h2 align="center">🗃️ Estrutura Básica dos Dados</h2>

Atualmente, o sistema pode ser estruturado com três entidades principais: <code>Projeto</code>, <code>Bolsista</code> e <code>Item</code>. A tabela <code>Item</code> passa a se relacionar com a tabela <code>Projeto</code> por meio do campo <code>codprojeto</code>, que atua como chave estrangeira.

### Tabela <code>projeto</code>

| Campo | Tipo | Descrição |
| --- | --- | --- |
| <code>id</code> | inteiro | Identificador do projeto |
| <code>nome_projeto</code> | texto | Nome do projeto |
| <code>data_inicio</code> | data | Data de início do projeto |
| <code>data_fim</code> | data | Data de encerramento do projeto |

### Tabela <code>bolsista</code>

| Campo | Tipo | Descrição |
| --- | --- | --- |
| <code>id</code> | inteiro | Identificador do bolsista |
| <code>nome</code> | texto | Nome completo do bolsista |
| <code>cpf</code> | texto | CPF do bolsista |
| <code>data_inicio_lab</code> | data | Data de início da atuação no laboratório |
| <code>data_fim_lab</code> | data | Data de fim da atuação no laboratório |

### Tabela <code>item</code>

| Campo | Tipo | Descrição |
| --- | --- | --- |
| <code>id</code> | inteiro | Identificador do item |
| <code>name</code> | texto | Nome do item |
| <code>description</code> | texto | Descrição complementar |
| <code>active</code> | booleano | Indica se o item está ativo |
| <code>created_at</code> | data/hora | Data de criação do registro |
| <code>updated_at</code> | data/hora | Data da última atualização |
| <code>idprojeto</code> | inteiro | Identificador do projeto ao qual o item está vinculado (chave estrangeira para <code>projeto.id</code>) |
| <code>idbolsista</code> | inteiro | Identificador do bolsista ao qual o item está vinculado (chave estrangeira para <code>bolsista.id</code>) |

---
<h2 align="center">📁 Estrutura do Projeto</h2>

```bash
📦 fastapi-containers-projeto-final
├── 📄 .dockerignore
├── 📄 .env.example
├── 📄 .gitignore
├── 📄 Dockerfile
├── 📄 README.md
├── 📄 docker-compose.yml
├── 📄 docker-backup.sh
├── 📄 requirements.txt
└── 📁 app/
    ├── 📄 __init__.py
    ├── 📄 database.py      # conexão com o PostgreSQL
    ├── 📄 main.py          # rotas, health check e CRUD de itens
    ├── 📄 models.py        # modelo ORM da tabela items
    └── 📄 schemas.py       # schemas de entrada e saída da API
```

---

<h2 align="center">🔌 Endpoints da API</h2>

| Método | Rota | Descrição |
| --- | --- | --- |
| <code>GET</code> | <code>/health</code> | Verifica a saúde da API e do banco |
| <code>POST</code> | <code>/items</code> | Cria um item |
| <code>GET</code> | <code>/items</code> | Lista os itens |
| <code>GET</code> | <code>/items/{id}</code> | Busca um item por ID |
| <code>PUT</code> | <code>/items/{id}</code> | Atualiza um item |
| <code>DELETE</code> | <code>/items/{id}</code> | Remove um item |

---

<h2 align="center">🚀 Como Utilizar</h2>

### 1. Clonar o repositório

```bash
git clone https://github.com/nanda-costa/gestor-pdi-track.git
cd gestor-pdi-track
```

### 2. Criar o arquivo de ambiente

```bash
cp .env.example .env
```

Se desejar, ajuste no arquivo <code>.env</code> os valores de usuário, senha e nome do banco.

### 3. Subir os containers

```bash
docker compose up -d --build
```

### 4. Verificar se os serviços estão em execução

```bash
docker compose ps
```

### 5. Acessar a aplicação

A API ficará disponível em:

```bash
http://localhost:8001
```

A documentação interativa poderá ser acessada em:

```bash
http://localhost:8001/docs
```

O health check poderá ser testado em:

```bash
http://localhost:8001/health
```

---

<h2 align="center">🧪 Exemplos de Uso</h2>

### Criar um item

```bash
curl -X POST http://localhost:8001/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Notebook",
    "description": "Notebook destinado às atividades do projeto",
    "active": true,
    "idprojeto": 1,
    "idbolsista": 1
  }'
```

### Listar itens

```bash
curl http://localhost:8001/items
```

### Buscar status da aplicação

```bash
curl http://localhost:8001/health
```

---

<h2 align="center">💾 Backup e Restauração</h2>

O projeto também possui um script auxiliar para backup e restauração do banco de dados.

```bash
chmod +x docker-backup.sh
```

### Fazer backup

```bash
./docker-backup.sh backup
```

### Listar backups

```bash
./docker-backup.sh list
```

### Restaurar o backup mais recente

```bash
./docker-backup.sh restore
```

---

<h2 align="center">✅ Boas Práticas Implementadas</h2>

- Uso de imagem oficial e enxuta do Python;
- Execução da aplicação com usuário não root;
- Separação de variáveis sensíveis em arquivo <code>.env</code>;
- Persistência dos dados do PostgreSQL com volume nomeado;
- Health check do banco de dados;
- Inicialização ordenada dos serviços com <code>depends_on</code>;
- Estrutura simples e organizada para evolução futura.

---

<h2 align="center">👥 Equipe</h2>

| Integrante | GitHub |
| --- | --- |
| Juliana Ballin Lima | [JulianaBallin](https://github.com/JulianaBallin) |
| Camila Félix dos Reis | [cawzkf](https://github.com/cawzkf) |
| Pedro Dias | [pedroddias-oss](https://github.com/pedroddias-oss) |
| Fernanda Costa | [nanda-costa](https://github.com/nanda-costa) |

---
<h2 align="center">📌 Considerações Finais</h2>

O <strong>PD&amp;I Track</strong> foi pensado como uma base inicial para um sistema de apoio à gestão administrativa de projetos de PD&amp;I, especialmente no controle de itens que precisam ser registrados, acompanhados e posteriormente conferidos. A estrutura atual é simples, mas já demonstra uma organização técnica consistente e pronta para evolução.

---

<p align="center">
  Desenvolvido como projeto final da disciplina <strong>Fundamentos de Docker</strong>, ministrada pelo <strong>Professor Fabio Santos da Silva</strong> no ano de 2026.
</p>
