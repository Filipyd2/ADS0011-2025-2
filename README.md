# Projeto Final — Banco de Dados ORM

Sistema de biblioteca de jogos usando **Python + SQLAlchemy** conectado ao **PostgreSQL**.

Aluno: Luiz Filipy Soares da Silva
Matricula: 2025013503
---

## Estrutura dos arquivos

```
.
├── .env                  # Variáveis de ambiente (credenciais do banco)
├── requirements.txt      # Dependências Python
├── database.py           # Configuração da engine e sessão SQLAlchemy
├── models.py             # Mapeamento ORM (classes ↔ tabelas)
├── crud.py               # Operações CRUD via ORM
├── queries.py            # Consultas com relacionamento (JOIN)
├── main.py               # Ponto de entrada — demonstra todas as operações
├── Evidencias\           # Pasta com prints com evidencias de execução do projeto
└── Scripts\              # Arquivos .sql do projeto
```

---

## Pré-requisitos

- Python 3.11+
- PostgreSQL com o banco já criado (executar os scripts `.sql`)

---

## Como configurar

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variáveis de ambiente** no arquivo `.env`:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=sua_senha
   DB_NAME=nome_do_banco
   ```

3. **Criar o banco** executando os scripts SQL no PostgreSQL:
   ```bash
   psql -U postgres -d nome_do_banco -f ProjetoFinal_Etapa4.sql
   psql -U postgres -d nome_do_banco -f ProjetoFinal_Etapa5.sql
   ```

---

## Como executar

```bash
python main.py
```

---
