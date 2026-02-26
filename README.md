<div align="center">

# 🛠️ Vibecraft

### *Craft your project from a research idea.*

Agent-driven development framework that bootstraps a complete project workspace from just two files: `research.md` and `stack.md`.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-v0.4_dev-orange?style=flat-square)]()

</div>

---

## 🧠 Philosophy

```
research → design → plan → implement (TDD) → review
```

Each phase is driven by **specialised agents**. Skills orchestrate which agents run and in what order. Context is always documented so you can open a new chat at any phase.

---

## ⚡ Install

### Windows

<details>
<summary><b>Option 1 — One-Click Global Install</b> (recommended)</summary>

Double-click `install.bat` in the vibecraft-framework folder. This installs vibecraft globally and adds it to your PATH.

```bash
pip install vibecraft
```

Verify installation:
```bash
vibecraft --help
vibecraft doctor
```

</details>

<details>
<summary><b>Option 2 — PowerShell or CMD</b></summary>

```bash
# Clone or download the repository
cd vibecraft-framework

# Install in development mode
pip install -e .

# Or install with test dependencies
pip install -e ".[test]"
```

### Option 3: Local Install (No Admin Required)

</details>

<details>
<summary><b>Option 3 — Local Install</b> (per-project, no admin required)</summary>

Installs vibecraft into your project directory (`.vibecraft-venv/`).

```bash
# In your project directory
python vibecraft-framework/install-to-project.py

Then use:
```bash
vibecraft-local.bat --help
vibecraft-local.bat doctor
```

</details>

<details>
<summary><b>Option 4 — No Install</b> (run with py launcher)</summary>

```bash
py -m vibecraft --help
```

Or use the included launcher:
```bash
vibecraft.bat --help
```

</details>

### ✅ Verify Installation

```bash
vibecraft doctor
```

---

## 🚀 Quick Start

### 1️⃣ Check your environment

Create two files in your project directory:

**`research.md`** — Describe your project idea:
```markdown
# My Project — Research

## Project Vision
Build a task management API for small teams.

## Goals
1. User authentication and authorization
2. CRUD operations for tasks
3. Real-time updates via WebSocket
4. Filter and search functionality

## Users
- Team leads who assign tasks
- Team members who complete tasks
- Admins who manage users

## Risks
- Authentication complexity
- Real-time sync challenges
- Database performance at scale
```

**`stack.md`** — Define your technology stack:
```markdown
# Technology Stack

## Backend
- Python 3.10+
- FastAPI — async web framework
- SQLAlchemy — ORM
- PostgreSQL — database

### 2️⃣ Create your input files

| File | Purpose |
|------|---------|
| `research.md` | Describe your project idea, goals, users, and risks |
| `stack.md` | Define your technology choices and architecture principles |

> 💡 See the `examples/` folder for reference files.

---

### 3️⃣ Initialise the project

```bash
vibecraft init --research research.md --stack stack.md
```

With custom agents:
```bash
vibecraft init -r research.md -s stack.md
```

This generates the following workspace:

```
📁 .vibecraft/
├── 📄 manifest.json          # project state
├── 📁 agents/                # agents tailored to your stack
│   ├── tdd_writer.md
│   ├── implementer.md
│   └── ...
├── 📁 skills/
│   ├── research_skill.yaml
│   ├── design_skill.yaml
│   ├── plan_skill.yaml
│   ├── implement_skill.yaml
│   └── review_skill.yaml
├── 📁 prompts/               # versioned prompt history (timestamped)
└── 📁 snapshots/             # rollback snapshots per skill run

📁 docs/
├── 📄 context.md             # paste this into any new chat
├── 📄 research.md
├── 📄 stack.md
├── 📁 design/
└── 📁 plans/

📁 src/
└── 📁 tests/                 # sacred — tdd_writer only
```

---

### 4️⃣ Run a skill

```bash
# Phase 1: Research
vibecraft run research

# Phase 2: Design
vibecraft run design

# Phase 3: Plan
vibecraft run plan

# Phase 4: Implement (TDD cycle)
vibecraft run implement --phase 1

# Phase 5: Review
vibecraft run review
```

> **How it works — Clipboard Workflow**
>
> Vibecraft uses a **clipboard-based workflow** by default — no LLM API key required!
>
> 1. Each step builds a prompt and copies it to your clipboard
> 2. Paste the prompt into any LLM (GPT, Claude, Gemini, etc.)
> 3. Copy the response back to vibecraft
> 4. Human approval gates ensure you control every step

---

### 5️⃣ Check project status

```bash
vibecraft status
```

Output:
```
Project: My Project
Type:    api
Phase:   implement
Updated: 2024-02-27T10:30:00Z

  Phase       Status      Command
  ─────────────────────────────────
  research    ✓ done
  design      ✓ done
  plan        ✓ done
  implement   → current   vibecraft run implement
  review      pending

Agents: researcher, architect, planner, ...
Stack: {FastAPI, SQLAlchemy, PostgreSQL, ...}
```

