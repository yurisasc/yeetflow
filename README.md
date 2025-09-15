# YeetFlow

Democratize web automation by enabling anyone to execute complex, multi-step workflows with AI assistance through a simple web interface.

## Key Features

### Human-in-the-Loop Automation
- **Interactive Sessions**: Users can perform manual steps (login, navigation, data entry) at any point during automation
- **AI Takeover**: Smart AI agents handle automated tasks, with seamless transitions between human and AI control
- **No Credential Storage**: User credentials are never stored or shared

### Web Portal & Flow Library
- **Dashboard**: Web interface for managing automation Flows
- **Flow Library**: Browse and run authorized automations
- **Real-time Updates**: Live progress tracking with visual browser automation

### Results & Monitoring
- **Download Results**: Easy access to completed automation outputs
- **Status Tracking**: Real-time progress updates and notifications

## Architecture

YeetFlow is built as a monorepo with three main components:

```
┌─────────────────┐    API    ┌─────────────────┐    API    ┌─────────────────┐
│   Next.js Web   │◄─────────►│  Python Worker  │◄─────────►│   Steel.dev     │
│   Dashboard     │           │   (FastAPI)     │           │  Cloud Browser  │
│                 │  Socket.IO│                 │           │                 │
│   TypeScript    │◄─────────►│   browser-use   │           │   Sessions      │
└─────────────────┘           └─────────────────┘           └─────────────────┘
```

### Components

- **Frontend**: Next.js application with better-auth for user management
- **Backend**: Python FastAPI worker orchestrating automation tasks
- **Browser Service**: Steel.dev provides secure, isolated cloud browser sessions
- **AI Agent**: browser-use framework for intelligent automation

## Prerequisites

- **Node.js 20 LTS**
- **pnpm >= 9**
- **Python 3.11**
- **Docker** (optional, for containerizing the worker)
- **Steel.dev API access** (for browser sessions)

## Quick Start

### 1. Repository Setup

```bash
# Clone the repository
git clone https://github.com/yurisasc/yeetflow.git
cd yeetflow

# Install dependencies
pnpm install
```

### 2. Environment Configuration

#### Web App (apps/web/.env.local)
```bash
AUTH_SECRET=your_auth_secret_here
DATABASE_URL=your_database_url_here
WORKER_BASE_URL=http://localhost:8000
WORKER_API_TOKEN=your_worker_api_token_here
```

#### Worker (apps/worker/.env)
```bash
STEEL_API_KEY=your_steel_api_key
API_TOKEN=dev-token
ARTIFACTS_DIR=./artifacts
```

### 3. Development Setup

```bash
# Terminal 1 - Start the worker
cd apps/worker
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Start the web app
pnpm --filter web dev
```

Visit `http://localhost:3000` to access the YeetFlow dashboard.

## Development

### Project Structure

```
yeetflow/
├── apps/
│   ├── web/          # Next.js frontend
│   └── worker/       # Python FastAPI backend
└── pnpm-workspace.yaml
```

**YeetFlow** - Empowering users with AI-assisted web automation, one Flow at a time.
