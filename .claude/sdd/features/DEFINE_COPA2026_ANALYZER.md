# DEFINE: Analisador de Resultados Copa do Mundo 2026

> Pipeline de coleta diária + análise LLM multi-sinal que prediz resultados da Copa 2026 com 3 cenários probabilísticos, apresentado em dashboard Streamlit Cloud alimentado por GCS.

## Metadata

| Atributo | Valor |
|----------|-------|
| **Feature** | COPA2026_ANALYZER |
| **Data** | 2026-06-19 |
| **Autor** | define-agent |
| **Status** | Ready for Design |
| **Clarity Score** | 15/15 |
| **Fonte** | BRAINSTORM_COPA2026_ANALYZER.md |

---

## Problem Statement

Apostadores e participantes de bolão tomam decisões baseadas em feeling ou em estatísticas públicas que os bookmakers já precificaram — eliminando qualquer vantagem informacional. Falta um sistema que combine dados estruturados (H2H, forma, lesões, odds) com informação assimétrica (noticiários locais em idioma nativo + sentimento de vestiário) para detectar oportunidades onde a probabilidade real diverge da probabilidade implícita do mercado.

---

## Target Users

| Usuário | Papel | Dor Principal |
|---------|-------|---------------|
| Apostador pessoal | Usuário primário | Aposta em bookmakers sem vantagem estatística sobre o mercado; perde dinheiro a longo prazo |
| Participante de bolão | Usuário secundário | Palpites baseados em feeling ou narrativa de mídia mainstream, não em dados multi-camada |
| Pesquisador técnico | Usuário terciário | Quer explorar pipeline LLM + dados esportivos como projeto de portfólio/pesquisa |

---

## Goals

| Prioridade | Goal |
|------------|------|
| **MUST** | Coletar e persistir dados dos 48 times da Copa 2026 no GCS automaticamente (pipeline local diário) |
| **MUST** | Analisar qualquer partida entre os 48 times com 3 cenários probabilísticos (%) + narrativa explicativa para cada |
| **MUST** | Calcular e armazenar score de sentimento de vestiário por seleção via pipeline híbrido (XLM-RoBERTa + Claude Haiku) |
| **MUST** | Dashboard Streamlit Cloud lendo dados do GCS com módulos: análise de partida, perfil de time, H2H, odds, sentimento, tabela |
| **MUST** | Percentuais da análise calibrados contra odds implícitas dos bookmakers para identificar value bets |
| **SHOULD** | Histórico temporal de sentimento por seleção (série de scores ao longo dos dias/semanas) |
| **SHOULD** | Módulo de artilheiros, passes e defesas mais vazadas (atual + histórico de Copas) |
| **SHOULD** | Alertas automáticos de jogadores-chave ausentes na análise de partida |
| **COULD** | Botão "Refresh agora" que força recoleta sob demanda para uma seleção específica |
| **COULD** | Exportar análise de partida como PDF/markdown |

---

## Success Criteria

- [ ] Pipeline coleta dados dos 48 times e faz upload para GCS em < 15 minutos por execução
- [ ] Análise completa de uma partida (3 cenários + narrativa) gerada em < 30 segundos no Streamlit
- [ ] Custo mensal total < $10 (storage GCS + LLM calls) fora do período da Copa
- [ ] Notícias processadas em ≥ 10 idiomas diferentes via XLM-RoBERTa + Haiku
- [ ] Score de sentimento disponível para ≥ 90% dos 48 times com dados de pelo menos 48h
- [ ] H2H histórico disponível para qualquer par de seleções que já se enfrentou em Copa do Mundo (1930–2022)
- [ ] Dashboard operacional e acessível via Streamlit Cloud antes de julho de 2026

---

## Acceptance Tests

