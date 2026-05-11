# claude-project-template

> Reusable Claude Code base config for any Python / cloud project.
> Clone this once — never rebuild agents, KB, hooks, or SDD workflow from scratch again.

---

## What's Included

| Directory | Contents | Purpose |
|-----------|----------|---------|
| `.claude/agents/` | 40+ specialized agents | Code quality, data engineering, AI/ML, AWS, workflow |
| `.claude/commands/` | 13 slash commands | `/brainstorm`, `/define`, `/design`, `/build`, `/ship`, `/dev`, `/review`, etc. |
| `.claude/hooks/` | 6 automation hooks | Cloud safety, secret detection, ruff auto-fix, stop loop, notifications |
| `.claude/kb/` | 17 KB domains | Pydantic, GCP, Gemini, LangFuse, Terraform, Spark, BigQuery, WhatsApp, and more |
| `.claude/rules/` | 3 rule files | Python style, SDD workflow, multi-cloud safety |
| `.claude/sdd/` | SDD scaffold | Templates, examples, architecture docs — empty features/reports/archive |
| `.claude/dev/` | Dev Loop scaffold | PROMPT templates and examples |

---

## Quick Start

### 1. Copy template to your new project

```bash
# Option A — copy the .claude folder into your existing project
cp -r claude-project-template/.claude /path/to/your-project/
cp claude-project-template/.gitignore /path/to/your-project/

# Option B — clone and rename
git clone https://github.com/Saulo-Porva/claude-project-template your-project
cd your-project
rm -rf .git && git init
```

### 2. Fill in CLAUDE.md

Edit `.claude/CLAUDE.md` — replace all `{placeholders}`:
- `{PROJECT_NAME}` — your project name
- `{DESCRIPTION}` — one-line description
- Architecture diagram
- Tech stack table
- Environment variables

### 3. Customise settings.json (optional)

`.claude/settings.json` is ready to use. Add cloud-specific permissions if needed:

```json
"Bash(gcloud:*)",      // GCP
"Bash(aws:*)",         // AWS
"Bash(az:*)",          // Azure
"Bash(terraform:*)",   // Terraform
```

### 4. Open in Claude Code

```bash
claude .
```

All agents, commands, hooks, and KB load automatically.

---

## Hooks Explained

| Hook | Trigger | Behaviour |
|------|---------|-----------|
| `pre-bash-cloud-safety.js` | Every Bash call | Blocks destructive GCP/AWS/Azure commands + prod targets |
| `pre-bash-secrets.js` | Every Bash call | Blocks commands with hardcoded API keys, tokens, private keys |
| `pre-bash-sqz.js` | Every Bash call | Compresses long Bash output to save Claude context |
| `post-write-ruff.js` | Write/Edit/MultiEdit | Auto-runs `ruff check --fix` + `ruff format` on `.py` files |
| `stop-loop.js` | Claude Stop event | Blocks stop if pytest fails or TODO/FIXME remain in modified files |
| `post-stop-notify.js` | Claude Stop event | Desktop notification (Windows/Mac/Linux) |

---

## SDD Workflow (AgentSpec 4.1)

Five-phase spec-driven development — every feature goes through:

```
/brainstorm → /define → /design → /build → /ship
```

Artifacts live in `.claude/sdd/features/` (active) and `.claude/sdd/archive/` (shipped).

See `.claude/sdd/templates/` for document templates and `.claude/sdd/examples/` for a complete example.

---

## Knowledge Base Domains

| Domain | Best for |
|--------|----------|
| `pydantic` | Data validation, LLM output parsing |
| `gcp` | Cloud Run, Pub/Sub, GCS, Firestore, BigQuery |
| `gemini` | Multimodal LLM, Vertex AI integration |
| `langfuse` | LLMOps observability, cost tracking |
| `terraform` | GCP/AWS/Azure infrastructure as Code |
| `terragrunt` | Multi-environment IaC with DRY config |
| `crewai` | Multi-agent AI orchestration |
| `openrouter` | Unified LLM API gateway + fallback |
| `agents` | ReAct patterns, hook system, agent evaluation |
| `bigquery` | Schema design, queries, streaming inserts |
| `lakeflow` | Databricks DLT pipelines, Delta Lake |
| `medallion` | Bronze/Silver/Gold lakehouse architecture |
| `spark` | PySpark, performance tuning, streaming |
| `whatsapp` | WhatsApp Business API, webhooks, routing |
| `gcp-safety` | GCP destructive operations guide |
| `aws-safety` | AWS destructive operations guide |
| `azure-safety` | Azure destructive operations guide |

---

## Adding a New KB Domain

```bash
/create-kb {domain-name}
```

The `kb-architect` agent will scaffold the full domain structure.

---

## Customising Agents

Each agent is a Markdown file in `.claude/agents/{category}/`. To create a domain-specific agent, add a file following the template in `.claude/agents/_template.md.example`.

---

## What This Template Does NOT Include

- **Project source code** — write your own
- **Infrastructure (Terraform/Terragrunt)** — project-specific
- **CI/CD pipelines** — project-specific (GitHub Actions, Azure DevOps, etc.)
- **Tests** — project-specific
- **Project-specific KB content** — use `/create-kb` to add domains you need

---

## Version

Built from: `hub_whats_app / develop` — May 2026
