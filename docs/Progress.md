# CampaignLauncher -- Progress

## Current State

Phase 4b (Campaign Settings + Pin Positions & Behavioral Triggers) complete. The create modal now collects 6 campaign settings -- all required except negative keywords (Google Ads needs them). Settings are threaded to Claude and included in the user message. Claude returns behavioral trigger labels (from the 7-item Behavioral Toolbox in SystemPrompt.md) on every headline and description. Pin positions and triggers are displayed on the detail page. The Excel Ads sheet outputs one row per headline/description with separate columns for Type, #, Copy, Pin Position, Trigger, and Length -- keeping copy text clean for business user review. All changes are backwards compatible. All tests pass (91 backend, 24 frontend), lint is clean.

## What Has Been Implemented

### Infrastructure
- **Docker Compose**: 3 services -- `db` (PostgreSQL 16-alpine), `backend` (FastAPI), `frontend` (Next.js)
- **Database**: PostgreSQL with health check, named volume (`pgdata`), async connection via `asyncpg`
- **Migrations**: Alembic with sync `psycopg2` driver, runs automatically on container startup
- **Dev mode**: `docker-compose.dev.yml` with hot reload for both frontend and backend
- **ANTHROPIC_API_KEY**: Configured in Settings, Docker Compose, and .env.example

### Backend (FastAPI)
- **Models**: Campaign (with settings: match_types, negative_keywords, bid_value, location_targeting), AdGroup, Keyword, Ad with SQLAlchemy 2.0 async, UUID PKs, timestamp mixin
- **Enums**: CampaignStatus (draft/review/approved/launched/paused), BiddingStrategy (default: TARGET_CPA), MatchType
- **Schemas**: Pydantic v2 for campaign CRUD and pipeline (PageContent, CampaignStructure with trigger fields, GenerateResponse with settings)
- **Endpoints**: Full CRUD at `/api/campaigns` + `/api/campaigns/{id}/generate` + `/api/campaigns/{id}/approve` + `/api/campaigns/{id}/reject` + `/api/campaigns/{id}/export` + `/api/health`
- **Database**: Async engine + session via `get_db` dependency, `init_db` connection check at startup
- **Logging**: Structured JSON via python-json-logger

#### Agent Pipeline Services
- **PageFetcher** (`app/services/page_fetcher.py`): httpx + BeautifulSoup, extracts title, meta desc, headings, hero text, CTAs, features, raw text. URL validation with SSRF protection (blocks private IPs, loopback, reserved ranges)
- **ClaudeAnalyzer** (`app/services/claude_analyzer.py`): Loads system prompt from `docs/SystemPrompt.md`, builds structured user message from PageContent with campaign settings (match types, bidding strategy, bid value, daily budget, location targeting, negative keywords), requests behavioral trigger labels on headlines/descriptions, calls Claude via Anthropic SDK, parses JSON response (handles markdown code fences)
- **CampaignSaver** (`app/services/campaign_saver.py`): Saves CampaignStructure to DB -- creates AdGroup, Keyword, Ad records atomically, transitions campaign to REVIEW status
- **PipelineOrchestrator** (`app/services/pipeline.py`): Chains fetch -> analyze -> save with per-step timing and error logging. PipelineError includes step identification
- **PipelineRouter** (`app/routers/pipeline.py`): POST endpoint, maps PipelineError.step to HTTP status codes (400 for validation, 502 for fetch/analyze, 500 for save)

