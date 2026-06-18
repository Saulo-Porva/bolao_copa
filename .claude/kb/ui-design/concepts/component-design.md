# Component Design

## Anatomia de um Componente

```
Root (container com classes de layout)
├── Content (dados/texto)
├── State indicator (badge, ícone)
└── Action (botão, link)
```

## Os 6 Estados que todo componente interativo deve suportar

| Estado | Visual | Tailwind |
|--------|--------|---------|
| `default` | Borda cinza, fundo branco | `border-gray-200 bg-white` |
| `hover` | Borda mais escura, leve elevação | `hover:border-gray-400 hover:shadow-md` |
| `focus` | Borda brand, ring de foco | `focus:border-brand-red focus:ring-2 focus:ring-brand-red/20 focus:outline-none` |
| `active` | Fundo levemente escurecido | `active:bg-gray-50` |
| `error` | Borda vermelha, fundo tint | `border-red-400 bg-red-50` |
| `disabled` | Opacidade reduzida | `disabled:opacity-50 disabled:cursor-not-allowed` |

## Botão — Variantes

```tsx
// Primário — CTA principal da tela
<button className="w-full bg-brand-red text-white py-3.5 rounded-xl font-semibold text-base disabled:opacity-50 active:brightness-90 transition-all">
  Nova Viagem
</button>

// Secundário — ação alternativa
<button className="w-full bg-gray-100 text-gray-700 py-3.5 rounded-xl font-medium text-base hover:bg-gray-200 transition-colors">
  Ver Detalhes
</button>

// Ghost — navegação ou ação de baixo destaque
<button className="w-full border border-gray-200 text-gray-700 py-3.5 rounded-xl font-medium text-base hover:border-gray-400 transition-colors">
  Cancelar
</button>

// Destrutivo — fechar mês, cancelar viagem
<button className="w-full bg-red-600 text-white py-3.5 rounded-xl font-semibold text-base disabled:opacity-50">
  Fechar Mês
</button>
```

## Input — Estados Visuais

```tsx
// Base do input com todos os estados
<input className="
  w-full
  border border-gray-200 rounded-xl
  px-4 py-3.5
  text-base text-gray-900
  placeholder:text-gray-400
  bg-white
  focus:border-brand-red focus:ring-2 focus:ring-brand-red/20 focus:outline-none
  disabled:opacity-50 disabled:bg-gray-50 disabled:cursor-not-allowed
  aria-[invalid=true]:border-red-400 aria-[invalid=true]:bg-red-50
  transition-colors
" />
```

## Card — Variantes

```tsx
// Card padrão (informativo)
<div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">

// Card interativo (clickável)
<div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 hover:shadow-md hover:border-gray-200 transition-all cursor-pointer">

// Card de destaque/ativo
<div className="bg-brand-red/5 rounded-2xl p-4 border border-brand-red/20">

// Card de ação — botão grande com ícone
<button className="flex items-center gap-3 bg-brand-red text-white p-4 rounded-2xl shadow-sm active:brightness-90 w-full">
  <span className="text-2xl">+</span>
  <div className="text-left">
    <p className="font-bold text-base">Nova Viagem</p>
    <p className="text-xs text-red-200">Registrar viagem de hoje</p>
  </div>
</button>
```

## Loading State — Padrões

```tsx
// Skeleton (preferido — não causa layout shift)
<div className="animate-pulse">
  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
  <div className="h-4 bg-gray-200 rounded w-1/2" />
</div>

// Spinner inline em botão
<button disabled className="...">
  <svg className="animate-spin w-4 h-4 mr-2" .../>
  Salvando...
</button>

// Nunca: texto plano "Carregando..." sem indicador visual
```

## Empty State

```tsx
// Empty state com ação clara
<div className="text-center py-12 px-4">
  <div className="text-4xl mb-3">🚛</div>
  <p className="font-semibold text-gray-900 mb-1">Nenhum mês aberto</p>
  <p className="text-sm text-gray-500 mb-6">Inicie o mês para começar a registrar suas viagens</p>
  <Link href="..." className="inline-flex items-center gap-2 bg-brand-red text-white px-6 py-3.5 rounded-xl font-semibold text-base">
    Iniciar Mês de {mesLabel}
  </Link>
</div>
```
