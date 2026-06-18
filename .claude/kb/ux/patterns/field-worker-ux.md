# Field Worker UX

## O Contexto do Motorista

O usuário deste app não está sentado numa mesa com Wi-Fi estável e tempo para explorar a interface. Ele está:

- No pátio de uma empresa, caminhão ligado esperando
- Às vezes com luvas de trabalho finas
- Pressionado para registrar rápido e partir
- Com sinal 4G variável em zonas industriais/rurais
- Com luz solar direta no celular

**Consequência de design:** Cada fricção extra é amplificada 3x neste contexto.

## Princípios Específicos para Campo

### 1. Zero Latência Percebida
O motorista não vai esperar. Se a tela parece travada, ele vai apertar o botão de novo.

```tsx
// Feedback imediato ao tap
<button
  onMouseDown={() => setPressed(true)}  // inicia feedback antes do click completo
  className="active:scale-95 active:brightness-90 transition-transform duration-75"
>
```

### 2. Formulário Mínimo
Só pedir o que é absolutamente necessário. Campos opcionais podem ser omitidos na primeira versão.

| Campo | Obrigatório? | Justificativa |
|-------|-------------|---------------|
| Placa | ✓ Sim | Rastreamento do caminhão |
| Cliente | Opcional | Pode não saber no momento |
| Origem/Destino | Opcional | Pode preencher depois |
| Peso | Opcional | Verificado na balança, pode não ter na hora |
| DDT | Opcional | Documento entregue no destino |

**Regra:** Se o motorista pode completar a tarefa sem o campo, ele é opcional.

### 3. Smart Defaults
Pré-preencher com os valores mais prováveis:

```tsx
// Placa do caminhão padrão do motorista (já implementado)
const [placa, setPlaca] = useState(placaDefault ?? '');

// Data de hoje (para campos de data)
const today = new Date().toISOString().split('T')[0];

// Último cliente usado (a implementar)
const ultimoCliente = useLocalStorage('ultimo_cliente_id');
```

### 4. Confirmação Rápida, Não Bloqueante
Após salvar uma viagem, mostrar confirmação por 2-3s e retornar ao fluxo. Não exigir que o motorista feche um modal.

```tsx
// Auto-dismiss após 3s
useEffect(() => {
  if (success) {
    const timer = setTimeout(() => setSuccess(false), 3000);
    return () => clearTimeout(timer);
  }
}, [success]);
```

### 5. Recuperação Fácil de Erros
Se falhou, deixar claro o que falhou e como corrigir. Não limpar o formulário após erro.

```tsx
// ✓ Manter dados após erro
async function handleSubmit(dados) {
  const result = await criarViagem(dados);
  if (result.error) {
    setError('Não foi possível salvar. Tente novamente.');
    // NÃO resetar o formulário — manter dados digitados
  }
}
```

## Padrão de Ação Crítica de Campo

Para fechar viagem ou fechar mês — ações com consequências:

```tsx
// 1. Tap no botão → bottom sheet de confirmação
// 2. Motorista confirma ou cancela
// 3. Se confirmar → loading visual → sucesso → redirect

export function FecharAcaoPage() {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleConfirmar() {
    setLoading(true);
    const result = await fecharViagem(id);
    if (!result.error) {
      router.push(successRedirect);
    } else {
      setLoading(false);
      setError(result.error);
      setConfirmOpen(false);
    }
  }

  return (
    <>
      <button
        onClick={() => setConfirmOpen(true)}
        className="w-full bg-gray-800 text-white py-3.5 rounded-xl font-semibold"
      >
        Fechar Viagem
      </button>

      <ConfirmSheet
        open={confirmOpen}
        title="Fechar esta viagem?"
        description="Os dados não poderão ser editados após fechar."
        confirmLabel="Confirmar"
        onConfirm={handleConfirmar}
        onCancel={() => setConfirmOpen(false)}
        loading={loading}
      />
    </>
  );
}
```

## Anti-Patterns a Evitar para Campo

| Anti-pattern | Por que é ruim para motoristas | Alternativa |
|---|---|---|
| Modal centralizado bloqueante | Difícil fechar com uma mão | Bottom sheet |
| Pequeno botão "Cancelar" ao lado do "Confirmar" | Tap acidental destrutivo | Botões em coluna, "Cancelar" embaixo |
| Formulário que limpa após erro | Motorista digita tudo de novo | Manter estado |
| Loading infinito sem timeout | Motorista acha que travou | Timeout 15s + mensagem |
| Deep navigation sem BackButton | Usuário fica preso | BackButton sempre visível em sub-páginas |
| Texto `text-xs` em informação crítica | Ilegível ao sol | `text-base` mínimo |
