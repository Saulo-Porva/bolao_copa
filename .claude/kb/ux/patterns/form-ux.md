# Form UX Patterns

## Princípios de UX para Formulários

### 1. Uma coluna, exceto quando relacionados
Em mobile, sempre uma coluna. Exceção: campos curtos e relacionados (Peso + DDT, Origem + Destino).

### 2. Labels acima, sempre
Labels laterais economizam espaço mas são difíceis em mobile. Labels acima do campo são mais fáceis de ler.

### 3. Placeholder como exemplo, não como label
```tsx
// ✓ Label + placeholder de exemplo
<Field label="Placa do Caminhão">
  <input placeholder="Ex: GA993AV" />
</Field>

// ✗ Placeholder como label (desaparece ao digitar)
<input placeholder="Placa do Caminhão" />
```

### 4. Hint text para campos não óbvios
```tsx
<Field label="DDT / Form" hint="Número do documento de transporte">
  <input name="ddt_form" placeholder="1992" />
</Field>
```

### 5. Ordem: do mais simples ao mais complexo
No ViagemForm atual, a ordem é razoável. Para otimizar:
```
1. Placa (simples, tem default)
2. Cliente (select com opções)
3. Origem / Destino (texto livre — juntos pois são par lógico)
4. Peso / DDT (numérico/código — juntos pois são par lógico)
```

### 6. Botão de submit sempre visível
Em formulários que precisam de scroll, usar `sticky bottom-0` no botão.

## Smart Defaults

```tsx
// Pré-preencher com dados prováveis
function useSmartDefaults(motoristaId: string) {
  const [defaults, setDefaults] = useState({
    placa: '',
    cliente_id: '',
    origem: '',
  });

  useEffect(() => {
    // Placa padrão do motorista (do banco)
    // Último cliente (do localStorage)
    // Última origem usada (do localStorage)
    const ultimoCliente = localStorage.getItem('ultimo_cliente_id') ?? '';
    const ultimaOrigem = localStorage.getItem('ultima_origem') ?? '';
    setDefaults(prev => ({ ...prev, cliente_id: ultimoCliente, origem: ultimaOrigem }));
  }, [motoristaId]);

  return defaults;
}
```

## Validação — Quando e Como

| Trigger | Quando usar | Exemplo |
|---------|-------------|---------|
| `onBlur` | Campos de texto | Após sair do campo: mostrar erro |
| `onChange` | Confirmação de senha | Verificar match em tempo real |
| `onSubmit` | Campos obrigatórios | Resumo de erros ao tentar enviar |

```tsx
// Pattern: validar onBlur, mostrar erro no campo específico
function ViagemForm() {
  const [errors, setErrors] = useState<Record<string, string>>({});

  function validateField(name: string, value: string) {
    if (name === 'placa' && !value.trim()) {
      setErrors(prev => ({ ...prev, placa: 'Placa é obrigatória' }));
    } else {
      setErrors(prev => { const { [name]: _, ...rest } = prev; return rest; });
    }
  }

  return (
    <Field label="Placa" error={errors.placa}>
      <input
        onBlur={(e) => validateField('placa', e.target.value)}
        aria-invalid={!!errors.placa}
        aria-describedby={errors.placa ? 'placa-error' : undefined}
      />
    </Field>
  );
}
```

## Submit Button — Estados

```tsx
type SubmitState = 'idle' | 'loading' | 'success' | 'error';

function SubmitButton({ state }: { state: SubmitState }) {
  const config = {
    idle:    { label: 'Criar Viagem', disabled: false, className: 'bg-brand-red' },
    loading: { label: 'Salvando...',  disabled: true,  className: 'bg-brand-red opacity-75' },
    success: { label: '✓ Salvo!',     disabled: true,  className: 'bg-green-600' },
    error:   { label: 'Tentar novamente', disabled: false, className: 'bg-brand-red' },
  }[state];

  return (
    <button
      type="submit"
      disabled={config.disabled}
      aria-busy={state === 'loading'}
      className={`w-full text-white py-3.5 rounded-xl font-semibold text-base flex items-center justify-center gap-2 transition-colors ${config.className}`}
    >
      {state === 'loading' && <SpinnerIcon className="w-4 h-4 animate-spin" aria-hidden />}
      {config.label}
    </button>
  );
}
```

## Double Submit Protection

```tsx
// Garantir que não submete duas vezes
const submitting = useRef(false);

async function handleSubmit(e: React.FormEvent) {
  if (submitting.current) return;
  submitting.current = true;
  setLoading(true);

  try {
    await onSubmit(formData);
  } finally {
    submitting.current = false;
    setLoading(false);
  }
}
```
