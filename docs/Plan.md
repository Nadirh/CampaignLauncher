# CampaignLauncher -- Development Plan

## Phase 1: Full-Stack Scaffolding (Completed)

- [x] Next.js frontend with TypeScript and Tailwind CSS
- [x] FastAPI backend with structured JSON logging
- [x] Docker Compose with separate containers for frontend and backend
- [x] BFF pattern: frontend API routes proxy to FastAPI
- [x] Health check endpoint end-to-end
- [x] Vitest for frontend tests, pytest for backend tests
- [x] ESLint + Prettier linting
- [x] Dev scripts: dev-start, dev-stop, test-backend, test-frontend, lint

### Session Summary (Phase 1)
Established the full-stack foundation. Next.js App Router frontend with Tailwind, FastAPI backend, Docker Compose networking, BFF proxy pattern via `/app/api` route handlers, health check endpoint working end-to-end, test infrastructure for both sides, linting passes.

---

## Phase 2: Database, Domain Models, CRUD API, and Campaign UI (Completed)

- [x] Step 1: PostgreSQL 16 container in Docker Compose with health check and volume
- [x] Step 2: Python dependencies -- SQLAlchemy 2.0 async, asyncpg, Alembic, psycopg2-binary, aiosqlite (dev)
- [x] Step 3: Database engine/session setup (async engine, get_db dependency, init_db startup)
- [x] Step 4: SQLAlchemy Base model with UUID PK, created_at, updated_at (TimestampMixin)
- [x] Step 5: Domain models -- Campaign, AdGroup, Keyword, Ad with enums, relationships, JSON columns
- [x] Step 6: Alembic setup with sync driver for migrations, initial migration generated and applied
- [x] Step 7: Pydantic schemas -- CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse
- [x] Step 8: Campaign CRUD router -- GET list, POST create, GET by id, PUT update, DELETE
- [x] Step 9: Backend tests -- async SQLite test DB, 9 campaign tests + 2 health tests, all passing
- [x] Step 10: Frontend dependencies -- Zustand and TanStack Query installed, QueryProvider wired
- [x] Step 11: TypeScript types for Campaign domain
- [x] Step 12: BFF route handlers -- /api/campaigns and /api/campaigns/[id] proxying to FastAPI
- [x] Step 13: TanStack Query hooks -- useCampaigns, useCreateCampaign with cache invalidation
- [x] Step 14: Campaign list table and create campaign modal components
- [x] Step 15: Campaigns page at /campaigns, navigation link from home page
- [x] Step 16: Frontend tests -- 4 campaign component tests + 1 existing page test, all passing
- [x] Step 17: Final verification -- all tests pass, lint clean, build succeeds

### Session Summary (Phase 2)
Added the full data layer. PostgreSQL 16 in Docker Compose, SQLAlchemy 2.0 async models for Campaign/AdGroup/Keyword/Ad, Alembic migrations, full CRUD API for campaigns with Pydantic validation, async SQLite test DB for pytest. Frontend gets TanStack Query + Zustand, campaign list/create UI with modal, BFF proxy routes, and comprehensive tests. 11 backend tests, 5 frontend tests, all passing. Lint and build clean.

---

## Phase 3: Agent Pipeline -- Core (Completed)

- [x] Step 1: Add Python dependencies -- anthropic, beautifulsoup4, httpx (moved from dev to main)
- [x] Step 2: Configuration -- ANTHROPIC_API_KEY in Settings, Docker Compose, .env.example
- [x] Step 3: Fix Ad model -- postgresql.JSON to sqlalchemy.JSON for SQLite test compatibility
- [x] Step 4: Pipeline schemas -- PageContent, CampaignStructure, GenerateResponse with nested types
- [x] Step 5: Page fetcher service -- httpx + BeautifulSoup, URL validation, SSRF protection, 19 tests
- [x] Step 6: Claude analyzer service -- Anthropic SDK, system prompt loading, JSON parsing, 16 tests
- [x] Step 7: Campaign saver service -- atomic DB writes, status transition to review, 6 tests
- [x] Step 8: Pipeline orchestrator -- chains fetch/analyze/save with per-step timing and logging
- [x] Step 9: Pipeline router -- POST /api/campaigns/{id}/generate with error mapping, 5 integration tests
- [x] Step 10: Frontend -- BFF proxy route, TypeScript types, useGenerateCampaign hook, Generate button
- [x] Step 11: Frontend tests -- Generate button visibility tests, all 7 frontend tests passing

### Session Summary (Phase 3)
Built the core AI agent pipeline. POST /api/campaigns/{id}/generate triggers a 3-step pipeline: (1) fetch landing page with httpx+BeautifulSoup including SSRF protection, (2) analyze with Claude via Anthropic SDK using the system prompt from docs/SystemPrompt.md, (3) save generated ad groups/keywords/ads to the database and transition campaign to review status. Each step logs start/completion/failure with timing. Frontend gets a Generate button that appears only for draft campaigns. 57 backend tests, 7 frontend tests, all passing. Lint clean. Google Sheets and Ads Script generation deferred to a later phase.

E2E tested with anthropic.com -- Claude generated 4 ad groups (AI Safety Research, Claude AI Assistant, AI Development Platform, AI Learning Resources) with 10 keywords each (phrase + exact), 15 headlines, and 4 descriptions per ad group. Campaign transitioned to review status successfully.

Docker fixes during E2E: system prompt path resolution updated to walk up directory tree instead of hardcoded parents[4] (breaks inside Docker container). Added docs/ volume mount to Docker Compose. Added SYSTEM_PROMPT_PATH config setting. Used --env-file .env.local for Docker Compose variable interpolation.

---

## Phase 3b: Agent Pipeline -- Extensions (Upcoming)

- [ ] Google Sheets integration via MCP
- [ ] Google Ads Script generation

## Phase 4: Review and Approval Workflow (Upcoming)

- [ ] Spreadsheet review UI
- [ ] Approval/rejection flow
- [ ] Campaign status transitions

## Phase 5: Production Readiness (Upcoming)

- [ ] Supabase Auth integration
- [ ] Row-level security
- [ ] Rate limiting and CORS hardening
- [ ] Sentry error tracking
- [ ] Production Docker configuration
