# Progress

## Current State

Phase 1 (Full-Stack Scaffolding) is complete. The project has a running full-stack foundation with Next.js frontend and FastAPI backend communicating through the BFF pattern, orchestrated by Docker Compose.

## What Has Been Done

### Phase 1: Full-Stack Scaffolding (Complete)

- **Backend (FastAPI)**: Health endpoint at GET /api/health, structured JSON logging via python-json-logger, CORS middleware, Pydantic Settings config, lifespan event handler
- **Frontend (Next.js 15)**: App Router with TypeScript, Tailwind CSS v4, Pino logger, ESLint + Prettier
- **BFF Pattern**: fetchFromApi utility in lib/api.ts, /api/health route handler proxies to backend, home page server component displays backend status
- **Docker**: Backend and frontend Dockerfiles with non-root users, Docker Compose with production and dev override configs
- **Tests**: Backend pytest (2 tests), Frontend vitest (1 test), all passing
- **Scripts**: dev-start.sh, dev-stop.sh, test-backend.sh, test-frontend.sh, lint.sh

## Key Decisions

- **Tailwind CSS v4** with @tailwindcss/postcss plugin (not v3 config-based approach)
- **Node_modules symlink** at project root points to src/frontend/node_modules -- needed for Vite to resolve imports in test files under tests/frontend/
- **Direct venv binary** in backend Dockerfile CMD (not uv run) to avoid cache permission issues with non-root user
- **force-dynamic** on home page to prevent static pre-rendering (backend not available at build time)
- **Lifespan context manager** for FastAPI startup events (not deprecated on_event)

## Architecture

```
Browser -> localhost:3000 (Next.js) -> BFF route handlers -> localhost:8000 (FastAPI)
```

Frontend never calls backend directly from the browser. All API calls go through Next.js /app/api/ route handlers.

## What Remains

- Phase 2+: Agent pipeline, landing page analysis, keyword/ad generation
- Supabase integration (auth, database, RLS)
- Google Sheets MCP integration
- Google Ads Script generation
- Sentry error tracking (DSN fields exist in config, SDK not installed yet)
