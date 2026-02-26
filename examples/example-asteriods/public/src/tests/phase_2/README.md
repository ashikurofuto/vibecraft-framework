# Phase 2 Tests — Application Layer

**Created:** 2026-02-26  
**Status:** RED Phase (tests written before implementation)  
**TDD Agent:** tdd_writer

---

## 📋 What These Tests Verify

These tests cover the **Application Layer** of the Asteroids game, which is responsible for:

- Game state management (menu, playing, paused, gameover)
- Score tracking and high score persistence
- Game loop with fixed timestep physics
- Main game facade integrating all components

---

## 🧪 Test Files

| File | Component | Purpose |
|------|-----------|---------|
| `GameState.test.js` | `GameState` | State transitions, lives, levels |
| `ScoreManager.test.js` | `ScoreManager` | Score tracking, high score management |
| `GameLoop.test.js` | `GameLoop` | Fixed timestep, accumulator pattern |
| `Game.test.js` | `Game` | Main facade, integration of all components |

---

## 🎯 Coverage Intentions

### GameState
- Initial state is 'menu'
- Transitions: menu → playing → paused → playing
- Lives decrement on hit
- Game over when lives reach 0
- Level progression
- Score tracking integration

### ScoreManager
- Initial score is zero
- Adding scores
- High score tracking and persistence
- High score updates only when exceeded
- Reset functionality

### GameLoop
- Start/stop functionality
- Fixed timestep (1/60 sec) calls to update
- Accumulator pattern for multiple updates
- Render called after updates
- Spiral of death prevention

### Game (Facade)
- Initialization in menu state
- Start game transitions to playing
- Input handling only when playing
- Pause/resume functionality
- Score management
- State access for renderer

---

## ❌ What Is NOT Covered (For Implementer Awareness)

These aspects are intentionally deferred to later phases:

1. **Integration with Canvas rendering** — Phase 4 (Presentation Layer)
2. **Actual input from keyboard** — Phase 4 (InputHandler)
3. **Audio integration** — Phase 3 (Infrastructure Layer)
4. **localStorage persistence** — Phase 3 (Storage)
5. **Ship/Asteroid/Bullet entity management** — Tested in domain layer
6. **Collision detection logic** — Tested in domain layer
7. **UI/HUD updates** — Phase 5 (UI Polish)

---

## 🚦 Running These Tests

```bash
# Run all tests
npm test

# Run only phase 2 tests
npm test -- --testPathPattern="phase_2"

# Run with coverage
npm run test:coverage
```

---

## 🔒 Immutable Contract

**These tests are LOCKED after approval.**

The implementer must:
- Write code to make these tests pass (GREEN phase)
- Never modify these test files
- Follow TDD: RED → GREEN → REFACTOR

---

**TDD Status:** RED (tests written, awaiting implementation)