| ID | Tipo | Cenário | Given | When | Then |
|----|------|---------|-------|------|------|
| AT-001 | ✅ Happy Path | Análise completa de partida | Dados de BRA e FRA disponíveis no GCS (coletados nas últimas 24h), odds disponíveis | Usuário seleciona "Brasil" e "França" e clica "Analisar" | Dashboard exibe 3 cenários (ex: BRA 62% / Empate 24% / FRA 14%), narrativa para cada, morale scores, H2H resumido e alertas de lesões — tudo em < 30s |
| AT-002 | ❌ Error Case | API de dados indisponível durante coleta | Pipeline roda às 6h, football-data.org retorna 429 (rate limit) | Collector tenta coletar dados de forma e recebe erro | Collector registra o erro, usa dados do cache GCS do dia anterior, continua com demais seleções sem crash; log indica quais times usaram cache |
| AT-003 | ↩ Rollback | Upload parcial para GCS | Pipeline coletou 48 times mas network falha na metade do upload (24/48 enviados) | Erro de rede durante upload ao GCS | Dados existentes no GCS não são sobrescritos; pipeline salva progresso localmente; próxima execução retoma a partir dos times não enviados; usuário vê dados completos da execução anterior |
| AT-004 | 🔲 Edge Case | Times sem histórico H2H | Canada e Panama nunca se enfrentaram em Copa do Mundo | Usuário seleciona os dois para análise | Dashboard exibe "Sem histórico de confrontos diretos em Copa do Mundo" no módulo H2H; análise prossegue com os outros 4 sinais; LLM menciona ausência de H2H na narrativa |
| AT-005 | 🔲 Edge Case | Seleção sem cobertura de notícias | Saudi Arabia tem zero artigos no Google News RSS nas últimas 48h | Pipeline de sentimento tenta coletar notícias da Arábia Saudita | Score de sentimento marcado como "Sem dados suficientes (< 3 artigos)"; análise de partida prossegue sem componente de sentimento para esse time; LLM cita ausência na narrativa de incerteza |
| AT-006 | ❌ Error Case | Cota de API-Football esgotada | 100 calls/dia já consumidos antes de coletar todos os times | Collector tenta buscar squad/injuries e recebe 429 | Collector para imediatamente, preserva dados já coletados, registra quais times ficaram sem atualização, usa dados do GCS para os restantes |

### Scenario: AT-001 — Análise completa de partida

**Given** dados de Brasil e França existem no GCS (coletados na última execução < 24h): form.json, squad.json, sentiment/history.json, e odds do dia disponíveis no bucket  
**When** usuário acessa o dashboard Streamlit Cloud, navega para "Análise de Partida", seleciona Brasil e França, clica em "Analisar"  
**Then** o dashboard exibe dentro de 30 segundos:
- Card "Brasil vence" com percentual, ex: 62%
- Card "Empate" com percentual, ex: 24%  
- Card "França vence" com percentual, ex: 14%
- Narrativa de 3-5 parágrafos explicando cada cenário
- Tabela de comparação: forma, ranking FIFA, gols marcados/sofridos
- Score de sentimento de vestiário (0-10) para cada seleção com tendência
- Alertas de lesões/suspensões para jogadores-chave
- Comparação de odds implícitas vs. percentuais do sistema (value bet highlight)

---

### Scenario: AT-002 — API de dados indisponível

**Given** pipeline inicia execução às 06:00 com 0 erros até o momento; football-data.org começa a retornar HTTP 429  
**When** collector de "form" tenta buscar últimos 10 jogos da 15ª seleção da fila  
**Then** o sistema registra `WARNING: football-data.org rate limited, using cached data for {team}`, carrega form.json do GCS como fallback, continua execução para as seleções restantes sem interrupção; ao final, log de execução lista quais times usaram cache vs. dados frescos

---

### Scenario: AT-003 — Rollback de upload parcial

**Given** pipeline concluiu coleta local para todos os 48 times; iniciou upload para GCS e enviou 24 times com sucesso; na 25ª seleção, conexão de rede cai  
**When** `google.cloud.exceptions.ServiceUnavailable` é levantada  
**Then** upload é abortado sem sobrescrever os arquivos já existentes no GCS para as 24 restantes; pipeline salva em `data/.upload_progress.json` quais times foram enviados com sucesso; próxima execução detecta o arquivo de progresso e retoma apenas os pendentes; durante o período sem upload completo, Streamlit usa os dados da coleta anterior intactos

