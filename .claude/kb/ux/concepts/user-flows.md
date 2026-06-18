# User Flows

## Fluxo Principal — Registrar uma Viagem

**Happy path (3 taps):**
```
Dashboard
  [tap: "Nova Viagem"]
    ↓
Formulário Nova Viagem
  [preencher: placa (default), cliente, origem, destino]
  [tap: "Criar Viagem"]
    ↓
Tela do Dia (com viagem criada + toast de sucesso)
```

**Pain points atuais no happy path:**
- Após criar viagem, redireciona para `/motorista/dia/[id]` — correto
- Mas não há toast confirmando o sucesso
- Se o motorista apertar "Criar Viagem" duas vezes, pode criar duplicata (sem proteção de double-submit)

## Fluxo de Abertura de Mês

```
Dashboard (empty state: "Nenhum mês aberto")
  [tap: "Iniciar Mês"]
    ↓
/motorista/mes/novo?ano=2025&mes=5
  [preencher: KM inicial, selecionar caminhão]
  [tap: "Abrir Mês"]
    ↓
Dashboard (com card do mês + "Nova Viagem" disponível)
```

## Fluxo de Fechamento de Mês

**Ação crítica — requer confirmação:**
```
/motorista/mes/[id]
  [tap: "Fechar Mês"]
    ↓
Bottom sheet de confirmação
  "Fechar Maio/2025? Esta ação não pode ser desfeita."
  [tap: "Confirmar"]
    ↓
/motorista/mes/[id] (status = fechado)
```

**Por que bottom sheet e não modal:** Bottom sheet é mais natural em mobile e não bloqueia totalmente o contexto visual da tela anterior.

## Fluxo de Erro — Sem Conexão

```
Motorista tenta criar viagem [offline]
  ↓
Banner de offline aparece (topo)
  "Sem conexão — conecte-se para salvar"
  ↓
Botão "Criar Viagem" desabilitado ou:
  Tenta → toast de erro com "Tente novamente quando online"
```

## Fluxo de Autenticação

```
Acesso a qualquer rota protegida (sem sessão)
  ↓
Middleware redireciona → /login
  ↓
Login com e-mail + senha
  ↓
Supabase Auth → role = 'motorista' | 'admin'
  ↓
Redirecionamento por role:
  motorista → /motorista/dashboard
  admin     → /admin/dashboard
```

## Fluxo Admin — Consultar Motorista

```
/admin/dashboard (lista de motoristas com status)
  [tap no card do motorista]
    ↓
/admin/motoristas/[id]
  Histórico de meses, viagens do mês selecionado
  [tap: "Ver Relatório"]
    ↓
/admin/relatorio/[mesId]
  Relatório mensal imprimível / exportável
```

## Error Paths — Tratamento

| Erro | Causa | UX Recomendada |
|------|-------|---------------|
| Login inválido | Credenciais erradas | Mensagem inline, campos não limpos |
| Sem conexão | Offline | Banner + desabilitar ações de escrita |
| Timeout da API | Supabase lento | Toast com "Tente novamente" + retry |
| Mês já fechado | Tenta criar viagem em mês fechado | Redirect para dashboard com aviso |
| Campo obrigatório vazio | Submit sem preencher | Validação inline no blur |
| Sessão expirada | Token vencido | Redirect para login com mensagem "Sessão expirada" |

## Microdecisions — Decisões de UX Menores

| Decisão | Escolha | Rationale |
|---------|---------|-----------|
| Label "Sair" vs ícone de logout | Label de texto | Ícone só é óbvio se for universalmente reconhecido |
| Data atual: exibir ou não? | Exibir no dashboard | Motorista confirma que está no dia certo |
| Placa padrão: pré-selecionar? | Sim (já implementado) | Reduce friction para o caso mais comum |
| Campos opcionais: marcar? | Não (todos tratados como opcionais por default) | Menos ruído visual |