---

### 6️⃣ Continue in a new chat

```bash
# Copy context to clipboard
vibecraft context

# Copy context + specific skill prompt
vibecraft context --skill implement
```

Paste into a new LLM chat — the agent knows exactly where you left off.

### Rollback Support

### 7️⃣ Roll back a skill run

Every `vibecraft run` takes a snapshot before executing, so you can always undo.

```bash
# List available snapshots
vibecraft snapshots

# Restore latest snapshot
vibecraft rollback

# Restore specific snapshot
vibecraft rollback 2

# Restore by skill name
vibecraft rollback design
```

---

### 8️⃣ Export the project

```bash
vibecraft export                  # creates docs/project_summary.md
vibecraft export --format zip     # creates a portable archive
```

---

## 🤖 Custom Agents

### Example 1: REST API Project

**research.md:**
```markdown
# Task API — Research

## Vision
REST API for task management with authentication.

## Features
- User registration/login
- CRUD for tasks
- Filter by status, priority
- Pagination

## Users
- End users (create/manage tasks)
- Admins (manage all tasks)
```

**stack.md:**
```markdown
# Stack

## Backend
- Python 3.10+
- FastAPI
- SQLAlchemy + PostgreSQL
- PyJWT for auth

## Testing
- pytest
- httpx
```

**Initialize and run:**
```bash
vibecraft init -r research.md -s stack.md
vibecraft run research
vibecraft run design
vibecraft run plan
vibecraft run implement --phase 1
```

### Example 2: Modular SaaS Application

```bash
# Initialize in modular mode
vibecraft init -r research.md -s stack.md --mode modular

# Create modules
vibecraft module create users -d "User management"
vibecraft module create auth -d "Authentication" --depends-on users
vibecraft module create billing -d "Billing system" --depends-on users
vibecraft module create api -d "REST API" --depends-on auth,billing

# Analyze and build
vibecraft integrate analyze
vibecraft integrate build

# Implement modules in order
vibecraft run implement --phase 1 --module users
vibecraft run implement --phase 1 --module auth
vibecraft run implement --phase 1 --module billing
vibecraft run implement --phase 1 --module api
```

---

## ❓ FAQ

### Do I need an LLM API key?

**No!** Vibecraft uses clipboard-based workflow. You paste prompts into any LLM chat (ChatGPT, Claude, Gemini, etc.) and copy responses back. No API integration required.

### Can I use Vibecraft with my existing project?

Yes! Create `research.md` and `stack.md` describing your project, then run:
```bash
vibecraft init -r research.md -s stack.md
```

Vibecraft will generate agents and skills tailored to your stack.

### What if I make a mistake?

Use rollback:
```bash
vibecraft snapshots     # List snapshots
vibecraft rollback      # Restore latest
```

### How do I continue in a new chat session?

```bash
vibecraft context    # Copies context.md to clipboard
```

Paste into any new LLM chat — the agent knows your project state.

### Can I customize agents?

Yes! Create `agents.yaml`:
```yaml
- name: data_engineer
  triggers: [database, etl, pipeline]

- name: ml_engineer
  triggers: [machine learning, pytorch]
```

Then:
```bash
vibecraft init -r research.md -s stack.md --agents agents.yaml
```

Agents matching any trigger keyword from `research.md` or `stack.md` are included automatically.

---

## 🧪 TDD Rules

These are enforced at the agent level and should be upheld at every human gate:

| Rule | Enforced By |
|------|-------------|
| ✅ Only writes tests | `tdd_writer` |
| 🚫 Never modifies `src/tests/` | `implementer` |
| 🔒 Tests locked after approval | **You** (human gate) |
| 🚩 Flags issues, doesn't fix tests | `implementer` |

---

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EDITOR` / `VISUAL` | `nano` | Editor opened by `[e]` at human gate |
| `PYTHONIOENCODING` | `utf-8` | Console encoding (auto-set on Windows) |

---

## 📍 Roadmap

| Version | Status | Highlights |
|---------|--------|------------|
| `v0.1` | ✅ Released | `init`, `run`, `status`, `context` |
| `v0.2` | ✅ Released | `doctor`, `rollback`, `export`, custom agents, prompt versioning |
| `v0.3` | ✅ Released | Clipboard-only workflow, improved installer, TDD RED/GREEN phases |
| `v0.4` | 🔄 **In Progress** | Local project installation, PATH reliability fixes |
| `v0.5` | 🔜 Planned | Git hooks to enforce test immutability |
| `v0.6` | 🔜 Planned | Multi-project workspace support |

---

<div align="center">

Made with ❤️ for developers who think before they build.

</div>