---

## Out of Scope

- **Apache Kafka / Pinot / Flink** — volume de < 1.000 registros/dia não justifica infraestrutura de streaming
- **Cloud Composer / Airflow gerenciado** — custo de $300/mês desnecessário; pipeline local é suficiente
- **Banco de dados** (PostgreSQL, Firestore, BigQuery) — file-based no GCS cobre todos os casos de uso do MVP
- **API paga do Twitter/X** — Reddit RSS e Google News RSS cobrem sentimento sem custo
- **Análise ao vivo durante partidas** — MVP é exclusivamente pré-jogo; in-game analytics é feature futura
- **Notificações (WhatsApp, email, push)** — pós-MVP
- **Treinamento de modelo ML próprio** — LLM reasoning supera ML clássico para dados não-estruturados
- **Scraping de sites** (TransferMarkt, FBRef direto) — risco de bloqueio; APIs free cobertas são suficientes
- **Multi-usuário / autenticação** — uso pessoal; Streamlit Cloud sem auth é aceitável

---

## Constraints

| Tipo | Restrição | Impacto |
|------|-----------|---------|
| Custo | Total < $10/mês (LLM + GCS) | LLM de volume via Haiku; Sonnet só para análise final; GCS free tier suficiente |
| Storage | File-based JSON/CSV no GCS; sem banco de dados | Design deve evitar queries relacionais; tudo resolvível com leitura de JSON |
| API — football-data.org | 10 calls/minuto (free tier) | Collector deve ter throttling com `time.sleep(6)` entre chamadas |
| API — API-Football | 100 calls/dia (free tier) | Cache agressivo obrigatório; só atualiza squad/injuries quando dado tem > 24h |
| API — The Odds API | 500 requisições/mês (free tier) | Coletar odds 1x/dia por partida agendada; cache de 12h mínimo |
| Compute | Pipeline roda em máquina local Windows | Windows Task Scheduler; scripts Python devem ser tolerantes a falhas de rede |
| LLM — Sentimento | XLM-RoBERTa roda em CPU local | Sem GPU; tempo de inferência aceitável (< 1s/artigo em CPU) |
| LLM — Análise | Claude Haiku para volume; Sonnet 4.6 para análise final | Haiku: triagem de sentimento; Sonnet: predição de partida com 3 cenários |
| Deploy | Streamlit Cloud (free tier) | App deve autenticar no GCS via Streamlit Secrets (service account JSON) |
| Timeline | Dashboard operacional antes de julho de 2026 | Copa começa em junho de 2026 |

---

## Technical Context

| Aspecto | Valor | Notas |
|---------|-------|-------|
| **Estrutura de código** | `src/collectors/`, `src/analyzers/`, `src/pipeline/`, `dashboard/` | Separação clara por responsabilidade |
| **Storage** | GCS bucket `gs://bolao-copa-2026/` | JSON/CSV; estrutura de diretórios por seleção e por data |
| **LLMs utilizados** | Claude Haiku 4.5 (volume) + Claude Sonnet 4.6 (análise final) | Haiku: $0.00025/1K tokens; Sonnet: $0.003/1K tokens |
| **Modelo de sentimento** | `cardiffnlp/twitter-xlm-roberta-base-sentiment` via HuggingFace | Multilíngue, grátis, roda local em CPU |
| **KB Domains** | `gcp` (GCS patterns), `agents` (LLM design patterns), `pydantic` (modelos de dados) | Consultar durante Design |
| **IaC Impact** | GCS bucket + service account (criação manual ou Terraform simples) | Sem Cloud Run ou Composer no MVP |
| **Orchestration** | Windows Task Scheduler → `python src/pipeline/run_daily.py` | Sem Airflow; script único com retry logic interno |

### Estrutura de Dados no GCS

