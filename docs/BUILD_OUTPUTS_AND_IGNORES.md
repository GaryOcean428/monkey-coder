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
  - `.gitignore` ignores typical Node/Python outputs, including `.next/` and `out/`.
  - Exception: `services/sandbox/Dockerfile` is explicitly allowed so it can be tracked
    while other Dockerfiles remain ignored to avoid conflicts with Railpack builds.
  - There is no `.dockerignore` at the root. Railpack handles deploy inputs via `railpack.JSON`.

- Deploy
  - `railpack.JSON` orchestrates two steps: `web` (builds Next.js export) and `Python`
    (installs Python deps). The unified service starts with `Python run_server.py`.

Keep Next.js static export-only mode unless switching to server rendering.
If you switch, update `railpack.JSON` and FastAPI static mounting accordingly.
