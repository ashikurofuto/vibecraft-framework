# Stack

## Language: TypeScript
## Framework: Phaser.js (game engine)
## Architecture: Clean Architecture
## Testing: Vitest
## Backend: Node.js + Express
## Realtime: WebSocket (ws library)
## DB: None (v1 — in-memory session state only)
## Linting: ESLint + Prettier

## Principles
- No `any` types
- Repository pattern for all state access
- Domain layer has zero framework imports
- All side effects isolated and injectable
- Tests must run without a browser (jsdom)