```
gs://bolao-copa-2026/
  teams/
    {COD_FIFA}/                        # BRA, FRA, ARG, ESP, etc.
      profile.json                     # nome, ranking FIFA, confederação, grupo
      form.json                        # últimos 10 jogos: W/D/L, gols, adversário
      squad.json                       # elenco atual + status: fit/injured/doubtful/suspended
      stats.json                       # artilheiros, passes, defesas da temporada
      news/
        {YYYY-MM-DD}.json              # artigos do dia resumidos pelo LLM
      sentiment/
        history.json                   # série temporal: [{date, score, dimensions, alerts}]
  matches/
    h2h/
      {COD1}_vs_{COD2}.json            # histórico completo de confrontos (ordenado alfa)
    wc2026/
      groups/
        {COD1}_vs_{COD2}_analysis.json
      r16/
        {COD1}_vs_{COD2}_analysis.json
      qf/ sf/ f/
  odds/
    {YYYY-MM-DD}/
      {COD1}_vs_{COD2}.json            # odds de múltiplos bookmakers + implied probability
  history/
    wc_results_1930_2022.json          # todos os resultados de Copa (Kaggle bulk)
    wc_top_scorers.json                # artilheiros históricos de Copa
    wc_team_stats.json                 # estatísticas históricas por seleção em Copas
  _meta/
    last_updated.json                  # timestamp da última coleta bem-sucedida
    collection_log.json                # log das últimas 7 execuções do pipeline
```

### Fontes de Dados Mapeadas

| Sinal | Fonte | Endpoint Chave | Limite Free | Estratégia de Cache |
|-------|-------|----------------|-------------|---------------------|
| Histórico + Form | football-data.org | `/matches`, `/standings` | 10 calls/min | Atualizar 1x/dia; histórico é imutável |
| Squad + Lesões | API-Football | `/players`, `/injuries` | 100 calls/dia | Atualizar apenas se dado > 24h |
| Odds | The Odds API | `/odds` | 500 req/mês | 1x/dia por partida agendada; cache 12h |
| Notícias locais | Google News RSS | `?q={team}&hl={lang}&gl={country}` | Sem limite | Coletar últimas 48h, deduplicar por URL |
| Notícias extra | NewsAPI | `/everything?q={team}` | 100 req/dia | Complementar Google News; baixa prioridade |
| Sentimento comunidade | Reddit RSS | `r/worldcup`, `r/{country}soccer` | Sem limite | Últimas 24h de posts |
| Histórico bulk | Kaggle WC Dataset | Download único | Grátis | Download na inicialização; não recoleta |
| Dados ricos | StatsBomb Open Data | GitHub release | Grátis | Download na inicialização |

### Pipeline de Sentimento (Detalhado)

```
Artigo de notícia (qualquer idioma)
         ↓
XLM-RoBERTa → score bruto: positive/neutral/negative (0-1)
         ↓
Normalização → score 0-10 (0=muito negativo, 10=muito positivo)
         ↓
[Se score < 3 ou > 8]:
   Claude Haiku → extrai sinais estruturados:
   {
     "coesao_grupo": 7,
     "pressao_media": 8,
     "motivacao": 9,
     "confianca_tecnico": 6,
     "alertas": ["Striker dúvida por lesão muscular", "Conflito com federação"]
   }
         ↓
Agregação diária → score composto por seleção
         ↓
GCS: teams/{COD}/sentiment/history.json (append)
```

### Formato de Output da Análise de Partida

O sistema prevê **placares específicos com probabilidades**, não apenas outcomes (vitória/empate/derrota). Isso permite identificar value bets em mercados de placar exato, que os bookmakers precificam com maior margem e portanto oferecem mais oportunidade.

