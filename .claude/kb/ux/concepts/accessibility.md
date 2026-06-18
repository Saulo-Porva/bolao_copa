# Accessibility — WCAG 2.1

## Nível AA — Requisitos para este Projeto

### 1. Contraste de Cor (1.4.3)
Mínimo 4.5:1 para texto normal, 3:1 para texto grande (18px+).

Verificações necessárias:
- `text-red-200` em `bg-brand-red`: 1.8:1 → **FALHA** (botão "Sair" atual)
- `text-gray-500` em `bg-white`: 4.6:1 → ✓
- `text-white` em `bg-brand-red`: 5.1:1 → ✓

### 2. Labels de Formulário (1.3.1 / 4.1.2)
Todo input deve ter um `<label>` associado.

```tsx
// ✓ Correto
<label htmlFor="email">E-mail</label>
<input id="email" name="email" type="email" />

// ✗ Errado — label não associado
<label>E-mail</label>
<input name="email" type="email" />
```

### 3. Mensagens de Erro (1.3.3 / 3.3.1)
Erros não podem ser identificados apenas por cor.

```tsx
// ✓ Cor + ícone + texto
<div className="text-red-600 flex items-center gap-1">
  <ExclamationCircleIcon className="w-4 h-4" aria-hidden="true" />
  <span id="email-error">E-mail inválido</span>
</div>

// Associar ao input
<input aria-describedby="email-error" aria-invalid="true" />
```

### 4. Foco Visível (2.4.7)
Elementos interativos devem ter indicador de foco visível.

```tsx
// ✓ Focus ring explícito
<button className="focus:outline-none focus:ring-2 focus:ring-brand-red focus:ring-offset-2">
```

### 5. Textos Alternativos (1.1.1)
Imagens e ícones com significado precisam de alt/aria-label.

```tsx
// Ícone decorativo
<TruckIcon aria-hidden="true" className="w-6 h-6" />

// Ícone com significado
<button aria-label="Voltar para dashboard">
  <ArrowLeftIcon aria-hidden="true" />
</button>

// Logo/imagem
<img src="/logo.png" alt="PR Trasporti" />
```

### 6. Ordem de Foco (2.4.3)
A ordem de tab deve seguir a ordem visual/lógica do conteúdo.

**No formulário de viagem:** Placa → Cliente → Peso → DDT → Origem → Destino → Botão Submit.

### 7. Idioma da Página (3.1.1)
```tsx
// app/layout.tsx
<html lang="pt-BR">  {/* ou "it" se mudar para italiano */}
```

## ARIA Roles Relevantes

```tsx
// Região de conteúdo principal
<main role="main">

// Alertas que devem ser lidos imediatamente
<div role="alert" className="...">Erro ao salvar</div>

// Status updates não urgentes
<div role="status" aria-live="polite">Viagem salva com sucesso</div>

// Botão com estado de loading
<button aria-busy={loading} aria-label={loading ? 'Salvando viagem...' : 'Salvar viagem'}>
```

## Checklist por Componente

### Login Page
- [ ] `<label>` associado a cada input
- [ ] Erro de login com `role="alert"`
- [ ] Botão de submit com estado de loading acessível

### Formulário de Viagem
- [ ] Todos os campos com `<label htmlFor>`
- [ ] Campos com erro têm `aria-invalid="true"` e `aria-describedby`
- [ ] Botão submit com `aria-busy` durante loading

### Dashboard
- [ ] Heading hierarchy: h1 → h2 → h3 (sem pular níveis)
- [ ] Links de card com texto descritivo (não só "clique aqui")
- [ ] StatusBadge com texto suficiente (não só cor)

### Header/Nav
- [ ] Logo/link com `aria-label="Ir para dashboard"`
- [ ] Botão "Sair" com `aria-label="Sair da conta"` (texto atual muito pequeno)
