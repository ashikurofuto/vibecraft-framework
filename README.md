# Vibecraft 🛠️

> Craft your project from a research idea.

Agent-driven development framework that bootstraps a complete project workspace
from two files: `research.md` and `stack.md`.

---

## Philosophy

```
research → design → plan → implement (TDD) → review
```

Each phase is driven by specialised agents.  
Skills orchestrate which agents run and in what order.  
Context is always documented so you can open a new chat at any phase.

---

## Install

```bash
pip install -e .
```

---

## Usage

### 1. Create your input files

**`research.md`** — describe your project idea, goals, users, risks.

**`stack.md`** — define your technology choices and architecture principles.

See `examples/` for reference files.

---

### 2. Initialise the project

```bash
vibecraft init --research research.md --stack stack.md
```

This generates:

```
.vibecraft/
├── manifest.json          # project state
├── agents/                # agents tailored to your stack
│   ├── tdd_writer.md
│   ├── implementer.md
│   └── ...
└── skills/
    ├── research_skill.yaml
    ├── design_skill.yaml
    ├── plan_skill.yaml
    ├── implement_skill.yaml
    └── review_skill.yaml

docs/
├── context.md             # paste this into any new chat
├── research.md
├── stack.md
├── design/
└── plans/

src/
└── tests/                 # sacred — tdd_writer only
```

---

### 3. Run a skill

```bash
vibecraft run research     # builds prompt → copies to clipboard
vibecraft run design       # produces C4 architecture + ADRs
vibecraft run plan         # breaks into phases
vibecraft run implement --phase 1
vibecraft run review
```

Vibecraft builds the full prompt (skill + agents + context) and copies it to
your clipboard. Paste it into Qwen (or any LLM chat) to run the skill.

---

### 4. Check project status

```bash
vibecraft status
```

---

### 5. Continue in a new chat

```bash
vibecraft context                         # copies context.md to clipboard
vibecraft context --skill implement       # context + skill prompt
```

Paste into a new Qwen chat — the agent knows exactly where you are.

---

## TDD Rules

These are enforced at the agent level and should be enforced by you as the human gate:

| Rule | Who |
|------|-----|
| Only writes tests | `tdd_writer` |
| Never modifies `src/tests/` | `implementer` |
| Tests locked after your approval | You (human gate) |
| Flags issues, doesn't fix tests | `implementer` |

---

## Roadmap

- `v0.1` — init, run, status, context (current)
- `v0.2` — git hooks to enforce test immutability
- `v0.3` — Qwen CLI direct subprocess adapter
- `v0.4` — multi-project workspace support
