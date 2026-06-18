# KB: UX (User Experience)

> Padrões de experiência do usuário para PWAs móveis — com foco em trabalhadores de campo.

## Contexto do Projeto

**App:** PR Trasporti — Rapportini  
**Motoristas:** 12 usuários, celular em campo, podem usar luvas, luz solar direta, vibração do caminhão  
**Admins:** 2 usuários, desktop, escritório  
**Tipo de uso:** Tarefas operacionais de registro (iniciar/fechar jornadas, registrar viagens)  
**Criticidade:** Alta — erros de registro impactam folha de pagamento e compliance

## Quando consultar este KB

- Projetando ou revisando fluxos de navegação
- Identificando friction points em formulários ou processos
- Validando acessibilidade e usabilidade
- Projetando estados de erro/sucesso/loading
- Diferenciando a experiência motorista vs admin

## Navegação

### Conceitos
| Arquivo | Conteúdo |
|---------|----------|
| [usability-principles.md](concepts/usability-principles.md) | 10 heurísticas de Nielsen, lei de Fitts, Hick |
| [mobile-ux.md](concepts/mobile-ux.md) | Thumb zones, gestos, estados offline, PWA |
| [information-architecture.md](concepts/information-architecture.md) | Navegação, progressive disclosure, mental models |
| [user-flows.md](concepts/user-flows.md) | Happy path, error paths, task completion |
| [accessibility.md](concepts/accessibility.md) | WCAG 2.1 AA, ARIA, keyboard nav |

### Padrões
| Arquivo | Conteúdo |
|---------|----------|
| [field-worker-ux.md](patterns/field-worker-ux.md) | UX para motoristas: urgência, stress cognitivo |
| [form-ux.md](patterns/form-ux.md) | Progressive disclosure, smart defaults, validação |
| [feedback-patterns.md](patterns/feedback-patterns.md) | Toasts, skeletons, empty states, error recovery |
| [admin-vs-field-ux.md](patterns/admin-vs-field-ux.md) | Densidade de informação por perfil de usuário |

## Princípios Inegociáveis para este Projeto

1. **Zero ambiguidade em ações críticas:** Fechar mês e cancelar viagem sempre requerem confirmação explícita
2. **Feedback em < 200ms:** O motorista não pode ficar olhando para uma tela que parece travada
3. **Fluxo principal em ≤ 3 taps:** Da tela inicial até registrar uma viagem, no máximo 3 taps
4. **Erros com recuperação clara:** Nunca mostrar mensagem de erro sem indicar o que fazer
5. **Offline não interrompe o trabalho:** Dados de leitura disponíveis offline; erros de rede comunicados claramente
