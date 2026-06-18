# Typography — Interfaces Web Mobile

## Princípio Fundamental

**Nunca use `text-xs` para texto lido em campo.** Motoristas leem em movimento, com vibração, às vezes com luvas. `text-base` (16px) é o mínimo absoluto para qualquer informação operacional.

## Escala Tipográfica do Projeto

```
text-2xl  (24px) — Títulos de página (h1), usados com font-bold
text-xl   (20px) — Subtítulos, nome do motorista no dashboard
text-lg   (18px) — Textos de destaque, valores numéricos importantes
text-base (16px) — Corpo, labels de input, texto de navegação [MÍNIMO]
text-sm   (14px) — Metadados (datas, horários em contexto secundário)
text-xs   (12px) — Badges de status apenas (não texto de leitura)
```

## Hierarquia de Peso

| Peso | Tailwind | Uso |
|------|----------|-----|
| 700 | `font-bold` | Títulos h1, valores numéricos críticos |
| 600 | `font-semibold` | Subtítulos, labels de seção |
| 500 | `font-medium` | Labels de campo, botões, nav |
| 400 | `font-normal` | Texto de corpo, placeholders |

## Font Family

**Padrão atual do projeto:** `system-ui, -apple-system, sans-serif`

Para melhor legibilidade em campo, considerar Inter via `next/font`:

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'], display: 'swap' });
```

**Vantagens do Inter para este app:**
- Projetado para legibilidade em telas pequenas
- Dígitos tabelados (`font-variant-numeric: tabular-nums`) — importante para KM e pesos
- Excelente legibilidade em tamanhos 14-16px

## Números e Dados Operacionais

Para KM, pesos, horários — use `tabular-nums` para evitar "saltos" ao atualizar:

```tsx
<span className="font-mono text-lg font-bold tabular-nums">
  {km.toLocaleString('it-IT')}
</span>
```

## Line Height

| Contexto | `leading-` | Por quê |
|---------|-----------|---------|
| Títulos | `leading-tight` (1.25) | Títulos curtos, mais compacto |
| Corpo/labels | `leading-normal` (1.5) | Legibilidade padrão |
| Texto em card | `leading-relaxed` (1.625) | Mais fácil de ler rápido |

## Truncation

Para textos longos em espaços limitados (nome de cliente, rota):

```tsx
// Uma linha
<p className="truncate text-sm text-gray-600">{cliente.nome}</p>

// Duas linhas
<p className="line-clamp-2 text-sm text-gray-600">{descricao}</p>
```

## Anti-patterns

| Problema | Impacto | Correção |
|---------|---------|---------|
| `text-xs` para labels de campo | Ilegível em sol/vibração | `text-base` |
| `font-thin` ou `font-light` | Muito fino em telas mobile de baixa qualidade | `font-normal` mínimo |
| Itálico em campo | Difícil de ler em movimento | Nunca usar itálico para texto operacional |
| `letter-spacing` negativo | Reduz legibilidade | Manter padrão ou adicionar levemente |
