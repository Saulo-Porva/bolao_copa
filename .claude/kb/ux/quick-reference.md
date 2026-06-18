# UX — Quick Reference

## Heurísticas de Nielsen — Checklist Rápida

| # | Heurística | Status no App Atual |
|---|-----------|---------------------|
| 1 | Visibilidade do status do sistema | ⚠️ Loading sem indicador visual |
| 2 | Match com o mundo real | ✓ Terminologia italiana/operacional |
| 3 | Controle e liberdade | ⚠️ Sem undo em fechar mês |
| 4 | Consistência e padrões | ⚠️ rounded-lg vs rounded-xl misturados |
| 5 | Prevenção de erros | ⚠️ Sem confirmação em ações destrutivas |
| 6 | Reconhecimento vs recall | ✓ Selects com opções visíveis |
| 7 | Flexibilidade e eficiência | ✓ Placa default pré-selecionada |
| 8 | Estética e design minimalista | ✓ Interface limpa |
| 9 | Recuperação de erros | ⚠️ Mensagens de erro sem instrução |
| 10 | Ajuda e documentação | ✗ Sem help/hint nos campos |

## Taps para Ações Principais

| Ação | Taps atuais | Meta |
|------|-------------|------|
| Iniciar nova viagem | 2 (dashboard → nova viagem) | ✓ OK |
| Ver detalhes do dia | 3+ | Reduzir |
| Fechar uma viagem | 3+ | Reduzir |
| Fechar o mês | 4+ | Reduzir |

## Touch Targets — Mínimos

| Elemento | Atual | Meta |
|---------|-------|------|
| Inputs de form | ~40px | 52px |
| Botão "Sair" | ~24px (texto) | 44px |
| Links de card | ~48px | 56px |
| Botão primário | ~44px | 52px |

## Friction Points Identificados

| Tela | Friction | Severidade |
|------|---------|-----------|
| Login | Botão "Sair" minúsculo e quase invisível | Alta |
| Dashboard | Sem feedback após criar viagem com sucesso | Alta |
| Nova Viagem | Loading state = texto plano | Média |
| Fechar Mês | Sem confirmação antes de ação irreversível | Crítica |
| Admin | "Dashboard" como h1 sem contexto | Baixa |

## WCAG 2.1 — Checklist Rápida

- [ ] Todos os inputs têm `<label>` associado via `for`/`id`
- [ ] Erros identificados por texto (não só cor)
- [ ] Contraste de texto ≥ 4.5:1
- [ ] Botões têm texto descritivo ou `aria-label`
- [ ] Imagens decorativas têm `alt=""`
- [ ] Foco visível em todos os elementos interativos
- [ ] Não depende só de cor para comunicar status

## Estados de UI — Quando Usar Cada Um

| Estado | Quando mostrar | Duração típica |
|--------|---------------|----------------|
| Skeleton | Carregamento inicial de dados | 0 → dados chegam |
| Spinner inline | Ação em botão em andamento | 0 → resposta |
| Toast sucesso | Após salvar/criar com sucesso | 3s auto-dismiss |
| Toast erro | Após falha em ação | Permanente até ação |
| Empty state | Lista/dados sem itens | Permanente |
| Error state | Falha no carregamento inicial | Com botão "Tentar novamente" |
