# Tailwind v4 Design System

## globals.css — Tokens Completos

```css
@import "tailwindcss";

@theme {
  /* Brand */
  --color-brand: oklch(42% 0.18 25);          /* #C0392B */
  --color-brand-light: oklch(95% 0.05 25);    /* tint suave */

  /* Status semântico */
  --color-success: oklch(52% 0.17 145);
  --color-warning: oklch(72% 0.17 65);
  --color-danger: oklch(42% 0.20 25);

  /* Tipografia */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;

  /* Raios */
  --radius-card: 1rem;    /* rounded-2xl */
  --radius-input: 0.75rem; /* rounded-xl */

  /* Sombras customizadas */
  --shadow-card: 0 1px 3px 0 rgb(0 0 0 / 0.07), 0 1px 2px -1px rgb(0 0 0 / 0.04);
}

body {
  font-family: var(--font-sans);
  -webkit-tap-highlight-color: transparent;
  background-color: oklch(97% 0.005 0); /* gray-50 como fundo padrão */
}

/* Safe area para PWA */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 1rem);
}
```

## cn() — Utility de Class Merging

```ts
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

Instalar: `npm install clsx tailwind-merge`

## cva — Component Variant Authority

```ts
// components/ui/button.tsx
import { cva, type VariantProps } from 'class-variance-authority';

export const buttonVariants = cva(
  // base — aplicado a todas as variantes
  "inline-flex items-center justify-center gap-2 font-semibold text-base rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed active:brightness-90",
  {
    variants: {
      variant: {
        primary:     "bg-brand text-white shadow-sm",
        secondary:   "bg-gray-100 text-gray-700 hover:bg-gray-200",
        ghost:       "border border-gray-200 text-gray-700 hover:border-gray-400",
        destructive: "bg-red-600 text-white shadow-sm",
      },
      size: {
        sm:   "py-2.5 px-4 text-sm",
        md:   "py-3.5 px-6",
        lg:   "py-4 px-8 text-lg",
        icon: "p-3 w-12 h-12",
      },
      fullWidth: {
        true: "w-full",
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, fullWidth, ...props }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, fullWidth }), className)}
      {...props}
    />
  );
}
```

Instalar: `npm install class-variance-authority`

## Convenções de Ordem de Classes Tailwind

Seguir a ordem: Layout → Flex/Grid → Espaçamento → Tamanho → Tipografia → Cor → Borda → Efeito → Estado

```tsx
// ✓ Ordem correta
<div className="flex flex-col gap-4 p-4 w-full text-base text-gray-900 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-shadow">

// ✗ Ordem aleatória (dificulta leitura)
<div className="bg-white hover:shadow-md text-base border-gray-200 flex p-4 shadow-sm text-gray-900 gap-4 w-full rounded-xl border transition-shadow flex-col">
```

## Componentes Base Recomendados

Para construir um design system consistente neste projeto, criar:

```
src/components/ui/
├── Button.tsx      — buttonVariants com cva
├── Input.tsx       — input com todos os estados
├── Field.tsx       — wrapper label + input + error
├── Card.tsx        — variantes de card
├── Badge.tsx       — StatusBadge com variantes
├── Skeleton.tsx    — skeleton screen pieces
└── index.ts        — re-exports
```

## Animações Utilitárias

```css
/* Adicionar em globals.css */
@keyframes slide-in-from-top {
  from { transform: translateY(-100%); opacity: 0; }
  to   { transform: translateY(0);     opacity: 1; }
}

.animate-in { animation-fill-mode: both; }
.slide-in-from-top-2 { animation-name: slide-in-from-top; animation-duration: 200ms; }
```
