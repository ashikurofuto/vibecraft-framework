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
# After installation, restart your terminal and verify:
vibecraft --help
```

</details>

<details>
<summary><b>Option 2 — PowerShell or CMD</b></summary>

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

</details>

<details>
<summary><b>Option 3 — Local Install</b> (per-project, no admin required)</summary>

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

```bash
vibecraft doctor
```

Verifies Python version, required packages, and project structure.

---

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
vibecraft init --research research.md --stack stack.md --agents examples/custom_agents.yaml
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
vibecraft run research
vibecraft run design
vibecraft run plan
vibecraft run implement --phase 1
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

---

### 6️⃣ Continue in a new chat

```bash
vibecraft context                        # copies context.md to clipboard
vibecraft context --skill implement      # context + skill prompt
```

Paste into a new LLM chat — the agent knows exactly where you left off.

---

### 7️⃣ Roll back a skill run

Every `vibecraft run` takes a snapshot before executing, so you can always undo.

```bash
vibecraft snapshots              # list available snapshots
vibecraft rollback               # restore latest snapshot (interactive)
vibecraft rollback 1             # restore second-latest
vibecraft rollback design        # restore most recent 'design' snapshot
```

---

### 8️⃣ Export the project

```bash
vibecraft export                  # creates docs/project_summary.md
vibecraft export --format zip     # creates a portable archive
```

---

## 🤖 Custom Agents

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