```json
{
  "match": "BRA vs FRA",
  "generated_at": "2026-06-20T10:30:00Z",
  "cached_until": "2026-06-21T06:00:00Z",
  "scoreline_predictions": [
    {
      "scoreline": "Brasil 2x0 França",
      "probability": 0.22,
      "market_implied": 0.14,
      "value": "+8pp vs mercado ⭐ VALUE BET",
      "narrative": "Brasil domina defensivamente (média 0.8 gols sofridos/jogo) e tem poder ofensivo consolidado. Com Mbappé como dúvida, França perde 40% do seu xG histórico..."
    },
    {
      "scoreline": "Brasil 1x0 França",
      "probability": 0.18,
      "market_implied": 0.16,
      "value": "+2pp vs mercado",
      "narrative": "Cenário de jogo equilibrado com Brasil mais eficiente na única chance..."
    },
    {
      "scoreline": "Brasil 1x1 França",
      "probability": 0.15,
      "market_implied": 0.18,
      "narrative": "Empate mais provável dado histórico de 3 empates nos últimos 5 confrontos em Copa..."
    },
    {
      "scoreline": "França 1x0 Brasil",
      "probability": 0.12,
      "market_implied": 0.15,
      "narrative": "Cenário de surpresa: França historicamente melhora em eliminatórias..."
    }
  ],
  "outcome_summary": {
    "brasil_vence": 0.58,
    "empate": 0.22,
    "franca_vence": 0.20
  },
  "signals_used": {
    "h2h": {
      "total_matches": 14,
      "bra_wins": 7, "draws": 3, "fra_wins": 4,
      "common_scorelines": ["1x0", "2x1", "1x1"],
      "avg_goals_per_match": 2.4
    },
    "form_bra": {"last10": "7W-2D-1L", "goals_scored": 22, "goals_conceded": 8, "avg_goals": 2.2},
    "form_fra": {"last10": "6W-3D-1L", "goals_scored": 18, "goals_conceded": 9, "avg_goals": 1.8},
    "sentiment_bra": {"score": 8.2, "trend": "↑", "alerts": []},
    "sentiment_fra": {"score": 6.1, "trend": "↓", "alerts": ["Mbappé dúvida (muscular)"]},
    "odds_source": "Pinnacle/Bet365",
    "data_freshness": "< 18h"
  }
}
```

**Lógica de predição de placar:**
1. LLM calcula média de gols marcados/sofridos de cada time (últimos 10 jogos + H2H histórico)
2. Ajusta pela força do adversário (ranking FIFA + forma recente)
3. Penaliza/bonifica por alertas de sentimento (lesões, motivação)
4. Gera distribuição de placares mais prováveis (top 4-6 scorelines cobrindo ~70% da probabilidade)
5. Compara cada placar com odds implícitas dos bookmakers para flagrar value bets

---

## Módulos do Dashboard Streamlit

### M1 — Análise de Partida (tela principal)
- Seletor: Time A vs Time B (dropdown com 48 seleções)
- Botão "Analisar" → chama Claude Sonnet 4.6 com contexto completo do GCS
- 3 cards de resultado com %, narrativa expandível por cenário
- Painel de value bet (probabilidade sistema vs. odds implícitas)
- Resumo de sinais utilizados (transparência)

### M2 — Perfil de Seleção
- Seletor de time → carrega dados do GCS
- Últimos 10 jogos (mini-tabela com resultado, adversário, placar, competição)
- Elenco com status (fit / doubtful / injured / suspended) por posição
- Artilheiros da seleção (top 10)
- Jogadores com mais passes (top 5 playmakers)

### M3 — H2H Explorer
- Seletor de dois times → carrega `h2h/{COD1}_vs_{COD2}.json`
- Tabela de confrontos históricos com filtros: Copa do Mundo / Amistosos / Todos
- Gráfico de distribuição de resultados
- Estatísticas agregadas: total de jogos, vitórias A/B/empates, gols

### M4 — Monitor de Odds
- Tabela de partidas agendadas com odds atuais (Bet365, Pinnacle, bet365)
- Probabilidade implícita calculada (odds → %)
- Destaque de divergência entre sistema e mercado (value bets)

### M5 — Sentimento de Vestiário
- Mapa de calor de sentimento por seleção (0-10, colorido)
- Série temporal de score por seleção (linha chart)
- Feed de alertas recentes (ordenado por impacto)
- Detalhamento: coesão, pressão de mídia, motivação, confiança no técnico

