# Color Theory — Interfaces Web

## Papéis Semânticos de Cor

Toda cor numa interface deve ter um papel funcional, não apenas estético:

| Papel | Cor | Hex | Uso |
|-------|-----|-----|-----|
| **Brand / Primary** | Vermelho PR | `#C0392B` | Botões primários, header, CTAs |
| **Success** | Verde | `#2E7D32` | Status "aberto", confirmações |
| **Warning** | Âmbar | `#F57F17` | Alertas não críticos |
| **Danger** | Vermelho claro | `#C62828` | Erros, cancelamentos |
| **Neutral** | Cinza | escala gray | Texto, bordas, fundos |
| **Surface** | Branco/Off-white | `#FFFFFF` / `#F9FAFB` | Fundo de cards e página |

## Contraste WCAG 2.1

| Nível | Ratio | Texto normal | Texto grande (18px+) |
|-------|-------|-------------|---------------------|
| **AA** | 4.5:1 | Mínimo para uso indoor | 3:1 |
| **AAA** | 7:1 | Recomendado para campo | 4.5:1 |

**Para este projeto (uso outdoor/sol direto):** mínimo AAA (7:1) para texto em ações críticas.

### Verificação rápida da paleta atual

```
brand-red (#C0392B) como fundo:
  - text-white: 5.1:1  → AA ✓ (usar sempre)
  - text-red-100: 3.4:1 → Falha ✗
  - text-red-200: 1.8:1 → Falha ✗ (bug atual no "Sair")

white como fundo:
  - text-gray-900: 16.9:1 → AAA ✓
  - text-gray-700: 9.7:1  → AAA ✓
  - text-gray-500: 4.6:1  → AA ✓
  - text-gray-400: 3.0:1  → Falha ✗ (não usar para texto)
```

## Psicologia de Cor para Campo

**Vermelho (`brand-red`):** Ação, urgência, identidade. Reserve para CTAs primários e confirmações de início de jornada. Não usar para erros (confunde com a marca).

**Verde:** Confirmação positiva. Status "aberto" transmite que o trabalho está em andamento. Tranquiliza o motorista de que o registro está ativo.

**Cinza:** Neutro, fechado, arquivado. Status "fechado" em cinza comunica que o período foi encerrado sem urgência.

**Âmbar/Amarelo:** Atenção sem criticidade. Para alertas de prazo ou dados incompletos. Evitar puro amarelo — baixo contraste.

## Implementação com Tailwind v4

```css
/* globals.css */
@import "tailwindcss";

@theme {
  --color-brand: oklch(42% 0.18 25);
  --color-brand-light: oklch(95% 0.05 25);
  --color-success: oklch(52% 0.17 145);
  --color-warning: oklch(72% 0.17 65);
}
```

```tsx
// Uso em componentes
<button className="bg-brand text-white">  {/* brand-red */}
<div className="bg-success/10 text-success">  {/* success tint */}
```

## Erros Comuns a Evitar

| Anti-pattern | Problema | Correção |
|---|---|---|
| Texto claro em fundo colorido sem checar ratio | Ilegível no sol | Sempre verificar contraste |
| Usar vermelho para erros E para brand | Ambiguidade semântica | Usar `red-600/700` para erros, `brand` para ações |
| Gradientes em botões primários | Complexidade desnecessária, pode reduzir contraste | Cor sólida sempre |
| Muitas cores de destaque na mesma tela | Dispersão visual | Máximo 2 cores de destaque por tela |
