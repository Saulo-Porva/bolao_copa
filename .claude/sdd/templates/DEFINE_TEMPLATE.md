# DEFINE: {Feature Name}

> One-sentence description of what we're building

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | {FEATURE_NAME} |
| **Date** | {YYYY-MM-DD} |
| **Author** | {author} |
| **Status** | {Draft / In Progress / Needs Clarification / Ready for Design} |
| **Clarity Score** | {X}/15 |

---

## Problem Statement

{1-2 sentences describing the pain point we're solving. Be specific about who has the problem and what the impact is.}

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| {User 1} | {Their role} | {What frustrates them} |
| {User 2} | {Their role} | {What frustrates them} |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | {Primary goal - non-negotiable for MVP} |
| **MUST** | {Another critical goal} |
| **SHOULD** | {Important but can defer if timeline tight} |
| **COULD** | {Nice-to-have if time permits} |

**Priority Guide:**
- **MUST** = MVP fails without this
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes (must include numbers):

- [ ] {Metric 1: e.g., "Handle 1000 requests per minute"}
- [ ] {Metric 2: e.g., "Achieve 99.9% uptime"}
- [ ] {Metric 3: e.g., "Response time under 200ms"}

---

## Acceptance Tests

> Para cada fluxo principal, definir: happy path, error case e rollback scenario.

| ID | Type | Scenario | Given | When | Then |
|----|------|----------|-------|------|------|
| AT-001 | ✅ Happy Path | {Fluxo principal bem-sucedido} | {Estado inicial} | {Ação do usuário/sistema} | {Resultado esperado} |
| AT-002 | ❌ Error Case | {O que acontece quando falha} | {Estado inicial} | {Ação que causa erro} | {Mensagem/comportamento esperado} |
| AT-003 | ↩ Rollback | {Como o sistema se recupera} | {Estado após falha parcial} | {Trigger de rollback} | {Estado consistente restaurado} |
| AT-004 | 🔲 Edge Case | {Caso limite ou incomum} | {Estado inicial} | {Ação extrema} | {Resultado esperado} |

**Types:**
- ✅ **Happy Path** — fluxo principal sem problemas
- ❌ **Error Case** — entrada inválida, timeout, serviço indisponível
- ↩ **Rollback** — o que restaura consistência quando algo falha a meio caminho
- 🔲 **Edge Case** — volumes extremos, dados vazios, concorrência

**Rollback obrigatório quando a feature:**
- Escreve em múltiplos sistemas (ex: BigQuery + Firestore)
- Modifica estado persistente (ex: session state, schema)
- Faz chamadas externas não-idempotentes (ex: envio de email, Pub/Sub publish)

### Scenarios (OpenSpec)

> Para cada AT acima, escrever o cenário narrativo completo. Mínimo: happy path + error path por fluxo principal.

#### Scenario: {AT-001 — Nome do fluxo principal}

**Given** {estado inicial do sistema — dados presentes, serviços disponíveis}  
**When** {ação concreta do usuário ou evento do sistema}  
**Then** {resultado observável — o que aparece, o que é salvo, o que é publicado}

---

#### Scenario: {AT-002 — Nome do error case}

**Given** {estado inicial, incluindo qual serviço ou dado está ausente/inválido}  
**When** {ação que provoca o erro}  
**Then** {mensagem de erro retornada, estado do sistema após a falha, nenhum dado parcial persiste}

---

> Adicionar `#### Scenario:` para cada AT com rollback (AT-003) ou edge case relevante.
> Scenarios são a "prova executável" do DEFINE — se não conseguir escrever um, o requisito não está claro o suficiente.

---

## Out of Scope

Explicitly NOT included in this feature:

- {Item 1: What we're NOT doing}
- {Item 2: What's deferred to future}
- {Item 3: What's explicitly excluded}

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | {e.g., "Must use existing database schema"} | {How this affects design} |
| Timeline | {e.g., "Must ship by Q1"} | {How this affects scope} |
| Resource | {e.g., "No additional infrastructure budget"} | {How this affects approach} |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | {src/ \| functions/ \| gen/ \| deploy/ \| custom path} | {Why this location} |
| **KB Domains** | {pydantic, gcp, gemini, langfuse, terraform, crewai, openrouter} | {Which patterns to consult} |
| **IaC Impact** | {New resources \| Modify existing \| None \| TBD} | {Terraform/Terragrunt changes needed} |

**Why This Matters:**

- **Location** → Design phase uses correct project structure, prevents misplaced files
- **KB Domains** → Design phase pulls correct patterns from `.claude/kb/`
- **IaC Impact** → Triggers infrastructure planning, avoids "works locally" failures

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | {e.g., "Database can handle expected load"} | {Would need caching layer} | [ ] |
| A-002 | {e.g., "Request volume stays under 1000/hour"} | {Would need rate limiting} | [ ] |
| A-003 | {e.g., "Users have modern browsers"} | {Would need polyfills for legacy support} | [ ] |

**Note:** Validate critical assumptions before DESIGN phase. Unvalidated assumptions become risks.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | {0-3} | {Why this score} |
| Users | {0-3} | {Why this score} |
| Goals | {0-3} | {Why this score} |
| Success | {0-3} | {Why this score} |
| Scope | {0-3} | {Why this score} |
| **Total** | **{X}/15** | |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

> Perguntas sem resposta que podem invalidar o DESIGN se respondidas errado. Resolver antes de avançar.

| ID | Priority | Question | Who can answer | Status |
|----|----------|----------|---------------|--------|
| Q-001 | 🔴 Blocker | {Pergunta que bloqueia o DESIGN se não respondida} | {Stakeholder / Tech Lead / PO} | Open |
| Q-002 | 🟡 High | {Pergunta importante mas não bloqueante} | {Quem sabe responder} | Open |
| Q-003 | 🟢 Low | {Dúvida que pode ser respondida durante o build} | {Quem sabe responder} | Deferred |

**Priority guide:**
- 🔴 **Blocker** — DESIGN não pode começar sem resposta
- 🟡 **High** — responder antes de iniciar o BUILD
- 🟢 **Low** — pode ser respondida durante o BUILD sem risco

**Status options:** Open · In Progress · Answered · Deferred · N/A

*Se não há perguntas abertas: substituir tabela por "None — ready for Design."*

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | define-agent | Initial version |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_{FEATURE_NAME}.md`
