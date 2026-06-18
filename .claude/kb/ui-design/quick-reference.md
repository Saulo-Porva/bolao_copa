# UI Design — Quick Reference

## Touch Targets

| Elemento | Altura mínima | Tailwind |
|---------|--------------|---------|
| Botão primário | 52px | `py-3.5` + `text-base` |
| Input de formulário | 52px | `py-3.5` |
| Item de lista/link | 56px | `py-4` |
| Badge/chip (não interativo) | 28px | `py-1` |
| Botão de ícone | 48×48px | `p-3 w-12 h-12` |

## Paleta de Cor — Tokens @theme

```css
/* Em globals.css dentro de @theme */
--color-brand:       oklch(42% 0.18 25);   /* #C0392B — ações primárias */
--color-brand-light: oklch(95% 0.05 25);   /* tint suave para fundos */
--color-success:     oklch(52% 0.17 145);  /* status aberto/ok */
--color-warning:     oklch(72% 0.17 65);   /* atenção */
--color-neutral-900: oklch(15% 0.01 0);    /* texto principal */
--color-neutral-500: oklch(55% 0.01 0);    /* texto secundário */
--color-neutral-200: oklch(88% 0.01 0);    /* bordas */
--color-neutral-50:  oklch(97% 0.005 0);   /* fundo de card */
```

## Escala Tipográfica

| Tailwind | px | Uso |
|----------|----|-----|
| `text-2xl font-bold` | 24 | Título de página (h1) |
| `text-xl font-semibold` | 20 | Seção / nome do motorista |
| `text-base font-medium` | 16 | Labels, nav items |
| `text-base` | 16 | Corpo — **mínimo em campo** |
| `text-sm` | 14 | Metadados secundários |
| `text-xs` | 12 | Badges — nunca texto principal |

## Espaçamento — Base 4px

| Token | px | Uso |
|-------|----|-----|
| `gap-1` / `p-1` | 4 | Espaço entre ícone e texto |
| `gap-2` / `p-2` | 8 | Items inline |
| `gap-4` / `p-4` | 16 | Padding interno de card |
| `gap-6` / `p-6` | 24 | Entre seções |
| `gap-8` / `p-8` | 32 | Entre blocos de página |

## Sombras

| Classe | Uso |
|--------|-----|
| `shadow-sm` | Card padrão |
| `shadow-md` | Card em hover / ativo |
| `shadow-lg` | Bottom sheet, modal |

## Estados — Bordas e Rings

```
default:  border-gray-200
focus:    border-brand-red ring-2 ring-brand-red/20 outline-none
error:    border-red-400 bg-red-50
disabled: opacity-50 cursor-not-allowed pointer-events-none
success:  border-green-400 bg-green-50
```

## Contraste WCAG — Checklist

| Combinação | Ratio | Status |
|------------|-------|--------|
| `white` em `#C0392B` (brand-red) | 5.1:1 | ✓ AA |
| `gray-900` em `white` | 16.9:1 | ✓ AAA |
| `gray-500` em `white` | 4.6:1 | ✓ AA |
| `gray-400` em `white` | 3.0:1 | ✗ Falha |
| `red-200` em `brand-red` | 1.8:1 | ✗ Falha atual no botão "Sair" |

## Raios de Borda — Padrão do Projeto

| Elemento | Classe |
|---------|--------|
| Cards, containers | `rounded-2xl` |
| Botões, inputs, selects | `rounded-xl` |
| Badges, status pills | `rounded-full` |
| Bottom sheet (borda superior) | `rounded-t-2xl` |
