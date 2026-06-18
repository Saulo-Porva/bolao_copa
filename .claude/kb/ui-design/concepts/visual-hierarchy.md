# Visual Hierarchy

## As 5 Dimensões de Hierarquia

Em ordem de impacto visual numa interface mobile:

| Dimensão | Como usar | Exemplo |
|---------|-----------|---------|
| **Tamanho** | Maior = mais importante | h1 24px vs legenda 12px |
| **Peso** | Bold = primário | `font-bold` no valor, `font-normal` no label |
| **Cor** | Saturado = destaque | `brand-red` para CTA, `gray-500` para secundário |
| **Espaço** | Mais ar = mais importante | `mb-6` após título, `mb-2` após label |
| **Posição** | Topo/centro = lido primeiro | Saudação no topo, ação primária destacada |

## Princípio do Foco Único

**Cada tela deve ter uma e somente uma ação visual primária.**

```tsx
// ✓ Correto — um CTA claro
<div>
  <InfoCard />          {/* conteúdo informativo */}
  <PrimaryButton>       {/* UMA ação destacada */}
    Nova Viagem
  </PrimaryButton>
</div>

// ✗ Errado — dois CTAs disputando atenção
<div>
  <PrimaryButton>Nova Viagem</PrimaryButton>
  <PrimaryButton>Fechar Mês</PrimaryButton>  {/* mesmo peso visual */}
</div>
```

## Padrão de Leitura Mobile — Z-Pattern

Em telas mobile com cards, o olho segue um Z:

```
[Logo/Nome]  →  [Status/Badge]    ← linha 1: identidade
      ↘
[Info secundária]                 ← diagonal
      ↘
[CTA Principal]                   ← linha 3: ação
```

**Aplicação no dashboard do motorista:**
- Topo: saudação + data (contexto)
- Meio: card do mês com status badge
- Base: botão "Nova Viagem" em destaque

## Hierarquia de Texto em Cards

```tsx
// Estrutura ideal de card com hierarquia clara
<div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
  {/* Nível 1 — título do card */}
  <p className="text-xs text-gray-500 uppercase tracking-wide">Mês atual</p>

  {/* Nível 2 — valor principal */}
  <p className="text-xl font-bold text-gray-900">05/2025</p>

  {/* Nível 3 — dados secundários */}
  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 mt-2">
    <span>KM: <strong className="text-gray-900">12.450</strong></span>
    <span>Caminhão: <strong className="text-gray-900">GA993AV</strong></span>
  </div>

  {/* Ação */}
  <button className="mt-4 w-full ...">Ver Detalhes</button>
</div>
```

## Agrupamento por Proximidade

Campos relacionados devem estar mais próximos entre si do que de outros grupos:

```tsx
// ✓ Agrupamento claro
<div className="flex flex-col gap-6">
  {/* Grupo 1: dados da carga */}
  <div className="flex flex-col gap-3">
    <Field label="Origem" />
    <Field label="Destino" />
  </div>

  {/* Grupo 2: dados administrativos */}
  <div className="flex flex-col gap-3">
    <Field label="DDT" />
    <Field label="Peso" />
  </div>
</div>
```

## Contraste de Informação — Foreground/Background

| Tipo de conteúdo | Peso visual | Classe |
|-----------------|------------|--------|
| Dado principal (KM, placa) | Alto | `text-gray-900 font-bold` |
| Dado secundário (data, label) | Médio | `text-gray-700` |
| Metadado/contexto | Baixo | `text-gray-500` |
| Placeholder/hint | Muito baixo | `placeholder-gray-400` |
