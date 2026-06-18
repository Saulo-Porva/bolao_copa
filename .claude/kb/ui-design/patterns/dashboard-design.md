# Dashboard Design Patterns

## Dashboard do Motorista — Anatomia

```
┌────────────────────────────┐
│ Saudação + data hoje       │  ← contexto pessoal + temporal
├────────────────────────────┤
│ Card: Mês Atual            │  ← estado principal do trabalho
│  [status badge]  05/2025   │
│  KM: 12.450  Caminhão: GA  │
│  [Ver Mês Completo ↗]      │
├────────────────────────────┤
│ [+ Nova Viagem]            │  ← CTA principal (só se mês aberto)
└────────────────────────────┘
```

## StatusHeroCard — Card de Mês com Destaque

```tsx
export function MesStatusCard({ mes }: { mes: Mes }) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
      {/* Header do card */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Mês atual</p>
          <p className="text-xl font-bold text-gray-900">
            {String(mes.mes).padStart(2, '0')}/{mes.ano}
          </p>
        </div>
        <StatusBadge status={mes.status} />
      </div>

      {/* KPIs em grid 2 colunas */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <KpiItem label="KM Inicial" value={mes.km_inicial?.toLocaleString('it-IT') ?? '—'} />
        <KpiItem label="Caminhão" value={mes.caminhao?.placa ?? '—'} />
      </div>

      {/* Ação */}
      <Link
        href={`/motorista/mes/${mes.id}`}
        className="block w-full text-center bg-gray-100 text-gray-700 py-3 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
      >
        Ver Mês Completo
      </Link>
    </div>
  );
}

function KpiItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-xl p-3">
      <p className="text-xs text-gray-500 mb-0.5">{label}</p>
      <p className="text-base font-semibold text-gray-900 truncate">{value}</p>
    </div>
  );
}
```

## CTA Card — Botão de Ação Principal Grande

```tsx
// Mais impactante que um botão comum — destaca a ação principal
<Link
  href={`/motorista/viagem/nova?mesId=${mes.id}`}
  className="flex items-center gap-4 bg-brand-red text-white p-4 rounded-2xl shadow-md active:brightness-90 transition-all"
>
  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center shrink-0">
    <PlusIcon className="w-6 h-6" />
  </div>
  <div>
    <p className="font-bold text-base">Nova Viagem</p>
    <p className="text-sm text-red-100">Registrar viagem de hoje</p>
  </div>
  <ChevronRightIcon className="w-5 h-5 ml-auto text-red-200" />
</Link>
```

## Dashboard Admin — Grid de Motoristas

```tsx
// Cards de motoristas com status atual
export function MotoristasGrid({ motoristas, statusMap }: Props) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {motoristas.map((m) => {
        const mes = statusMap[m.id];
        return (
          <Link
            key={m.id}
            href={`/admin/motoristas/${m.id}`}
            className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md border border-gray-100 hover:border-gray-200 transition-all"
          >
            {/* Row 1: nome + status */}
            <div className="flex items-start justify-between mb-2">
              <p className="font-semibold text-base text-gray-900 leading-tight">{m.nome}</p>
              {mes
                ? <StatusBadge status={mes.status} />
                : <span className="text-xs text-gray-400">Sem mês</span>
              }
            </div>

            {/* Row 2: email */}
            <p className="text-sm text-gray-500 truncate mb-1">{m.email}</p>

            {/* Row 3: mês atual */}
            {mes && (
              <p className="text-xs text-gray-400">
                {String(mes.mes).padStart(2, '0')}/{mes.ano}
              </p>
            )}
          </Link>
        );
      })}
    </div>
  );
}
```

## Empty State — Dashboard sem Mês

```tsx
<div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 text-center">
  <div className="text-5xl mb-4">🚛</div>
  <p className="font-semibold text-gray-900 text-base mb-1">Nenhum mês aberto</p>
  <p className="text-sm text-gray-500 mb-6 leading-relaxed">
    Inicie o mês para começar a registrar suas viagens e jornadas
  </p>
  <Link
    href={`/motorista/mes/novo?ano=${ano}&mes=${mes}`}
    className="inline-flex items-center gap-2 bg-brand-red text-white px-6 py-3.5 rounded-xl font-semibold text-base"
  >
    <PlusIcon className="w-5 h-5" />
    Iniciar Mês {mesLabel}
  </Link>
</div>
```
