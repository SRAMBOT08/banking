# Lokii Frontend

Lokii is the AI-Native Security Operations Platform analyst workspace. This application is a Next.js 15 / React 19 frontend that communicates with the existing backend through the Gateway HTTP API.

## Run locally

From this directory:

```powershell
npm install
npm run dev
```

Open `http://localhost:3000`. Without a running Gateway, the workspace uses deterministic local fixtures so the complete analyst experience remains available during UI development. Set `NEXT_PUBLIC_GATEWAY_URL` to connect to the deployed Gateway.

## Structure

- `src/app` — App Router, global theme, providers
- `src/components` — reusable shell, panels, status elements, workspace views
- `src/lib/api.ts` — typed Gateway boundary
- `src/lib/mock.ts` — deterministic development fixtures
- `src/lib/store.ts` — Zustand UI/session state

The UI does not communicate with Kafka directly; it uses the existing Gateway HTTP boundary as defined by the backend service contract.
