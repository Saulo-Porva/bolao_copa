# Spacing & Layout

## Sistema de Espaçamento — Base 4px

Todo espaçamento segue múltiplos de 4px. Nunca use valores arbitrários como `p-3.5` exceto para atingir touch targets específicos.

```
4px  = gap-1  = espaço micro (ícone ↔ texto inline)
8px  = gap-2  = espaço pequeno (itens de uma mesma linha)
12px = gap-3  = espaço compacto (campos próximos)
16px = gap-4  = espaço padrão (padding de card, entre campos)
24px = gap-6  = espaço entre seções
32px = gap-8  = espaço entre blocos de página
48px = gap-12 = separação de áreas distintas
```

## Layout de Página — Estrutura Padrão

```
┌─────────────────────────────┐
│ Header (sticky, 56px)       │ ← bg-brand text-white
├─────────────────────────────┤
│                             │
│  main.flex-1                │ ← px-4 py-6
│  .max-w-lg.mx-auto.w-full   │ ← container centrado
│                             │
│  ┌─────────────────────┐    │
│  │ h1 (título)         │    │
│  ├─────────────────────┤    │
│  │ Conteúdo principal  │    │
│  └─────────────────────┘    │
│                             │
├─────────────────────────────┤
│ BottomNav (fixed, 64px)     │ ← se aplicável
└─────────────────────────────┘
```

## Thumb Zone — Zonas de Alcance Mobile

Para celular segurado com uma mão (mão direita, polegar):

```
┌──────────┐
│ ✗ Difícil│  ← Canto superior — evitar ações críticas
│          │
│ ✓ Fácil  │  ← Zona central — ações secundárias
│          │
│ ✓✓ Ótimo │  ← Zona inferior — ações primárias aqui
└──────────┘
```

**Implicação para este projeto:**
- Botão "Nova Viagem" deve estar na parte inferior da tela
- BottomNav é preferível a top tabs para motoristas
- Ações destrutivas (Cancelar, Fechar Mês) → confirmar antes de executar, nunca na thumb zone sem confirmação

## Densidade de Layout

### Mobile (motorista em campo)
- Padding de card: `p-4` (16px)
- Gap entre campos de form: `gap-4`
- Altura de input: `py-3.5` (≈52px)
- Itens de lista: `py-4` (≥56px)

### Desktop (admin no escritório)
- Pode usar `p-6` em cards maiores
- `gap-3` entre campos (mais compacto)
- Inputs com `py-2.5` são aceitáveis
- Grids de 2-3 colunas para dashboards

## Safe Areas (iOS/Android)

Para PWAs instaladas, adicionar suporte a safe areas:

```css
/* globals.css */
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom, 16px);
}
```

```tsx
// BottomNav
<nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 pb-[env(safe-area-inset-bottom,16px)]">
```

## Grid Responsivo

```tsx
// Dashboard admin — cards de motoristas
<div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">

// Linha de KPIs (2 por linha em mobile)
<div className="grid grid-cols-2 gap-3">

// Formulário com campo dividido (2 campos na mesma linha)
<div className="grid grid-cols-2 gap-3">
  <div>Peso</div>
  <div>DDT</div>
</div>
```
