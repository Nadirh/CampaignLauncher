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

## Phase 3: Agent Pipeline (Upcoming)

- [ ] Landing page fetching via Puppeteer MCP
- [ ] Page content analysis via Claude API (above-the-fold focus)
- [ ] Keyword generation (tightly themed ad groups)
- [ ] RSA ad copy generation (headlines + descriptions)
- [ ] Google Sheets integration via MCP
- [ ] Google Ads Script generation
- [ ] Agent chain logging and error handling

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
