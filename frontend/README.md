# SBS League Dashboard — Frontend

React + Vite + TypeScript frontend for the SBS League Dashboard, replacing the original Streamlit app. Talks to the FastAPI backend in `../backend`.

## Stack

- React Router for pages (`/`, `/teams`, `/scoreboard`, `/admin`)
- TanStack Query for data fetching/caching against the backend API
- Tailwind CSS v4 for styling (custom theme tokens in `src/styles/global.css`)
- `lucide-react` for icons

## Running locally

```bash
npm install
npm run dev
```

Runs on `http://localhost:5173` and expects the backend at `http://localhost:8000` (override with `VITE_API_URL` in a `.env` file — see `.env.example`).

## Structure

- `src/api/` — API client, TypeScript types mirroring the backend's Pydantic schemas, and TanStack Query hooks
- `src/components/` — shared UI: `MatchupCard`, `RegularSeasonColumn`/`PlayoffBoxscores` (the two matchup-box-score layouts reused across pages), roster/standings tables, and `ui/` primitives (`Select`, `Section`, `Card`, `Badge`, loading/empty states)
- `src/pages/` — one file per route
- `src/lib/` — small formatting/constant helpers