#### Excel Export
- **ExcelExport** (`app/services/excel_export.py`): Generates .xlsx workbook in-memory via openpyxl with 3 tabs: Summary (campaign settings), Keywords (denormalized), Ads (one row per headline/description with columns: Ad Group, Ad #, Type, #, Copy, Pin Position, Trigger, Length, Final URL, Path). Takes Pydantic model, not ORM objects. Bold headers with gray fill
- **ExportRouter** (`app/routers/export.py`): GET endpoint, loads campaign with selectinload, streams binary response with Content-Disposition

- **Tests**: 91 tests using async SQLite (`aiosqlite`) with httpx `AsyncClient`

### Frontend (Next.js)
- **State**: TanStack Query for server state, Zustand available for client state
- **Provider**: `QueryProvider` wrapping the app in `layout.tsx`
- **Types**: `types/campaign.ts` with Campaign, GenerateResponse, AdGroupResponse, KeywordResponse, AdResponse
- **BFF Routes**: `/api/campaigns` (GET/POST), `/api/campaigns/[id]` (GET/PUT/DELETE), `/api/campaigns/[id]/generate` (POST), `/api/campaigns/[id]/approve` (POST), `/api/campaigns/[id]/reject` (POST), `/api/campaigns/[id]/export` (GET, binary passthrough)
- **Hooks**: `useCampaigns()`, `useCreateCampaign()`, `useGenerateCampaign()`, `useCampaignDetail(id)`, `useApproveCampaign()`, `useRejectCampaign()` with cache invalidation
- **Components**: `CampaignList` (table with clickable name links, Generate button for draft campaigns), `CreateCampaignModal` (6 campaign settings fields with defaults), `ConfirmModal` (reusable)
- **Pages**: `/campaigns` list page, `/campaigns/[id]` detail page (collapsible ad groups, keywords with match type badges, ads with pin position badges and trigger labels, campaign settings display, approve/reject, Download Excel), home page with link to campaigns
- **Tests**: 24 tests (7 campaign list, 11 campaign detail, 5 confirm modal, 1 home page)
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
- Excel export replaces Google Sheets MCP -- openpyxl generates workbooks in-memory, no external API dependencies

## What Remains

### Phase 3c: Google Ads Script Generation

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
  frontend/campaigns.test.tsx         -- 7 tests (link test added in Phase 4)
  frontend/campaign-detail.test.tsx   -- 8 tests (Phase 4 + Phase 3b)
  frontend/confirm-modal.test.tsx     -- 5 tests (Phase 4)
```

## Phase 3b additions

```
src/backend/
  app/services/excel_export.py         -- workbook generation (Summary, Keywords, Ads tabs)
  app/routers/export.py                -- GET /api/campaigns/{id}/export endpoint

src/frontend/
  app/api/campaigns/[id]/export/route.ts  -- BFF binary proxy GET
  app/campaigns/[id]/page.tsx             -- added Download Excel button

tests/
  backend/test_excel_export.py         -- 14 unit tests
  backend/test_export_endpoint.py      -- 4 integration tests
```

## Phase 4 additions

```
src/backend/
  app/routers/campaigns.py             -- enhanced GET with selectinload, added approve/reject

src/frontend/
  app/api/campaigns/[id]/approve/route.ts  -- BFF proxy POST
  app/api/campaigns/[id]/reject/route.ts   -- BFF proxy POST
  app/campaigns/[id]/page.tsx              -- campaign detail page
  components/confirm-modal.tsx             -- reusable confirmation modal
  components/campaign-list.tsx             -- campaign names as links
  hooks/use-campaigns.ts                   -- added useCampaignDetail, useApproveCampaign, useRejectCampaign
```

## Phase 4b additions (Campaign Settings + Triggers)

```
src/backend/
  app/models/campaign.py                -- 4 new columns (match_types, negative_keywords, bid_value, location_targeting), default changed to TARGET_CPA
  app/schemas/campaign.py               -- settings in CampaignCreate/Update/Response
  app/schemas/pipeline.py               -- trigger field on HeadlineData/DescriptionData, settings in CampaignGenerateResponse
  app/services/claude_analyzer.py       -- campaign settings in user message, trigger field in JSON schema
  app/services/campaign_saver.py        -- persists trigger field from headlines/descriptions
  app/services/pipeline.py              -- threads campaign settings to analyzer
  app/services/excel_export.py          -- settings in Summary sheet, pin/trigger in Ads sheet
  app/routers/campaigns.py              -- passes new fields in create
  alembic/versions/a2b3c4d5e6f7_*.py   -- migration adding 4 new columns

src/frontend/
  types/campaign.ts                     -- 4 new fields on Campaign/GenerateResponse, trigger on Ad types
  components/create-campaign-modal.tsx   -- 6 settings fields (match types checkboxes, bidding strategy, bid value, daily budget, negative keywords, location targeting)
  app/campaigns/[id]/page.tsx           -- pin position badges, trigger labels, campaign settings display

tests/
  backend/test_campaigns.py             -- 2 new settings round-trip tests
  backend/test_claude_analyzer.py       -- 6 new tests for triggers/settings/match types
  backend/test_excel_export.py          -- updated fixtures + 2 new backwards-compat tests
  frontend/campaign-detail.test.tsx     -- 3 new tests (pin/trigger display, settings display)
```
