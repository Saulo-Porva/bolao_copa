# KB: UI Design

> Padrões de design visual para interfaces web — com foco em PWA mobile-first para trabalhadores de campo.

## Contexto do Projeto

**App:** PR Trasporti — Rapportini  
**Usuários primários:** Motoristas de caminhão (mobile, campo, luvas)  
**Usuários secundários:** Admins (desktop, escritório)  
**Stack:** Next.js 15, Tailwind CSS v4, Vercel  
**Cor de marca:** `#C0392B` (vermelho PR Trasporti)

## Quando consultar este KB

- Criando ou refinando componentes visuais (cards, forms, badges, botões)
- Definindo tokens de design (cores, tipografia, espaçamento, sombras)
- Revisando inconsistências visuais entre telas
- Implementando estados de UI (loading, error, empty, success)
- Garantindo acessibilidade visual (contraste, tamanho de alvo touch)

## Navegação

### Conceitos
| Arquivo | Conteúdo |
|---------|----------|
| [color-theory.md](concepts/color-theory.md) | Paleta semântica, WCAG, tokens de cor |
| [typography.md](concepts/typography.md) | Escala tipográfica, legibilidade mobile |
| [spacing-layout.md](concepts/spacing-layout.md) | Grid, 8px base, thumb zones |
| [visual-hierarchy.md](concepts/visual-hierarchy.md) | Peso, tamanho, Z-pattern, foco único |
| [component-design.md](concepts/component-design.md) | Estados, variantes, microinterações |

### Padrões
| Arquivo | Conteúdo |
|---------|----------|
| [mobile-first-ui.md](patterns/mobile-first-ui.md) | AppShell, BottomNav, touch targets |
| [dashboard-design.md](patterns/dashboard-design.md) | StatusCard, KpiGrid, timeline |
| [form-design.md](patterns/form-design.md) | Inputs, selects, validação inline |
| [tailwind-design-system.md](patterns/tailwind-design-system.md) | @theme tokens, cva, cn() utility |

## Princípios Inegociáveis para este Projeto

1. **Touch target mínimo:** 48px de altura para qualquer elemento interativo
2. **Contraste outdoor:** Mínimo 4.5:1 para texto, preferir 7:1 para uso sob sol
3. **Feedback imediato:** Toda ação do motorista deve ter resposta visual em < 100ms
4. **Foco único por tela:** Uma ação principal visualmente destacada por página
5. **Consistência de raio:** `rounded-xl` (12px) para botões e inputs; `rounded-2xl` para cards
