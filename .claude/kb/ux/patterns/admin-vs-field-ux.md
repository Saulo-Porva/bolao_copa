# Admin vs Field Worker UX

## Duas Personas, Dois Contextos

| Dimensão | Motorista (campo) | Admin (escritório) |
|----------|------------------|-------------------|
| Dispositivo | Celular (360-430px) | Desktop (1280px+) |
| Ambiente | Sol, vibração, pressa | Mesa, Wi-Fi, tranquilidade |
| Objetivo | Registrar rápido | Analisar, consultar, exportar |
| Frequência | Diária, múltiplas vezes | Semanal ou mensal |
| Tolerância a erros | Baixíssima (retrabalho caro) | Média (pode desfazer) |
| Densidade visual | Baixa (foco único) | Alta (mais dados por tela) |

## Layout por Perfil

### Motorista — Layout Mobile-First

```tsx
// Elementos de UI para motorista
- BottomNav (não sidebar)
- Cards em coluna única
- CTAs no fundo da tela
- Tipografia base ≥ 16px
- Touch targets ≥ 52px
- Foco em UMA ação por tela
- Confirmações via bottom sheet
```

### Admin — Layout Desktop

```tsx
// Elementos de UI para admin
- Sidebar de navegação (ou top nav)
- Grid de cards (2-3 colunas)
- Tabelas com múltiplas colunas
- Tipografia menor aceitável (14px)
- Ações em hover (não precisam de tap)
- Múltiplas ações visíveis simultaneamente
- Modais (não bottom sheets)
```

## Densidade de Informação

### Dashboard Motorista — Baixa densidade
```
✓ Ver só: mês atual, status, botão nova viagem
✗ Não mostrar: histórico de meses, relatórios, configurações
```

### Dashboard Admin — Alta densidade
```
✓ Ver: todos motoristas + status em grid
✓ Filtros, busca, exportação acessíveis
✓ Resumo numérico (total de viagens, meses abertos)
```

## Ações por Perfil

| Ação | Motorista | Admin |
|------|-----------|-------|
| Registrar viagem | Ação principal | Não faz |
| Abrir/fechar mês | Faz (próprio mês) | Pode fazer (por qualquer motorista) |
| Ver histórico | Só próprio | Todos os motoristas |
| Gerar relatório | Não | Sim (PDF/Excel) |
| Cadastrar motoristas | Não | Sim |
| Cadastrar caminhões | Não | Sim |

## Navegação por Perfil

### Motorista
```
/motorista/dashboard (hub)
├── Nova Viagem (CTA sempre visível)
├── Ver Mês Atual
└── [Histórico acessível via detalhe do mês]
```

### Admin
```
/admin/dashboard
├── Motoristas (default — lista geral)
├── Cadastros
│   ├── Motoristas
│   ├── Caminhões
│   └── Clientes
└── Relatórios (por motorista/mês)
```

## Responsividade

O projeto tem dois públicos distintos. A abordagem mais limpa é:

```
/motorista/* → otimizado para mobile (CSS mobile-first, max-w-lg)
/admin/*     → otimizado para desktop (grid responsivo, tabelas, mais densidade)
```

Não tentar fazer o layout do motorista funcionar em desktop ou vice-versa — são jornadas diferentes.

## Componentes Compartilhados vs Específicos

| Componente | Compartilhado | Notas |
|-----------|--------------|-------|
| StatusBadge | ✓ | Mesmo visual, mesma semântica |
| Button | ✓ (variantes) | Motorista usa fullWidth; admin usa size compacto |
| Input/Field | ✓ | Admin pode usar size menor |
| BottomNav | ✗ | Só motorista |
| Sidebar | ✗ | Só admin |
| DataTable | ✗ | Só admin (relatórios) |
| ConfirmSheet | ✓ | Motorista: bottom sheet; Admin: pode ser modal |
