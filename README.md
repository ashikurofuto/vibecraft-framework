# Vibecraft Framework 🛠️

> **Craft your project from a research idea.**

[![PyPI version](https://img.shields.io/pypi/v/vibecraft.svg)](https://pypi.org/project/vibecraft/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Agent-driven development framework** that bootstraps a complete project workspace from two files: `research.md` and `stack.md`.

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Core Concepts](#-core-concepts)
- [Command Reference](#-command-reference)
- [Dual-Mode Architecture](#-dual-mode-architecture)
- [Examples](#-examples)
- [FAQ](#-faq)
- [Contributing](#-contributing)

---

## ✨ Features

### 🎯 What Vibecraft Does

- **Bootstraps projects** from `research.md` + `stack.md`
- **Generates specialized agents** tailored to your tech stack
- **Creates skill workflows** for each development phase
- **Manages context** so you can continue in any LLM chat
- **Enforces TDD** with RED/GREEN test cycles
- **Tracks progress** through phases: research → design → plan → implement → review
- **Rollback support** with snapshots for every skill run
- **Dual-Mode Architecture**: Simple mode for small projects, Modular mode for large ones

### 🤖 Agent System

Vibecraft generates 10+ specialized agents:

| Agent | Role |
|-------|------|
| `researcher` | Gathers requirements and clarifies goals |
| `architect` | Designs system architecture |
| `planner` | Creates implementation plan |
| `plan_reviewer` | Reviews plan for completeness |
| `pre_checker` | Verifies dependencies and setup |
| `tdd_writer` | Writes tests first (RED phase) |
| `implementer` | Implements code to pass tests (GREEN phase) |
| `code_reviewer` | Reviews code quality |
| `security_auditor` | Checks for security issues |
| `api_designer` | Designs API interfaces |

### 🔄 TDD Workflow

```
RED Phase:  Write tests → Run tests (must FAIL) → Confirm RED
GREEN Phase: Implement code → Run tests (must PASS) → Confirm GREEN
Review: Code review → Security audit → Merge
```

---

## 📦 Installation

### Requirements

- **Python 3.10+** (required)
- **pip** (Python package manager)

### Option 1: Install from PyPI (Recommended)

```bash
pip install vibecraft
```

Verify installation:
```bash
vibecraft --help
vibecraft doctor
```

### Option 2: Install from Source

```bash
# Clone or download the repository
cd vibecraft-framework

# Install in development mode
pip install -e .

# Or install with test dependencies
pip install -e ".[test]"
```

### Option 3: Local Install (No Admin Required)

For per-project installation without admin rights:

```bash
# In your project directory
python vibecraft-framework/install-to-project.py

# Use the local launcher
./vibecraft-local.bat --help    # Windows
./vibecraft-local.sh --help     # macOS/Linux
```

### Verify Installation

```bash
vibecraft doctor
```

Expected output:
```
Vibecraft Doctor

  [OK]  [Python version] 3.10+  →  OK  Required ≥ 3.10
  [OK]  [Package] click  →  OK
  [OK]  [Package] jinja2  →  OK
  [OK]  [Package] yaml  →  OK
  [OK]  [Package] rich  →  OK
  [OK]  [Package] pyperclip  →  OK

[OK] Everything looks good!
```

---

## 🚀 Quick Start

### Step 1: Create Input Files

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

## Authentication
- PyJWT — JWT tokens
- passlib — password hashing

## Real-time
- WebSockets — live updates

## Testing
- pytest — test framework
- httpx — async HTTP client

## Code Quality
- ruff — linter
- mypy — type checker
```

### Step 2: Initialize Project

```bash
vibecraft init -r research.md -s stack.md
```

This generates:
```
your-project/
├── .vibecraft/
│   ├── manifest.json          # Project state
│   ├── agents/                # 10+ specialized agents
│   ├── skills/                # 5 skill workflows
│   ├── prompts/               # Versioned prompts
│   └── snapshots/             # Rollback snapshots
├── docs/
│   ├── context.md             # Context for new chats
│   ├── research.md
│   ├── stack.md
│   ├── design/
│   └── plans/
└── src/
    └── tests/                 # Test directory (TDD)
```

### Step 3: Run Development Phases

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

### Step 4: Check Progress

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

## 🧠 Core Concepts

### How Vibecraft Works

```
┌─────────────────────────────────────────────────────────┐
│  1. You create research.md + stack.md                   │
│  2. vibecraft init generates agents + skills            │
│  3. vibecraft run <skill> executes workflow:            │
│     a. Builds prompt for current step                   │
│     b. Copies prompt to clipboard                       │
│     c. You paste into LLM (GPT, Claude, etc.)           │
│     d. You copy LLM response back                       │
│     e. Human approval gate (y/n/e/r)                    │
│     f. Saves output to project                          │
│  4. Context is tracked for continuity                   │
└─────────────────────────────────────────────────────────┘
```

### Clipboard-Based Workflow

Vibecraft uses **clipboard-based workflow** by default:

1. **Prompt Generation**: Vibecraft builds a detailed prompt for the current step
2. **Copy to Clipboard**: Prompt is automatically copied to your clipboard
3. **LLM Interaction**: You paste the prompt into any LLM (GPT-4, Claude, Gemini, etc.)
4. **Response**: You copy the LLM's response
5. **Human Gate**: Vibecraft asks for approval:
   - `y` — Approve and continue
   - `n` — Reject and abort
   - `e` — Edit in editor, then continue
   - `r` — Retry the step

**No LLM integration required** — use any AI assistant you prefer!

### Context Management

Continue your work in any new chat:

```bash
# Copy context to clipboard
vibecraft context

# Copy context + specific skill prompt
vibecraft context --skill implement
```

Paste into a new LLM chat — the agent knows exactly where you are.

### Rollback Support

Every `vibecraft run` takes a snapshot before executing:

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

## 📖 Command Reference

### Project Initialization

| Command | Description |
|---------|-------------|
| `vibecraft init -r <research> -s <stack>` | Initialize new project |
| `vibecraft init --mode modular` | Initialize in modular mode |
| `vibecraft init --agents <file>` | Use custom agents |

### Skill Execution

| Command | Description |
|---------|-------------|
| `vibecraft run research` | Run research phase |
| `vibecraft run design` | Run design phase |
| `vibecraft run plan` | Run planning phase |
| `vibecraft run implement --phase N` | Run TDD implementation for phase N |
| `vibecraft run review` | Run review phase |

### Project Management

| Command | Description |
|---------|-------------|
| `vibecraft status` | Show project status and phase progress |
| `vibecraft context` | Copy context.md to clipboard |
| `vibecraft context --skill <name>` | Copy context + skill prompt |
| `vibecraft doctor` | Check environment and dependencies |
| `vibecraft snapshots` | List available rollback snapshots |
| `vibecraft rollback [N]` | Restore project to snapshot |
| `vibecraft export` | Export project summary |
| `vibecraft export --format zip` | Export as ZIP archive |

### Modular Mode Commands

| Command | Description |
|---------|-------------|
| `vibecraft module create <name> -d "<desc>"` | Create new module |
| `vibecraft module create <name> --depends-on a,b` | Create with dependencies |
| `vibecraft module list` | List all modules |
| `vibecraft module init <name>` | Initialize module structure |
| `vibecraft module status <name>` | Show module status |
| `vibecraft run implement --phase N --module <name>` | Run implement for module |
| `vibecraft integrate analyze` | Analyze module dependencies |
| `vibecraft integrate build` | Build integration layer |

---

## 🏗️ Dual-Mode Architecture

Vibecraft v0.4 supports two modes:

### Simple Mode (Default)

**Best for:** Small projects (< 10 files, 1-2 developers)

```bash
vibecraft init -r research.md -s stack.md
```

**Structure:**
```
project/
├── src/              # All source code
├── src/tests/        # All tests
└── docs/             # Documentation
```

### Modular Mode

**Best for:** Large projects with modular architecture

```bash
vibecraft init -r research.md -s stack.md --mode modular
```

**Features:**
- ✅ Module management
- ✅ Explicit dependencies
- ✅ Dependency analysis
- ✅ Integration build
- ✅ Per-module TDD cycles

#### Modular Mode Quick Start

```bash
# 1. Create modules
vibecraft module create database -d "Database layer"
vibecraft module create auth -d "Authentication" --depends-on database
vibecraft module create api -d "REST API" --depends-on auth,database

# 2. List modules
vibecraft module list

# 3. Analyze dependencies
vibecraft integrate analyze

# Output:
# ✓ All dependencies valid!
# Build order:
#   1. database
#   2. auth (depends on: database)
#   3. api (depends on: auth, database)

# 4. Build integration layer
vibecraft integrate build

# 5. Run skills for specific module
vibecraft run implement --phase 1 --module auth
```

**Modular Structure:**
```
project/
├── modules/
│   ├── database/
│   │   ├── .module.json
│   │   ├── src/
│   │   └── tests/
│   ├── auth/
│   │   ├── .module.json
│   │   ├── src/
│   │   └── tests/
│   └── api/
│       ├── .module.json
│       ├── src/
│       └── tests/
├── integration/
│   ├── interfaces.py      # Auto-generated
│   └── connectors/        # Module connectors
└── shared/                # Shared code
```

---

## 📚 Examples

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

### What's the difference between Simple and Modular mode?

| Feature | Simple Mode | Modular Mode |
|---------|-------------|--------------|
| Best for | Small projects | Large projects |
| Structure | Flat `src/` | `modules/` |
| Dependencies | None | Explicit |
| TDD | Single cycle | Per-module |

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Report Bugs

Use GitHub Issues with the `bug` label. Include:
- Vibecraft version
- Python version
- Steps to reproduce
- Expected vs actual behavior

### Suggest Features

Use GitHub Issues with the `enhancement` label. Describe:
- The problem you're solving
- Proposed solution
- Alternative approaches considered

### Submit Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Check code quality: `ruff check vibecraft/`
6. Commit: `git commit -m "Add amazing feature"`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/vibecraft/vibecraft.git
cd vibecraft/vibecraft-framework

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode with test dependencies
pip install -e ".[test]"

# Run tests
pytest tests/ -v

# Check code quality
ruff check vibecraft/
mypy vibecraft/ --ignore-missing-imports
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

## 🙏 Acknowledgments

- Inspired by test-driven development principles
- Built with ❤️ using [Click](https://click.palletsprojects.com/), [Jinja2](https://jinja.palletsprojects.com/), and [Rich](https://rich.readthedocs.io/)
- Thanks to all contributors and users!

---

## 📬 Contact

- **GitHub:** [github.com/vibecraft/vibecraft](https://github.com/vibecraft/vibecraft)
- **PyPI:** [pypi.org/project/vibecraft](https://pypi.org/project/vibecraft)
- **Issues:** [github.com/vibecraft/vibecraft/issues](https://github.com/vibecraft/vibecraft/issues)

---

**Happy Coding! 🚀**
