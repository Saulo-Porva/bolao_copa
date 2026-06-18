# Usability Principles

## 10 Heurísticas de Nielsen

### 1. Visibilidade do Status do Sistema
O sistema deve manter os usuários informados sobre o que está acontecendo.

**Para motoristas:** Estado do mês (aberto/fechado) deve ser sempre visível. Loading de ações deve ter indicador visual, não silêncio.

```tsx
// ✓ Botão com estado de loading visível
<button disabled={loading}>
  {loading ? (
    <><SpinnerIcon className="animate-spin w-4 h-4" /> Salvando...</>
  ) : 'Criar Viagem'}
</button>

// ✗ Loading silencioso
<button disabled={loading}>
  {loading ? 'Carregando...' : 'Criar Viagem'}
</button>
```

### 2. Match com o Mundo Real
Use a linguagem e conceitos familiares ao usuário.

**Para motoristas italianos:** "DDT" (Documento di Trasporto), "Bolla", "Targa" — não traduzir.

### 3. Controle e Liberdade do Usuário
Usuários cometem erros. Ofereça saídas claramente marcadas.

**Para este app:** Confirmar antes de fechar mês (irreversível). Permitir editar viagem antes de fechar o dia.

### 4. Consistência e Padrões
Usuários não deveriam precisar adivinhar se diferentes palavras, situações ou ações significam a mesma coisa.

**Bug atual:** `rounded-lg` nos inputs do ViagemForm vs `rounded-xl` no resto → inconsistência visual.

### 5. Prevenção de Erros
Melhor que uma boa mensagem de erro é um design cuidadoso que previne o problema.

```tsx
// Confirmação antes de ação destrutiva
<button onClick={() => setShowConfirm(true)}>Fechar Mês</button>
<ConfirmSheet
  title="Fechar mês de Maio/2025?"
  description="Esta ação não pode ser desfeita. Todas as viagens serão finalizadas."
  onConfirm={handleFecharMes}
/>
```

### 6. Reconhecimento em vez de Recall
Minimize a carga de memória. Opções visíveis > memorizar comandos.

**Para formulários:** Usar `<datalist>` para placas (já implementado ✓). Usar `<select>` para clientes. Mostrar placa padrão pré-selecionada.

### 7. Flexibilidade e Eficiência de Uso
Accelerators — invisíveis para novatos, mas permitem que experientes sejam mais rápidos.

**Para motoristas frequentes:** Placa padrão pré-selecionada (já implementado ✓). Último cliente usado como default. Data de hoje pré-preenchida.

### 8. Estética e Design Minimalista
Cada unidade extra de informação compete com as unidades relevantes e diminui sua visibilidade relativa.

**Para este app:** Foco numa ação por tela. Remover labels óbvios. Não mostrar KM Final no card do mês se ainda não foi fechado.

### 9. Ajudar Usuários a Reconhecer, Diagnosticar e Recuperar de Erros
Mensagens de erro devem ser expressas em linguagem simples, indicar o problema e sugerir solução.

```tsx
// ✓ Erro com instrução
<ErrorAlert>
  Não foi possível salvar. Verifique sua conexão e tente novamente.
  <button onClick={retry}>Tentar novamente</button>
</ErrorAlert>

// ✗ Erro sem orientação
<ErrorAlert>Erro ao salvar.</ErrorAlert>
```

### 10. Ajuda e Documentação
Mesmo que seja melhor que o sistema não precise de documentação, pode ser necessário fornecer ajuda.

**Para este app:** Hint text em campos não óbvios (ex: DDT: "Número do documento de transporte").

---

## Lei de Fitts

**Princípio:** O tempo para atingir um alvo é função da distância e do tamanho do alvo.

**Implicações:**
- Botões maiores = mais fáceis de acertar = menos erros
- Botões no canto inferior são mais fáceis de alcançar com o polegar
- Botões perigosos (cancelar, fechar) devem ser menores E separados

## Lei de Hick

**Princípio:** O tempo de decisão aumenta logaritmicamente com o número de opções.

**Implicações para formulários:**
- Limitar opções em selects (mostrar mais usadas primeiro)
- Uma ação por tela quando possível
- Agrupe ações relacionadas, não as espalhe
