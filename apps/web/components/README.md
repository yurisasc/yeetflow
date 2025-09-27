# YeetFlow Components

This folder contains provider-agnostic, reusable UI components for the web app. It intentionally avoids direct coupling to Next.js server actions, providers, or app-specific data-fetching. This allows us to later extract `components/` into a separate package and reuse it in other client apps.

## Design Principles

- **Provider-agnostic UI**
  - Components should not import app providers (e.g. `useAuth`) or feature-specific server action modules.
  - Pass data and functions via props, so callers decide how to wire them.

- **Server-first data fetching & server actions**
  - Feature mutations should live in colocated route action files: `app/(segment)/feature/actions.ts`.
  - Server pages pass server actions to client layouts via props.
  - Client components display errors; server actions perform redirects and revalidation.

- **Clear boundaries**
  - `components/` owns UI and UX and must not include `'use client'` directives.
  - `app/(segment)` owns server data fetching, server actions, and client adapters (which may use `'use client'`).

## Folder Conventions

- `components/<feature>/layout.tsx`
  - Main client UI for a feature (provider-agnostic).
  - Accepts data and callbacks (e.g. `startFlow`, `onLogout`).

- `components/<feature>/*` (subcomponents)
  - Smaller, focused UI pieces like `header`, `grid`, `card`, `tabs`, etc.

- `app/(segment)/feature/actions.ts` (Server Actions)
  - Colocated server actions (mutations). E.g. `app/(app)/flows/actions.ts`.
  - Validate inputs (e.g. Zod), call BFF/SDK, redirect or return typed errors.

## Error Handling & Redirects

- When an action succeeds and should navigate, perform the redirect in the server action (server-side navigation).
- When an action fails validation or throws, return a typed error payload from the action and let the client layout render the error state.

## Extracting `components/` in the future

- Keep `components/` free from Next.js-only dependencies (`next/*`, `app/(segment)/*`, server action imports).
- When extracting, publish `components/` as a separate package; keep adapters in the Next.js app.

## Type Guidelines

- UI components accept callbacks as props:
  - For server actions: `(formData: FormData) => Promise<void | { success: false; error: string }>`
  - For client adapters: explicit payload/result types, e.g. `onLogin({ email, password }): Promise<{ ok: true } | { ok: false; error: string }>`
- Avoid importing types from `app/(segment)` into `components/` to maintain decoupling.

---

This pattern ensures our UI stays portable and testable, while Next.js-specific behavior remains in the Next.js app.
