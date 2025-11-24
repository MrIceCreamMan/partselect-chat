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
- Docker

### Frontend
- React 18 + JavaScript
- Plain CSS
- Docker

### Communication:
- API: REST
- Streaming: Server-Sent Events (SSE)
- Format: JSON

### Infrastructure:
- Orchestration: Docker Compose

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Deepseek API Key

### Setup

1. Clone the repository
```bash
git clone https://github.com/MrIceCreamMan/partselect-chat.git
cd partselect-chat
```

2. Create environment file
```bash
cp .env.example .env
vi .env
# Edit .env and add your DEEPSEEK_API_KEY
```

3. Start all services
```bash
docker-compose up --build -d
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
├── docker-compose.yml
├── README.md
├── .env
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                          # FastAPI entry point
│   ├── config.py                        # Configuration
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py             # Chat endpoints
│   │   │   │   └── health.py           # Health check
│   │   │   └── dependencies.py          # FastAPI dependencies
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py         # Main agent orchestrator
│   │   │   ├── deepseek_client.py      # Deepseek API wrapper
│   │   │   └── prompts.py              # System prompts
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py              # Pydantic models
│   │   │   └── database_models.py      # SQLAlchemy models
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py         # Chroma integration
│   │   │   ├── database.py             # PostgreSQL connection
│   │   │
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Base tool class
│   │   │   ├── product_search.py       # Product search tool
│   │   │   ├── compatibility.py        # Compatibility checker
│   │   │   └── troubleshooting.py      # Troubleshooting tool
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── guards.py               # Guard rails
│   │       └── helpers.py              # Utility functions
│   │
│   ├── data/
│   │   ├── products.json               # Product catalog
│   │   ├── compatibility.json          # Compatibility matrix
│   │   ├── troubleshooting/
│   │   │   ├── fridge_icemaker.txt
│   │   │   ├── dishwasher_not_cleaning.txt
│   │   │   └── dishwasher_not_draining.txt
│   │
│   ├── scripts/
│   │   ├── seed_data.py                # Seed initial data
│   │   └── check_data_summary.py       # Check database summary
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   │
│   ├── public/
│   │   └── partselect-logo.svg
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── vite-env.d.ts
│       │
│       ├── components/
│       │   ├── Chat/
│       │   │   ├── ChatContainer.tsx
│       │   │   ├── ChatMessage.tsx
│       │   │   ├── ChatInput.tsx
│       │   │   └── TypingIndicator.tsx
│       │   │
│       │   ├── Messages/
│       │   │   ├── ProductCard.tsx
│       │   │   ├── CompatibilityBadge.tsx
│       │   │   ├── InstallationSteps.tsx
│       │   │   └── TroubleshootingCard.tsx
│       │   │
│       │   └── ui/                     # shadcn components
│       │       ├── button.tsx
│       │       ├── card.tsx
│       │       └── ...
│       │
│       ├── hooks/
│       │   ├── useChat.ts
│       │   └── useStreamingResponse.ts
│       │
│       ├── services/
│       │   └── api.ts                  # API client
│       │
│       ├── store/
│       │   └── chatStore.ts            # Zustand store
│       │
│       ├── types/
│       │   └── index.ts                # TypeScript types
│       │
│       └── styles/
│           └── globals.css
│
└── postgres/
    └── init.sql                        # Database initialization
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

### Docker commands

```
// nuke/delete all
docker compose down --volumes --remove-orphans
docker system prune -a --volumes

// stop
docker compose down

// start
docker compose up --build -d
```
