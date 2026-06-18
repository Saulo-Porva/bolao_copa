# Information Architecture

## Estrutura de Navegação Atual

```
/login
└── /motorista
    ├── /dashboard (hub central)
    ├── /mes/novo
    ├── /mes/[id] (detalhe do mês)
    │   └── /fechar
    ├── /viagem/nova
    ├── /viagem/[id]
    │   └── /fechar
    └── /dia/[id]
        └── /fechar

/admin
├── /dashboard (lista de motoristas)
├── /motoristas/[id]
├── /cadastros/motoristas
├── /cadastros/caminhoes
├── /cadastros/clientes
└── /relatorio/[mesId]
```

## Hierarquia de Informação — Motorista

```
Mês (unidade de trabalho mensal)
└── Dia (dias com atividade registrada)
    └── Viagem (entrega individual)
```

**Mental model do motorista:** "Eu abro o mês no começo, registro cada viagem, e fecho no fim do mês."

O fluxo ideal espelha este mental model sem jargão técnico.

## Progressive Disclosure

Princípio: mostrar apenas o que é necessário agora. Detalhes sob demanda.

**Aplicação no dashboard do motorista:**

```
Nível 1 (dashboard) — O que é mais urgente?
  → Status do mês (aberto/fechado)
  → Botão "Nova Viagem" (ação principal do dia)

Nível 2 (detalhe do mês) — O que aconteceu este mês?
  → Lista de dias com viagens
  → KM total, número de viagens

Nível 3 (detalhe da viagem) — Dados desta entrega
  → Cliente, origem, destino, peso, DDT
```

**Anti-pattern:** mostrar todos os campos de todos os meses no dashboard → sobrecarga cognitiva.

## Navegação — Regras para este App

### Motorista (mobile)
- **BottomNav** para destinos principais (≤ 4 items)
- **BackButton** explícito em sub-páginas (não depender do gesto do sistema)
- **Breadcrumb** desnecessário — hierarquia é simples
- **Nunca** usar tabs no topo — zona difícil do polegar

### Admin (desktop)
- **Sidebar** ou **top nav** para módulos principais
- **Breadcrumb** útil em `/admin/motoristas/[id]`
- Pode usar mais densidade de informação

## Nomenclatura — Consistência

| Entidade | No app (PT) | Dito pelos usuários (IT) |
|---------|-------------|------------------------|
| Mês | "Mês" | "Mese" |
| Viagem | "Viagem" | "Viaggio" / "Consegna" |
| Caminhão | "Caminhão" | "Camion" |
| Placa | "Placa" / "Targa" | "Targa" |

**Decisão:** manter PT-BR no código e UI (time de dev fala português). Usuários italianos aprendem os termos em contexto — interface é simples o suficiente.

## Fluxo de Onboarding

Para novos motoristas, o fluxo esperado é:
1. Admin cria conta no Supabase Auth
2. Admin cria perfil de motorista com caminhão padrão
3. Motorista faz login pela primeira vez
4. Dashboard vazio → empty state com "Iniciar Mês" visível

O empty state é o onboarding — não precisa de tela separada.
