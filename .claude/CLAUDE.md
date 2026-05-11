# {PROJECT_NAME}

> {One-line description of what this project does}

---

## Project Context

**Business Problem:** {Describe the problem being solved}

**Solution:** {Describe the technical solution}

**Stack:** {Primary languages, frameworks, cloud provider}

---

## Architecture Overview

```text
{ASCII diagram of the system — replace this block}

Input → Process → Output
```

| Layer | Technology | Purpose |
|-------|------------|---------|
| Compute | {e.g. Cloud Run / Lambda / Docker} | {purpose} |
| Storage | {e.g. GCS / S3 / PostgreSQL} | {purpose} |
| Messaging | {e.g. Pub/Sub / SQS / Kafka} | {purpose} |
| LLM | {e.g. Gemini / OpenAI / Anthropic} | {purpose} |

---

## Project Structure

```text
{project-root}/
├── src/                    # Application source code
├── tests/                  # Test suites
├── infra/                  # Infrastructure as Code
├── .claude/                # Claude Code ecosystem (this directory)
│   ├── agents/             # 40+ specialized agents
│   ├── commands/           # Slash commands
│   ├── hooks/              # Security + automation hooks
│   ├── kb/                 # Knowledge Base (17 domains)
│   ├── rules/              # Coding + workflow rules
│   └── sdd/                # Spec-Driven Development artifacts
└── pyproject.toml
```

---

## Development Workflows

### AgentSpec 4.1 — Spec-Driven Development (SDD)

```text
/brainstorm → /define → /design → /build → /ship
```

| Command | Phase | Purpose |
|---------|-------|---------|
| `/brainstorm` | 0 | Explore ideas through dialogue (optional) |
| `/define` | 1 | Capture and validate requirements |
| `/design` | 2 | Create architecture and specification |
| `/build` | 3 | Execute implementation with verification |
| `/ship` | 4 | Archive with lessons learned |
| `/iterate` | Any | Update documents when requirements change |

**Artifacts:** `.claude/sdd/features/` → `.claude/sdd/archive/`

### Dev Loop — Level 2 Agentic Development

```bash
/dev "I want to build a date parser utility"
/dev tasks/PROMPT_DATE_PARSER.md
/dev tasks/PROMPT_DATE_PARSER.md --resume
```

Use for: KB building, prototypes, utilities, single-file features.

---

## Available Agents

| Category | Agents | Use When |
|----------|--------|----------|
| **Workflow** | brainstorm, define, design, build, ship, iterate | SDD feature development |
| **Code Quality** | code-reviewer, code-cleaner, python-developer, test-generator, dual-reviewer | Code review and improvement |
| **AI/ML** | llm-specialist, genai-architect, ai-prompt-specialist, ai-data-engineer | LLM prompts, AI systems |
| **Data Engineering** | spark-*, lakeflow-*, medallion-architect | Spark, Databricks, Medallion |
| **AWS** | aws-deployer, lambda-builder, aws-lambda-architect, ci-cd-specialist | AWS deployments |
| **Communication** | adaptive-explainer, meeting-analyst, the-planner | Documentation, planning |
| **Exploration** | codebase-explorer, kb-architect | Codebase exploration, KB creation |
| **Dev** | prompt-crafter, dev-loop-executor | Dev Loop workflow |

---

## Commands

| Command | Purpose |
|---------|---------|
| `/brainstorm` | Explore ideas through collaborative dialogue |
| `/define` | Capture and validate requirements |
| `/design` | Create technical architecture |
| `/build` | Execute implementation |
| `/ship` | Archive completed features |
| `/iterate` | Update documents mid-stream |
| `/dev` | Dev Loop for structured iteration |
| `/create-kb` | Create knowledge base domains |
| `/review` | Code review workflow |
| `/create-pr` | Create pull requests |
| `/memory` | Save session insights |
| `/sync-context` | Update CLAUDE.md with project context |
| `/readme-maker` | Generate comprehensive README |

---

## Knowledge Base (17 domains)

| Domain | Purpose |
|--------|---------|
| **pydantic** | Data validation, Pydantic v2 patterns |
| **gcp** | GCP serverless — Cloud Run, Pub/Sub, GCS, BigQuery |
| **gemini** | Gemini multimodal LLM, Vertex AI |
| **langfuse** | LLMOps observability |
| **terraform** | Infrastructure as Code |
| **terragrunt** | Multi-environment IaC orchestration |
| **crewai** | Multi-agent AI orchestration |
| **openrouter** | Unified LLM API gateway / fallback |
| **agents** | LLM agent design patterns (ReAct, hooks, eval) |
| **bigquery** | Google BigQuery — schema, queries, streaming |
| **lakeflow** | Databricks Lakeflow / DLT pipelines |
| **medallion** | Medallion architecture Bronze/Silver/Gold |
| **spark** | Apache Spark / PySpark |
| **whatsapp** | WhatsApp Business API (Meta) |
| **gcp-safety** | GCP destructive ops — what to block |
| **aws-safety** | AWS destructive ops — what to block |
| **azure-safety** | Azure destructive ops — what to block |

---

## Hooks (Active)

| Hook | Trigger | Purpose |
|------|---------|---------|
| `pre-bash-cloud-safety.js` | Bash | Blocks destructive GCP + AWS + Azure commands |
| `pre-bash-secrets.js` | Bash | Detects hardcoded secrets in commands |
| `pre-bash-sqz.js` | Bash | Compresses Bash output for Claude context |
| `post-write-ruff.js` | Write/Edit | Auto-runs ruff lint+format on Python files |
| `stop-loop.js` | Stop | Blocks stop if tests fail or TODOs remain |
| `post-stop-notify.js` | Stop | Desktop notification when Claude finishes |

---

## Coding Standards

### Python 3.11+

- **Linter/Formatter:** Ruff (line-length 100, select E/F/I/UP/B/SIM)
- **Validation:** Pydantic v2 for all data models
- **Testing:** pytest with `-v --tb=short`
- **Type Hints:** Required on all function signatures
- **Package Manager:** pyproject.toml with hatchling

### Rules

- `rules/python-style.md` — Python coding standards
- `rules/sdd-workflow.md` — SDD phase rules and artifact requirements
- `rules/cloud-safety.md` — Cloud safety and deployment patterns

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `{ENV_VAR_1}` | {purpose} |
| `{ENV_VAR_2}` | {purpose} |

---

## Getting Help

- **SDD Workflow:** `.claude/sdd/_index.md`
- **SDD Templates:** `.claude/sdd/templates/`
- **SDD Examples:** `.claude/sdd/examples/`
- **Dev Loop:** `.claude/dev/_index.md`
- **Agents:** `.claude/agents/`
- **KB Index:** `.claude/kb/_index.yaml`

---

## Version History

| Date | Changes |
|------|---------|
| {YYYY-MM-DD} | Initial setup from claude-project-template |
