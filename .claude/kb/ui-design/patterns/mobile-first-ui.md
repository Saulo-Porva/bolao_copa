# Mobile-First UI Patterns

## AppShell — Estrutura Base

```tsx
// Motorista layout — estrutura recomendada
export default function MotoristaLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header fixo */}
      <header className="bg-brand-red text-white px-4 py-3 flex items-center justify-between sticky top-0 z-10 h-14">
        <Link href="/motorista/dashboard" className="flex items-center gap-2">
          <TruckIcon className="w-6 h-6" />
          <span className="font-bold text-base">PR Trasporti</span>
        </Link>
        <LogoutButton />
      </header>

      {/* Conteúdo scrollável */}
      <main className="flex-1 px-4 py-6 max-w-lg mx-auto w-full pb-24">
        {children}
      </main>

      {/* BottomNav fixo — se mais de 2 destinos principais */}
      <BottomNav />
    </div>
  );
}
```

## BottomNav — Navegação Principal Mobile

```tsx
// Quando o motorista tiver 3+ destinos frequentes
export function BottomNav() {
  const pathname = usePathname();

  const items = [
    { href: '/motorista/dashboard', icon: HomeIcon, label: 'Início' },
    { href: '/motorista/viagem/nova', icon: PlusCircleIcon, label: 'Viagem' },
    { href: '/motorista/mes', icon: CalendarIcon, label: 'Mês' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex safe-area-bottom z-10">
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            "flex-1 flex flex-col items-center gap-1 py-3 text-xs font-medium transition-colors",
            pathname === item.href
              ? "text-brand-red"
              : "text-gray-500 hover:text-gray-700"
          )}
        >
          <item.icon className="w-6 h-6" />
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
```

## StickyActionBar — Botão de Ação Fixo

Para formulários longos ou páginas com scroll — o CTA fica visível sempre:

```tsx
// Dentro do form ou da página
<div className="sticky bottom-0 bg-white border-t border-gray-100 p-4 -mx-4 mt-6">
  <button
    type="submit"
    disabled={loading}
    className="w-full bg-brand-red text-white py-3.5 rounded-xl font-semibold text-base disabled:opacity-50"
  >
    {loading ? <LoadingSpinner /> : 'Salvar Viagem'}
  </button>
</div>
```

## Feedback de Ação — Toast / Snackbar

```tsx
// Toast minimalista (sem biblioteca externa)
// Posicionado no topo para não bloquear o conteúdo em edição
export function Toast({ message, type }: { message: string; type: 'success' | 'error' }) {
  return (
    <div className={cn(
      "fixed top-16 left-4 right-4 z-50 p-4 rounded-xl shadow-lg flex items-center gap-3",
      "animate-in slide-in-from-top-2 duration-200",
      type === 'success' ? "bg-green-600 text-white" : "bg-red-600 text-white"
    )}>
      {type === 'success' ? <CheckIcon className="w-5 h-5 shrink-0" /> : <XIcon className="w-5 h-5 shrink-0" />}
      <span className="text-sm font-medium">{message}</span>
    </div>
  );
}
```

## Banner Offline

```tsx
// Detectar conectividade para campo
export function OfflineBanner() {
  const [offline, setOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const on = () => setOffline(false);
    const off = () => setOffline(true);
    window.addEventListener('online', on);
    window.addEventListener('offline', off);
    return () => { window.removeEventListener('online', on); window.removeEventListener('offline', off); };
  }, []);

  if (!offline) return null;

  return (
    <div className="bg-amber-500 text-white text-center text-sm py-2 px-4 font-medium">
      Sem conexão — dados serão salvos quando reconectar
    </div>
  );
}
```

## Skeleton Screen — Loading State

```tsx
// Skeleton do dashboard do motorista
export function DashboardSkeleton() {
  return (
    <div className="flex flex-col gap-6 animate-pulse">
      {/* Header skeleton */}
      <div>
        <div className="h-6 bg-gray-200 rounded w-48 mb-2" />
        <div className="h-4 bg-gray-200 rounded w-32" />
      </div>
      {/* Card skeleton */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
        <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
        <div className="h-6 bg-gray-200 rounded w-32 mb-4" />
        <div className="grid grid-cols-2 gap-2 mb-4">
          <div className="h-4 bg-gray-200 rounded" />
          <div className="h-4 bg-gray-200 rounded" />
        </div>
        <div className="h-10 bg-gray-200 rounded-xl" />
      </div>
    </div>
  );
}
```
