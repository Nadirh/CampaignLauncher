# CampaignLauncher -- Progress

## Current State

Phase 2 complete. The application has a working full-stack CRUD flow for campaigns: PostgreSQL database, SQLAlchemy async models, Alembic migrations, FastAPI CRUD endpoints, Next.js BFF proxy, TanStack Query hooks, and a campaign list/create UI. All tests pass (11 backend, 5 frontend), lint is clean.

## What Has Been Implemented

### Infrastructure
- **Docker Compose**: 3 services -- `db` (PostgreSQL 16-alpine), `backend` (FastAPI), `frontend` (Next.js)
- **Database**: PostgreSQL with health check, named volume (`pgdata`), async connection via `asyncpg`
- **Migrations**: Alembic with sync `psycopg2` driver, runs automatically on container startup
- **Dev mode**: `docker-compose.dev.yml` with hot reload for both frontend and backend

### Backend (FastAPI)
- **Models**: Campaign, AdGroup, Keyword, Ad with SQLAlchemy 2.0 async, UUID PKs, timestamp mixin
- **Enums**: CampaignStatus (draft/review/approved/launched/paused), BiddingStrategy, MatchType
- **Schemas**: Pydantic v2 with `from_attributes` for ORM serialization
- **Endpoints**: Full CRUD at `/api/campaigns` (list, create, get, update, delete) + `/api/health`
- **Database**: Async engine + session via `get_db` dependency, `init_db` connection check at startup
- **Logging**: Structured JSON via python-json-logger
- **Tests**: 11 tests using async SQLite (`aiosqlite`) with httpx `AsyncClient`

### Frontend (Next.js)
- **State**: TanStack Query for server state, Zustand available for client state
- **Provider**: `QueryProvider` wrapping the app in `layout.tsx`
- **Types**: `types/campaign.ts` with full Campaign domain types
- **BFF Routes**: `/api/campaigns` (GET/POST) and `/api/campaigns/[id]` (GET/PUT/DELETE)
- **Hooks**: `useCampaigns()` and `useCreateCampaign()` with cache invalidation
- **Components**: `CampaignList` (table with loading/empty/error states), `CreateCampaignModal` (form overlay)
- **Pages**: `/campaigns` page, home page with link to campaigns
- **Tests**: 5 tests (4 campaign component, 1 home page)
- **API Utility**: `fetchFromApi` handles JSON and 204 responses

### Key Decisions
- SQLite for backend tests (no PostgreSQL needed for pytest)
- Python-side `default=uuid.uuid4` for cross-dialect UUID compatibility
- JSON columns on Ad model for headlines/descriptions (avoids 19 separate columns)
- Alembic uses sync psycopg2 driver while runtime uses async asyncpg
- Dockerfile runs `alembic upgrade head` before starting uvicorn

## What Remains

### Phase 3: Agent Pipeline
- Landing page fetching (Puppeteer MCP)
- Claude API page analysis
- Keyword and ad copy generation
- Google Sheets integration
- Google Ads Script generation

### Phase 4: Review and Approval Workflow
### Phase 5: Production Readiness (Auth, RLS, Rate Limiting, Sentry)

## File Structure (Phase 2 additions)

```
src/backend/
  app/core/database.py          -- async engine, session, get_db, init_db
  app/models/__init__.py        -- re-exports all models
  app/models/base.py            -- Base, TimestampMixin
  app/models/campaign.py        -- Campaign model + enums
  app/models/ad_group.py        -- AdGroup model
  app/models/keyword.py         -- Keyword model + MatchType enum
  app/models/ad.py              -- Ad model with JSON columns
  app/schemas/common.py         -- ErrorDetail, ErrorResponse
  app/schemas/campaign.py       -- Campaign CRUD schemas
  app/routers/campaigns.py      -- Campaign CRUD endpoints
  alembic.ini                   -- Alembic config
  alembic/env.py                -- Migration env with async-to-sync URL translation
  alembic/versions/             -- Migration files

src/frontend/
  providers/query-provider.tsx   -- QueryClientProvider wrapper
  types/campaign.ts              -- Campaign TypeScript types
  hooks/use-campaigns.ts         -- TanStack Query hooks
  components/campaign-list.tsx   -- Campaign table component
  components/create-campaign-modal.tsx  -- Create form modal
  app/campaigns/page.tsx         -- Campaigns page
  app/api/campaigns/route.ts     -- BFF GET/POST
  app/api/campaigns/[id]/route.ts -- BFF GET/PUT/DELETE

tests/
  backend/test_campaigns.py      -- 9 campaign CRUD tests
  frontend/campaigns.test.tsx    -- 4 campaign UI tests
```
