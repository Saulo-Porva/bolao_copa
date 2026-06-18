# Feedback Patterns

## Toast / Snackbar

Feedback não-bloqueante para ações completadas.

```tsx
// hooks/useToast.ts
interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
  duration?: number;
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const show = (message: string, type: Toast['type'] = 'success', duration = 3000) => {
    const id = Math.random().toString(36).slice(2);
    setToasts(prev => [...prev, { id, message, type, duration }]);

    if (duration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, duration);
    }
  };

  return { toasts, show };
}

// components/ToastContainer.tsx
export function ToastContainer({ toasts }: { toasts: Toast[] }) {
  return (
    <div className="fixed top-16 left-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map(toast => (
        <div
          key={toast.id}
          role={toast.type === 'error' ? 'alert' : 'status'}
          aria-live={toast.type === 'error' ? 'assertive' : 'polite'}
          className={cn(
            "flex items-center gap-3 px-4 py-3.5 rounded-xl shadow-lg text-sm font-medium",
            "animate-in slide-in-from-top-2 duration-200",
            toast.type === 'success' && "bg-green-600 text-white",
            toast.type === 'error'   && "bg-red-600 text-white",
            toast.type === 'info'    && "bg-gray-800 text-white",
          )}
        >
          {toast.type === 'success' && <CheckCircleIcon className="w-5 h-5 shrink-0" aria-hidden />}
          {toast.type === 'error'   && <XCircleIcon className="w-5 h-5 shrink-0" aria-hidden />}
          {toast.message}
        </div>
      ))}
    </div>
  );
}
```

## Skeleton Screens

Preferível a spinners para carregamento de dados de página.

```tsx
// components/skeletons/DashboardSkeleton.tsx
export function DashboardSkeleton() {
  return (
    <div className="flex flex-col gap-6 animate-pulse" aria-label="Carregando...">
      {/* Saudação */}
      <div>
        <div className="h-6 bg-gray-200 rounded-lg w-48 mb-2" />
        <div className="h-4 bg-gray-200 rounded w-32" />
      </div>

      {/* Card de mês */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
        <div className="flex justify-between mb-3">
          <div>
            <div className="h-3 bg-gray-200 rounded w-20 mb-2" />
            <div className="h-6 bg-gray-200 rounded w-24" />
          </div>
          <div className="h-6 bg-gray-200 rounded-full w-16" />
        </div>
        <div className="grid grid-cols-2 gap-2 mb-4">
          <div className="h-4 bg-gray-200 rounded" />
          <div className="h-4 bg-gray-200 rounded" />
        </div>
        <div className="h-10 bg-gray-200 rounded-xl" />
      </div>

      {/* CTA */}
      <div className="h-16 bg-gray-200 rounded-2xl" />
    </div>
  );
}
```

## Empty States

Contexto + orientação + ação. Nunca só "Nenhum resultado."

```tsx
interface EmptyStateProps {
  emoji: string;
  title: string;
  description: string;
  action?: { label: string; href: string };
}

export function EmptyState({ emoji, title, description, action }: EmptyStateProps) {
  return (
    <div className="text-center py-12 px-6">
      <div className="text-5xl mb-4" aria-hidden>{emoji}</div>
      <h2 className="text-base font-semibold text-gray-900 mb-1">{title}</h2>
      <p className="text-sm text-gray-500 leading-relaxed mb-6">{description}</p>
      {action && (
        <Link
          href={action.href}
          className="inline-flex items-center gap-2 bg-brand-red text-white px-6 py-3.5 rounded-xl font-semibold text-base"
        >
          {action.label}
        </Link>
      )}
    </div>
  );
}

// Uso
<EmptyState
  emoji="🚛"
  title="Nenhum mês aberto"
  description="Inicie o mês para registrar suas viagens e jornadas de trabalho."
  action={{ label: `Iniciar Maio/2025`, href: `/motorista/mes/novo?ano=2025&mes=5` }}
/>
```

## Error State — Falha no Carregamento

```tsx
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="text-center py-12 px-6">
      <div className="text-4xl mb-4" aria-hidden>⚠️</div>
      <p className="text-base font-semibold text-gray-900 mb-1">Algo deu errado</p>
      <p className="text-sm text-gray-500 mb-6">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 border border-gray-300 text-gray-700 px-6 py-3 rounded-xl font-medium text-sm"
        >
          <ArrowPathIcon className="w-4 h-4" />
          Tentar novamente
        </button>
      )}
    </div>
  );
}
```

## Inline Validation

Validar no `onBlur`, não no `onChange` (evita ansiedade de erro enquanto digita).

```tsx
function useFieldValidation(value: string, validate: (v: string) => string | null) {
  const [touched, setTouched] = useState(false);
  const error = touched ? validate(value) : null;
  return {
    error,
    onBlur: () => setTouched(true),
  };
}
```
