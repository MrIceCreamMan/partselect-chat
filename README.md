# PartSelect Chat Assistant

AI-powered chat assistant for PartSelect e-commerce platform, specializing in refrigerator and dishwasher parts.

## Features

- 🤖 Intelligent product search with semantic understanding
- 🔧 Troubleshooting assistance for common appliance issues
- ✅ Part compatibility checking
- 📦 Installation guides and instructions
- 💬 Natural conversation with context awareness

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- Deepseek LLM
- Chroma (Vector Database)
- PostgreSQL
- SQLAlchemy

### Frontend
- React 18 + TypeScript
- Tailwind CSS
- Vite

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Deepseek API Key

### Setup

1. Clone the repository
```bash
git clone <your-repo>
cd partselect-chat
```

2. Create environment file
```bash
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY
```

3. Start all services
```bash
docker-compose up --build
```

4. Initialize database and seed data
```bash
docker-compose exec backend python scripts/seed_data.py
```

5. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure
```
partselect-chat/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── postgres/         # Database initialization
└── docker-compose.yml
```

## Example Queries

- "How can I install part number PS11752778?"
- "Is this part compatible with my WDT780SAEM1 model?"
- "The ice maker on my Whirlpool fridge is not working. How can I fix it?"

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Architecture

The system uses an agent-based architecture with specialized tools:
- Product Search Tool (RAG with vector embeddings)
- Compatibility Checker Tool
- Troubleshooting Tool

See `docs/architecture.md` for detailed architecture documentation.

docker-compose exec backend python scripts/seed_data.py