### M6 — Tabela da Copa 2026
- Classificação por grupo em tempo real
- Artilheiros do torneio
- Defesas menos vazadas
- Histórico de campeões (1930–2022)

---

## Assumptions

| ID | Assumption | Se Errada, Impacto | Validado? |
|----|------------|---------------------|-----------|
| A-001 | football-data.org API estará disponível e estável durante a Copa 2026 | Precisaria de fonte alternativa (API-Football como fallback) | [ ] |
| A-002 | Google News RSS retorna artigos por país/idioma sem autenticação ou bloqueio | Precisaria de NewsAPI pago como substituto | [ ] |
| A-003 | API-Football free tier de 100 calls/dia é suficiente para 48 times (estima-se 48-96 calls/execução diária com cache agressivo) | Precisaria otimizar ainda mais ou pagar tier básico ($15/mês) | [ ] |
| A-004 | XLM-RoBERTa roda em CPU Windows sem GPU com performance aceitável (< 2s/artigo) | Precisaria de API externa de sentimento (ex: HuggingFace Inference API grátis) | [ ] |
| A-005 | Streamlit Cloud autentica no GCS via Streamlit Secrets sem expor service account key | Arquitetura de autenticação deve ser validada no Design | [ ] |
| A-006 | Kaggle WC Dataset histórico (1930-2022) está completo e em formato utilizável | Precisaria de limpeza manual ou fonte alternativa | [ ] |
| A-007 | The Odds API free tier de 500 req/mês é suficiente (estimativa: ~1-3 req/partida × ~65 partidas Copa = ~195 req durante torneio) | Margem existe; mas pré-Copa pode consumir parte da cota | [ ] |

---

## Open Questions

| ID | Prioridade | Pergunta | Quem responde | Status |
|----|------------|----------|---------------|--------|
| Q-001 | 🟡 High | Autenticação GCS no Streamlit Cloud: Design deve avaliar Streamlit Secrets (JSON da service account como secret) vs. Workload Identity; se complexo, criar agente especialista em GCP auth | Design phase | In Progress → Design resolverá |
| Q-002 | ✅ Answered | API-Football: focar exclusivamente em seleções nacionais; dados de clube só se necessário para histórico de jogador específico para sentimento | Usuário | Answered |
| Q-003 | ✅ Answered | Idioma: iniciar com PT-BR como prioritário; Design pode revisar estratégia multilíngue e XLM-RoBERTa cobre PT-BR nativamente | Usuário | Answered |
| Q-004 | ✅ Answered | Kaggle qualificatórias: incluir se disponível no dataset; H2H geral enriquece a análise sem custo adicional | Usuário | Answered |
| Q-005 | 🟢 Low | Reddit subreddits por país: Design mapeará os principais; para países sem subreddit ativo, Google News RSS é suficiente | Design phase | Deferred |

---

## Clarity Score Breakdown

| Elemento | Score | Justificativa |
|----------|-------|---------------|
| Problema | 3/3 | Específico: apostadores sem vantagem informacional; solução clara: informação assimétrica via notícias locais |
| Usuários | 3/3 | 3 personas com papéis e dores distintas; primário identificado |
| Goals | 3/3 | MoSCoW completo; MUSTs não-negociáveis definidos; SHOULDs e COULDs diferenciados |
| Sucesso | 3/3 | Métricas numéricas: < 30s, < $10/mês, ≥ 10 idiomas, ≥ 90% cobertura, < 15min pipeline |
| Escopo | 3/3 | Out-of-scope explícito e confirmado no brainstorm; constraints por API documentadas |
| **Total** | **15/15** | |

---

## Revision History

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 2026-06-19 | define-agent | Versão inicial extraída do BRAINSTORM_COPA2026_ANALYZER.md |
| 1.1 | 2026-06-19 | define-agent | Output reformatado: placares específicos (BRA 2x0 FRA 22%) em vez de só outcomes; Q-002/003/004 respondidas; Q-001 delegada ao Design |

---

## Next Step

**Pronto para:** `/design .claude/sdd/features/DEFINE_COPA2026_ANALYZER.md`
