# 📋 Gabarito Reader

Sistema de leitura e correção automática de gabaritos via foto.

## Tecnologias

- **Backend:** Python 3.11 + FastAPI
- **Banco de dados:** SQLite (dev) / PostgreSQL (prod)
- **Visão computacional:** OpenCV + NumPy
- **Frontend:** React + Vite + Tailwind CSS

## Como executar (desenvolvimento)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Estrutura do projeto

```
gabarito-reader/
├── backend/    # API Python
└── frontend/   # Interface React
```