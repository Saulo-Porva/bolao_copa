# Form Design Patterns

## Campo de Formulário — Padrão Base

```tsx
interface FieldProps {
  label: string;
  name: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: React.ReactElement;
}

export function Field({ label, name, error, hint, required, children }: FieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={name} className="text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>

      {React.cloneElement(children, {
        id: name,
        name,
        'aria-invalid': error ? 'true' : undefined,
        'aria-describedby': error ? `${name}-error` : hint ? `${name}-hint` : undefined,
      })}

      {hint && !error && (
        <p id={`${name}-hint`} className="text-xs text-gray-500">{hint}</p>
      )}
      {error && (
        <p id={`${name}-error`} role="alert" className="text-xs text-red-600 flex items-center gap-1">
          <ExclamationCircleIcon className="w-3.5 h-3.5 shrink-0" />
          {error}
        </p>
      )}
    </div>
  );
}
```

## Input Padrão — Classes

```tsx
const inputClasses = `
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
`;
```

## Select Nativo — Estilizado

```tsx
<select
  name="cliente_id"
  className="w-full border border-gray-200 rounded-xl px-4 py-3.5 text-base text-gray-900 bg-white focus:border-brand-red focus:ring-2 focus:ring-brand-red/20 focus:outline-none appearance-none bg-[url('data:image/svg+xml,...')] bg-no-repeat bg-[right_1rem_center]"
>
  <option value="">Selecionar cliente...</option>
  {clientes.map((c) => (
    <option key={c.id} value={c.id}>{c.nome}</option>
  ))}
</select>
```

## Formulário Completo — ViagemForm Refatorado

```tsx
export function ViagemForm({ clientes, caminhoes, placaDefault, onSubmit }: ViagemFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">

      {/* Campo obrigatório com destaque */}
      <Field label="Placa do Caminhão" name="placa" required>
        <input
          list="placas-list"
          className={inputClasses}
          placeholder="Ex: GA993AV"
        />
      </Field>

      {/* Select */}
      <Field label="Cliente" name="cliente_id">
        <select className={selectClasses}>
          <option value="">Selecionar cliente...</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>{c.nome}</option>
          ))}
        </select>
      </Field>

      {/* Grid 2 colunas — campos relacionados */}
      <div className="grid grid-cols-2 gap-3">
        <Field label="Peso (kg)" name="peso">
          <input type="number" step="0.01" className={inputClasses} placeholder="350" />
        </Field>
        <Field label="DDT / Form" name="ddt_form">
          <input type="text" className={inputClasses} placeholder="1992" />
        </Field>
      </div>

      {/* Grupo de rota */}
      <div className="flex flex-col gap-3">
        <Field label="Origem" name="origem">
          <input type="text" className={inputClasses} placeholder="Bolzano" />
        </Field>
        <Field label="Destino" name="destino">
          <input type="text" className={inputClasses} placeholder="Vicenza" />
        </Field>
      </div>

      {/* Erro global */}
      {error && (
        <div role="alert" className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 flex items-start gap-3">
          <XCircleIcon className="w-5 h-5 shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {/* CTA fixo no fundo */}
      <div className="sticky bottom-0 bg-white border-t border-gray-100 p-4 -mx-4 mt-2">
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-brand-red text-white py-3.5 rounded-xl font-semibold text-base disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading && <SpinnerIcon className="w-4 h-4 animate-spin" />}
          {loading ? 'Salvando...' : 'Criar Viagem'}
        </button>
      </div>
    </form>
  );
}
```

## Confirmação de Ação Destrutiva

Para "Fechar Mês" ou "Cancelar Viagem" — sempre requerer confirmação:

```tsx
// Bottom sheet de confirmação
export function ConfirmSheet({ title, description, onConfirm, onCancel }: Props) {
  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40" onClick={onCancel} />

      {/* Sheet */}
      <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-2xl p-6 pb-safe">
        <div className="w-12 h-1 bg-gray-300 rounded-full mx-auto mb-6" />
        <h2 className="text-lg font-bold text-gray-900 mb-2">{title}</h2>
        <p className="text-sm text-gray-600 mb-6">{description}</p>
        <div className="flex flex-col gap-3">
          <button onClick={onConfirm} className="w-full bg-red-600 text-white py-3.5 rounded-xl font-semibold text-base">
            Confirmar
          </button>
          <button onClick={onCancel} className="w-full bg-gray-100 text-gray-700 py-3.5 rounded-xl font-medium text-base">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
```
