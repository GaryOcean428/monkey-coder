# Build outputs and ignore rules

This repo uses a monorepo with a Next.js frontend and a FastAPI backend.

- Frontend (packages/web)
  - Next.js 15 with `output: 'export'`
  - Static export directory: `packages/web/out`
  - On Railway, the frontend is built in the deploy step and the `out/` directory is included as a deploy artifact.
  - The backend serves the static export at runtime. It probes these locations in order:
    - `/app/out`
    - `/app/packages/web/out`
    - `<repo-root>/out`
    - `<repo-root>/packages/web/out`
    - `/app/docs/build` (fallback)

- Backend (packages/core)
  - FastAPI app started via `Python run_server.py`
  - No compiled/dist output is committed.

- Ignore rules
  - `.gitignore` ignores typical Node/Python outputs, including `.next/`.
  - **UPDATE (2025-08-18)**: `out/` directory is now tracked in git for Railway deployment.
  - Exception: `services/sandbox/Dockerfile` is explicitly allowed so it can be tracked.
  - **UPDATE (2025-08-18)**: Dockerfiles in root are now allowed for flexible Railway deployment.
  - There is no `.dockerignore` at the root. Railpack handles deploy inputs via `railpack.json`.

- Deploy
  - `railpack.json` orchestrates two steps: `web` (builds Next.js export) and `Python`
    (installs Python deps). The unified service starts with `Python run_server.py`.

Keep Next.js static export-only mode unless switching to server rendering.
If you switch, update `railpack.json` and FastAPI static mounting accordingly.
