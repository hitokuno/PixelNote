# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize SQLite DB (required before first run)
python scripts/init_sqlite.py

# Run all tests (SQLite)
pytest

# Run a single test file
pytest tests/test_create_and_retrieve.py

# Run a single test function
pytest tests/test_create_and_retrieve.py::test_create_and_retrieve

# Start dev server (local, no Docker)
PYTHONPATH=. uvicorn app.main:app --reload

# Build Docker image
docker build -t pixelnote:latest .

# Start dev container (stops/removes existing, copies files, starts server)
./run-dev.sh
docker logs -f pixelnote-dev
```

## Architecture

**Stack:** FastAPI backend + SQLite or Oracle DB (switchable via `.env`). No frontend yet.

**Layer separation:**

```
routes.py  →  db/sqlite_impl.py or db/oracle_impl.py  →  models.py / schemas.py
```

- `routes.py`: HTTP layer only. No try/except, no raise (except HTTPException for 404). Dict conversion via `model.to_dict()` happens here exclusively.
- `db/sqlite_impl.py` / `db/oracle_impl.py`: DB layer. SELECT functions return raw tuples/rows. INSERT/UPDATE functions do not commit. API-level async methods (`create_image`, `save_drawing`, etc.) handle commit/rollback. Raise `RequestValidationError` for business logic errors (e.g., image_id not found), `RuntimeError` for DB errors.
- `models.py`: Internal domain objects (`ImageName`, `Drawing`, `Pixel`). Each maps 1:1 to a table row (all columns). Has `to_dict()` for serialization.
- `schemas.py`: Pydantic models for FastAPI request validation. Validators raise `ValueError` (converted to `RequestValidationError` by FastAPI).
- `main.py`: Global error handlers for `RequestValidationError` (→ 400) and `Exception` (→ 500).
- `db/interface.py`: Abstract interface that both DB implementations must follow.

**DB switching:** Controlled by `DB_BACKEND` env var (`sqlite` or `oracle`). Currently `routes.py` hardcodes `SQLiteDB()` — switching is manual. SQLite uses `?` placeholders; Oracle uses `:1, :2, ...` positional bind variables.

**Table structure:**
- `image_names`: `(image_id PK, image_name, last_modified_by, last_modified_at)` — updated on every save
- `drawings`: `(drawing_id PK AUTOINCREMENT, image_id FK, version, created_at, created_by)` — one row per version
- `pixels`: `(drawing_id FK, x, y, rgb)` — pixels per drawing version

**DB initialization:** `scripts/init_sqlite.py` / `scripts/init_oracle.py`. Run explicitly at setup or CI time. `conftest.py` imports `scripts.init_sqlite` to ensure tables exist before tests. `startup.sh` checks `DB_MODE` env var (note: `.env` uses `DB_BACKEND` — these must align).

**Sort order:** `/api/list` → `last_modified_at DESC`; version lists → `created_at DESC`.

**API routes:**
- `POST /api/create` — creates image + version 1
- `POST /api/save/{image_id}` — adds next version, updates `image_names.last_modified_*`
- `POST /api/rename` — updates `image_names` only
- `GET /api/list` — returns all images sorted by last modified
- `GET /api/images/{image_id}/versions` — returns version numbers as strings, descending
- `GET /api/images/{image_id}/version/{version}` — returns pixel list for a specific version

**CI:** SQLite tests run on every push/PR. Oracle tests run only on manual `workflow_dispatch` (uses `gvenzl/oracle-xe` Docker image).
