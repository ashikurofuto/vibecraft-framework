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

### Windows — Installation Options

**Option 1: Global install (One-Click)**

Double-click `install.bat` in the vibecraft-framework folder.

This installs vibecraft globally and adds it to your PATH.

```bash
# After installation, restart your terminal and verify:
vibecraft --help
```

**Option 2: Global install (PowerShell or CMD)**

```powershell
# PowerShell
cd vibecraft-framework
.\install.ps1
```

```cmd
REM Command Prompt
cd vibecraft-framework
python install.py
```

**Option 3: Local install (per-project, no admin required)**

Installs vibecraft into your project directory (`.vibecraft-venv/`).

```bash
cd your-project
python vibecraft-framework\install-to-project.py
```

Then use:
```bash
vibecraft-local.bat --help
vibecraft-local.bat doctor
```

**Option 4: No installation (run with py launcher)**

If you have Python installed, you can run without installation:

```bash
py -m vibecraft --help
```

Or use the included launcher:
```bash
vibecraft.bat --help
```

### Verify Installation

```bash
vibecraft doctor
```

Or for local installation:
```bash
vibecraft-local.bat doctor
```

---

## Quick Start

### 1. Check your environment first

```bash
vibecraft doctor
```

Verifies Python version, required packages, and project structure.

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

#### How it works

Vibecraft uses **clipboard-based workflow** by default:
- Each step builds a prompt and copies it to your clipboard
- Paste the prompt into any LLM (GPT, Claude, Gemini, etc.)
- Copy the response back to vibecraft
- Human approval gates ensure you control every step

No LLM integration required — use any AI assistant you prefer!

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
| `EDITOR` / `VISUAL` | `nano` | Editor opened by `[e]` at human gate |
| `PYTHONIOENCODING` | `utf-8` | Console encoding (auto-set on Windows) |

---

## Roadmap

- `v0.1` — init, run, status, context
- `v0.2` — doctor, rollback, export, custom agents, prompt versioning
- `v0.3` — clipboard-only workflow, improved installer, TDD RED/GREEN phases
- `v0.4` — local project installation, PATH reliability fixes ← **current development**
- `v0.5` — git hooks to enforce test immutability
- `v0.6` — multi-project workspace support
