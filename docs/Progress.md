# CampaignLauncher -- Progress

## Current State

Phase 3 (Core Agent Pipeline) complete. The application can now generate ad groups, keywords, and RSA ads from a landing page URL using Claude. The pipeline fetches the page, analyzes it with Claude, saves the results to the database, and transitions the campaign to review status. All tests pass (57 backend, 7 frontend), lint is clean.

## What Has Been Implemented

### Infrastructure
- **Docker Compose**: 3 services -- `db` (PostgreSQL 16-alpine), `backend` (FastAPI), `frontend` (Next.js)
- **Database**: PostgreSQL with health check, named volume (`pgdata`), async connection via `asyncpg`
- **Migrations**: Alembic with sync `psycopg2` driver, runs automatically on container startup
- **Dev mode**: `docker-compose.dev.yml` with hot reload for both frontend and backend
- **ANTHROPIC_API_KEY**: Configured in Settings, Docker Compose, and .env.example

### Backend (FastAPI)
- **Models**: Campaign, AdGroup, Keyword, Ad with SQLAlchemy 2.0 async, UUID PKs, timestamp mixin
- **Enums**: CampaignStatus (draft/review/approved/launched/paused), BiddingStrategy, MatchType
- **Schemas**: Pydantic v2 for campaign CRUD and pipeline (PageContent, CampaignStructure, GenerateResponse)
- **Endpoints**: Full CRUD at `/api/campaigns` + `/api/campaigns/{id}/generate` + `/api/health`
- **Database**: Async engine + session via `get_db` dependency, `init_db` connection check at startup
- **Logging**: Structured JSON via python-json-logger

#### Agent Pipeline Services
- **PageFetcher** (`app/services/page_fetcher.py`): httpx + BeautifulSoup, extracts title, meta desc, headings, hero text, CTAs, features, raw text. URL validation with SSRF protection (blocks private IPs, loopback, reserved ranges)
- **ClaudeAnalyzer** (`app/services/claude_analyzer.py`): Loads system prompt from `docs/SystemPrompt.md`, builds structured user message from PageContent, calls Claude via Anthropic SDK, parses JSON response (handles markdown code fences)
- **CampaignSaver** (`app/services/campaign_saver.py`): Saves CampaignStructure to DB -- creates AdGroup, Keyword, Ad records atomically, transitions campaign to REVIEW status
- **PipelineOrchestrator** (`app/services/pipeline.py`): Chains fetch -> analyze -> save with per-step timing and error logging. PipelineError includes step identification
- **PipelineRouter** (`app/routers/pipeline.py`): POST endpoint, maps PipelineError.step to HTTP status codes (400 for validation, 502 for fetch/analyze, 500 for save)

- **Tests**: 57 tests using async SQLite (`aiosqlite`) with httpx `AsyncClient`

### Frontend (Next.js)
- **State**: TanStack Query for server state, Zustand available for client state
- **Provider**: `QueryProvider` wrapping the app in `layout.tsx`
- **Types**: `types/campaign.ts` with Campaign, GenerateResponse, AdGroupResponse, KeywordResponse, AdResponse
- **BFF Routes**: `/api/campaigns` (GET/POST), `/api/campaigns/[id]` (GET/PUT/DELETE), `/api/campaigns/[id]/generate` (POST)
- **Hooks**: `useCampaigns()`, `useCreateCampaign()`, `useGenerateCampaign()` with cache invalidation
- **Components**: `CampaignList` (table with Generate button for draft campaigns, loading/error states), `CreateCampaignModal`
- **Pages**: `/campaigns` page, home page with link to campaigns
- **Tests**: 7 tests (6 campaign component including Generate button visibility, 1 home page)
- **API Utility**: `fetchFromApi` handles JSON and 204 responses

### Key Decisions
- SQLite for backend tests (no PostgreSQL needed for pytest)
- Python-side `default=uuid.uuid4` for cross-dialect UUID compatibility
- `sqlalchemy.JSON` (not `postgresql.JSON`) for Ad headlines/descriptions -- dialect-agnostic for SQLite tests
- Alembic uses sync psycopg2 driver while runtime uses async asyncpg
- Dockerfile runs `alembic upgrade head` before starting uvicorn
- httpx + BeautifulSoup for page fetching (simple, no browser dep; Playwright can be added later)
- Synchronous pipeline (POST blocks until complete) -- simplest for Phase 3
- Claude model: claude-sonnet-4-20250514 for cost/speed balance
- System prompt loaded from `docs/SystemPrompt.md` at runtime (path resolved by walking up directory tree, with SYSTEM_PROMPT_PATH config override)
- Docker Compose uses `--env-file .env.local` for secrets, `docs/` mounted as read-only volume into backend container
- E2E verified: anthropic.com generated 4 ad groups with proper keyword/headline/description structure

## What Remains

### Phase 3b: Agent Pipeline Extensions
- Google Sheets integration via MCP
- Google Ads Script generation

### Phase 4: Review and Approval Workflow
### Phase 5: Production Readiness (Auth, RLS, Rate Limiting, Sentry)

## File Structure (Phase 3 additions)

```
src/backend/
  app/services/__init__.py            -- empty package init
  app/services/page_fetcher.py        -- URL validation, httpx fetch, BS4 parsing
  app/services/claude_analyzer.py     -- Anthropic SDK, system prompt, JSON parsing
  app/services/campaign_saver.py      -- DB writes, status transition
  app/services/pipeline.py            -- orchestrator chaining 3 steps
  app/routers/pipeline.py             -- POST /api/campaigns/{id}/generate
  app/schemas/pipeline.py             -- PageContent, CampaignStructure, response schemas

src/frontend/
  app/api/campaigns/[id]/generate/route.ts  -- BFF proxy POST
  types/campaign.ts                   -- added GenerateResponse, AdGroupResponse, etc.
  hooks/use-campaigns.ts              -- added useGenerateCampaign
  components/campaign-list.tsx        -- added Generate button for draft campaigns

tests/
  backend/test_page_fetcher.py        -- 19 tests
  backend/test_claude_analyzer.py     -- 16 tests
  backend/test_campaign_saver.py      -- 6 tests
  backend/test_pipeline.py            -- 5 integration tests
  frontend/campaigns.test.tsx         -- 6 tests (2 new for Generate button)
```
