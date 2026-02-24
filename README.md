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

## Quick Start

### 1. Check your environment first

```bash
vibecraft doctor
```

Verifies Python version, required packages, Qwen CLI availability, and project structure.

---

### 2. Create your input files

**`research.md`** — describe your project idea, goals, users, risks.

**`stack.md`** — define your technology choices and architecture principles.

See `examples/` for reference files.

---

### 3. Initialise the project

```bash
vibecraft init --research research.md --stack stack.md
```

Optional: add custom agents via `--agents`:

```bash
vibecraft init --research research.md --stack stack.md --agents examples/custom_agents.yaml
```

This generates:

```
.vibecraft/
├── manifest.json          # project state
├── agents/                # agents tailored to your stack
│   ├── tdd_writer.md
│   ├── implementer.md
│   └── ...
├── skills/
│   ├── research_skill.yaml
│   ├── design_skill.yaml
│   ├── plan_skill.yaml
│   ├── implement_skill.yaml
│   └── review_skill.yaml
├── prompts/               # versioned prompt history (timestamped)
└── snapshots/             # rollback snapshots per skill run

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

### 4. Run a skill

```bash
vibecraft run research
vibecraft run design
vibecraft run plan
vibecraft run implement --phase 1
vibecraft run review
```

#### Dry-run mode (no LLM required)

If you want to use a different LLM (GPT, Claude, Gemini, etc.), use `--dry-run`:

```bash
vibecraft run design --dry-run
```

This builds the full prompt and copies it to your clipboard.
Paste it into any chat interface manually.

You can also set the backend via environment variable:

```bash
VIBECRAFT_BACKEND=clipboard vibecraft run design   # same as --dry-run
VIBECRAFT_BACKEND=echo      vibecraft run design   # test stub
VIBECRAFT_BACKEND=qwen      vibecraft run design   # default Qwen CLI
```

---

### 5. Check project status

```bash
vibecraft status
```

---

### 6. Continue in a new chat

```bash
vibecraft context                        # copies context.md to clipboard
vibecraft context --skill implement      # context + skill prompt
```

Paste into a new LLM chat — the agent knows exactly where you are.

---

### 7. Roll back a skill run

Every `vibecraft run` takes a snapshot before executing.
To undo a run that produced bad output:

```bash
vibecraft snapshots              # list available snapshots
vibecraft rollback               # restore latest snapshot (interactive)
vibecraft rollback 1             # restore second-latest
vibecraft rollback design        # restore most recent 'design' snapshot
```

---

### 8. Export the project

```bash
vibecraft export                        # creates docs/project_summary.md
vibecraft export --format zip           # creates a portable archive
```

---

## Custom Agents

Define project-specific agents in `agents.yaml` (see `examples/custom_agents.yaml`):

```yaml
- name: data_engineer
  triggers: [database, etl, pipeline]

- name: ml_engineer
  triggers: [machine learning, pytorch]
```

Pass it to `init`:

```bash
vibecraft init -r research.md -s stack.md --agents agents.yaml
```

Agents matching any trigger keyword (from research.md or stack.md) are included automatically.

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

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VIBECRAFT_BACKEND` | `qwen` | LLM backend: `qwen`, `clipboard`, `echo` |
| `VIBECRAFT_QWEN_CMD` | `qwen` | Path/name of Qwen CLI binary |
| `EDITOR` / `VISUAL` | `nano` | Editor opened by `[e]` at human gate |

---

## Roadmap

- `v0.1` — init, run, status, context
- `v0.2` — doctor, rollback, export, dry-run, adapter factory, custom agents, prompt versioning ← **current**
- `v0.3` — git hooks to enforce test immutability
- `v0.4` — multi-project workspace support
