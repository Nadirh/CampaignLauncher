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

## Phase 3b: Excel Export for Campaign Review (Completed)

- [x] Step 1: Add openpyxl dependency to pyproject.toml
- [x] Step 2: Create Excel export service (generate_workbook with Summary, Keywords, Ads sheets)
- [x] Step 3: Unit tests for Excel service -- 14 tests covering all sheets, helpers, edge cases
- [x] Step 4: FastAPI export endpoint (GET /api/campaigns/{id}/export), registered in main.py, 4 integration tests
- [x] Step 5: Frontend BFF proxy route for binary passthrough, Download Excel button on detail page, 2 new frontend tests
- [x] Step 6: Updated CLAUDE.md to reflect Excel export approach (replaces Google Sheets MCP)
- [x] Step 7: All tests pass (82 backend, 21 frontend), lint clean

### Session Summary (Phase 3b)
Added Excel export as a universal baseline for campaign review. openpyxl generates .xlsx workbooks in-memory (no temp files) with three tabs: Summary (key-value campaign metadata), Keywords (denormalized with ad group name for filtering), and Ads (headlines and descriptions as numbered multi-line strings). The service takes a Pydantic model (CampaignGenerateResponse) for testability without DB. FastAPI endpoint streams the binary response with proper content type and Content-Disposition. Frontend BFF proxy passes the binary through (raw fetch, not fetchFromApi which adds JSON headers). Download Excel button appears on the detail page whenever ad groups exist, with loading state and error handling. Replaces the original Google Sheets MCP approach -- Google Sheets can be added as an optional upload target later.

## Phase 3c: Agent Pipeline -- Extensions (Upcoming)

- [ ] Google Ads Script generation

## Phase 4: Review and Approval Workflow (Completed)

- [x] Step 1: Backend -- Enhance GET detail with selectinload for nested ad groups, add POST approve/reject endpoints with status validation (409 for wrong status)
- [x] Step 2: Backend tests -- 7 new tests for detail with nested data, approve/reject success/wrong status/not found (64 total)
- [x] Step 3: Frontend BFF proxy routes for approve and reject, updated GET return type to GenerateResponse
- [x] Step 4: TanStack Query hooks -- useCampaignDetail, useApproveCampaign, useRejectCampaign with cache invalidation
- [x] Step 5: Reusable ConfirmModal component following existing modal pattern
- [x] Step 6: Campaign detail page -- header with status badge, approve/reject buttons (review only), collapsible ad groups, keywords table, ad preview
- [x] Step 7: Campaign names as clickable links in campaign list table
- [x] Step 8: Frontend tests -- 12 new tests (6 campaign-detail, 5 confirm-modal, 1 link), lint clean

### Session Summary (Phase 4)
Added the review and approval workflow. Backend GET /api/campaigns/{id} now returns nested ad groups with keywords and ads via selectinload. Added POST approve (review -> approved) and reject (review -> draft) endpoints with 409 on invalid status. Frontend gets a campaign detail page at /campaigns/[id] with collapsible ad groups showing keywords and ad copy, approve/reject buttons with confirmation modals, and status-colored badges. Campaign names in the list table are now clickable links to the detail page. 64 backend tests, 19 frontend tests, all passing. Lint clean.

## Phase 4b: Campaign Settings + Pin Positions & Behavioral Triggers (Completed)

- [x] Step 1: Backend model -- 4 new nullable columns (match_types, negative_keywords, bid_value, location_targeting), bidding_strategy default changed to TARGET_CPA, Alembic migration
- [x] Step 2: Backend schemas -- Settings fields added to CampaignCreate/Update/Response and CampaignGenerateResponse, trigger field on HeadlineData/DescriptionData, campaign_saver persists triggers
- [x] Step 3: Claude analyzer -- analyze_page and _build_user_message accept campaign settings kwargs, dynamic match type instruction, Campaign Settings section in user message, trigger field in JSON schema example
- [x] Step 4: Backend tests -- Updated default bidding_strategy assertion, added test_create_campaign_with_settings and test_update_campaign_settings, 6 new claude_analyzer tests for triggers/settings/match types
- [x] Step 5: Excel export -- Summary sheet includes Match Types, Negative Keywords, Bid Value, Location Targeting rows; Ads sheet restructured to one row per headline/description with separate columns for Type, #, Copy, Pin Position, Trigger, Length
- [x] Step 6: Frontend types and create modal -- Campaign/CampaignCreate/GenerateResponse/AdResponse types updated; modal widened with scroll, 6 settings fields with defaults (match types checkboxes, bidding strategy dropdown, bid value, daily budget, negative keywords, location targeting)
- [x] Step 7: Frontend detail page -- Pin position badges and trigger text on headlines, trigger text on descriptions, campaign settings row in header area
- [x] Step 8: All tests pass (91 backend, 24 frontend), lint clean

### Session Summary (Phase 4b)
Added campaign settings and behavioral triggers throughout the stack. The create modal now collects 6 campaign settings (match types as checkboxes defaulting to phrase+exact, bidding strategy dropdown defaulting to target_cpa, bid value, daily budget, negative keywords as comma-separated, location targeting). All settings except negative keywords are required (Google Ads needs them). These settings are threaded through to the Claude analyzer which includes them in the user message and requests behavioral trigger labels (from the 7-item Behavioral Toolbox in SystemPrompt.md) on every headline and description. The campaign saver persists trigger values alongside text and position data. The Excel Ads sheet outputs one row per headline/description with separate columns: Ad Group, Ad #, Type, #, Copy, Pin Position, Trigger, Length, Final URL, Path -- keeping the Copy column clean for business user review. The detail page displays pin position badges, trigger labels, and campaign settings. All changes are backwards compatible -- missing triggers or positions are handled gracefully.

---

## Phase 5: Production Readiness (Upcoming)

- [ ] Supabase Auth integration
- [ ] Row-level security
- [ ] Rate limiting and CORS hardening
- [ ] Sentry error tracking
- [ ] Production Docker configuration
