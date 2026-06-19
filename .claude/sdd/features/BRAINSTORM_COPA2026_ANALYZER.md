# BRAINSTORM: Analisador de Resultados Copa do Mundo 2026

> Sessão exploratória para clarificar intenção e abordagem antes da captura de requisitos

## Metadata

| Atributo | Valor |
|----------|-------|
| **Feature** | COPA2026_ANALYZER |
| **Data** | 2026-06-19 |
| **Autor** | brainstorm-agent |
| **Status** | Abordagem Selecionada — Pronto para Define |

---

## Ideia Inicial

**Input original:** Criar um analisador de possibilidades de resultados da Copa do Mundo 2026 analisando: histórico de partidas, time atual, manchetes sobre jogadores (lesão, tratamento, notícias privilegiadas locais), odds de apostas, e "sentimento de vestiário" (o que a estatística não mostra). Sistema apresentado em dashboard Streamlit com custo mínimo.

**Contexto do projeto observado:**
- Projeto `bolao_copa` — novo, sem código existente
- Stack do template: Python, GCP, LLMs
- Sem banco de dados preferido — arquivo-first por decisão explícita do usuário
- Orçamento: mínimo possível (uso pessoal + pesquisa técnica)

**Contexto técnico (para Define):**

| Aspecto | Observação | Implicação |
|---------|------------|------------|
| Localização do código | `src/collectors/`, `src/analyzers/`, `dashboard/` | Separação clara por responsabilidade |
| KB relevantes | agents, bigquery (opcional), gcp | Padrões de LLM e storage |
| IaC | N/A no MVP — local-first | GCS sync entra na Fase 2 |

---

## Perguntas de Descoberta e Respostas

| # | Pergunta | Resposta | Impacto |
|---|----------|----------|---------|
| 1 | Objetivo principal | Uso pessoal (bolão/bets) + vantagem estatística + pesquisa técnica | Sistema precisa ser preciso E barato — LLM barato + APIs gratuitas |
| 2 | Escopo de seleções | Todas as 48 da Copa 2026 (dinâmico, qualquer partida) | Dados pré-computados por seleção, atualizados diariamente |
| 3 | Sinais determinantes | Todos: H2H, forma, lesões, odds globais + noticiários locais de cada país | 5 camadas de dados; notícias locais = diferencial estratégico |
| 4 | Como consumir a análise | Dashboard Streamlit | UI visual side-by-side, não chat nem PDF |
| 5 | MVP vs completo | Tudo junto desde o início, construção correta | Feature set completo, priorizando pipeline limpa |
| 6 | Infra local vs cloud | Rodar pipeline localmente, só subir arquivos para nuvem | Custo zero de compute; GCS como backup/compartilhamento opcional |

---

## Inventário de Amostras

| Tipo | Local | Quantidade | Observações |
|------|-------|------------|-------------|
| Dados históricos | N/A — partir do zero | 0 | Coletar via football-data.org + Kaggle WC datasets |
| Elenco atual | N/A | 0 | Coletar via API-Football |
| Ground truth | N/A | 0 | Resultados históricos das Copas são ground truth implícito |
| Código relacionado | N/A | 0 | Projeto novo |

**Como as amostras serão usadas após coleta:**
- Dados históricos → few-shot examples no prompt LLM de análise de confrontos
- Resultados passados de Copa → validação de acurácia do modelo preditivo
- Notícias coletadas → grounding do LLM para scoring de sentimento

---

## Abordagens Exploradas

### Approach A: "Pipeline Local → GCS → Streamlit Cloud" ⭐ Selecionado

**Descrição:** Pipeline Python que roda localmente via Windows Task Scheduler, coleta dados de APIs gratuitas e RSS de notícias locais por país/idioma, processa sentimento com XLM-RoBERTa (grátis, local) + Claude Haiku (extração de sinais), gera análise final com Claude Sonnet 4.6, e persiste tudo em GCS. Streamlit Cloud lê diretamente do GCS.

```
Fontes gratuitas (RSS + APIs)
         ↓
Python Collectors (Task Scheduler local, diário, 5-10 min)
         ↓
XLM-RoBERTa local → sentiment score 0-10 (grátis)
         ↓ (se score extremo)
Claude Haiku → extração de sinais (lesões, conflitos, motivação)
         ↓
JSON/CSV → GCS bucket (upload após coleta)
         ↓
Claude Sonnet 4.6 → análise de partida sob demanda
         ↓
Streamlit Cloud → lê GCS direto → dashboard público/privado
```

**Fontes de dados mapeadas:**

| Sinal | Fonte | Custo | Limite free |
|-------|-------|-------|-------------|
| Histórico partidas + form | football-data.org | Grátis | 10 calls/min |
| Jogadores + lesões | API-Football | Grátis | 100 calls/dia |
| Odds globais | The Odds API | Grátis | 500 req/mês |
| Notícias locais (todos os países) | Google News RSS (por país + idioma) | Grátis | Sem limite |
| Notícias complementares | NewsAPI | Grátis | 100 req/dia |
| Dados históricos ricos | StatsBomb Open Data (GitHub) | Grátis | Sem limite |
| Copas históricas bulk | Kaggle WC Datasets | Grátis | Download único |
| Sentimento comunidades | Reddit RSS (r/worldcup, r/brazil, etc.) | Grátis | Sem limite |

**Pipeline de sentimento (híbrido, custo mínimo):**
- XLM-RoBERTa (`cardiffnlp/twitter-xlm-roberta-base-sentiment`) — multilíngue, grátis, roda local: score rápido 0-10 por artigo
- Claude Haiku — acionado apenas para artigos com score extremo (< 3 ou > 8): extração profunda de sinais (lesões, conflitos, motivação, pressão de federação)
- Output estruturado: `{ coesao: 7, pressao_media: 4, motivacao: 9, alertas: ["Neymar dúvida", "conflito com comissão"] }`
- Histórico temporal: série de scores por seleção para detectar tendências

**Análise de partida com 3 resultados (Claude Sonnet 4.6):**
- Integra todos os 5 sinais: H2H + forma + lesões + odds + sentimento
- Output: resultado mais provável (%) + 2 alternativas (%) + narrativa de cada cenário
- Percentuais calibrados contra odds implícitas dos bookmakers (detecta value bets)
- Exemplo de output:
  ```
  🏆 Brasil vence: 62% | ⚖️ Empate: 24% | ⚠️ Adversário: 14%
  ```
- Custo estimado: ~$0.05/análise com Sonnet; ~$0.03/dia pipeline de sentimento com Haiku

**Pros:**
- Custo mensal: ~$0-5 (só LLM calls, zero compute)
- Dados pré-calculados → Streamlit instantâneo
- Notícias em idioma nativo = vantagem não capturada pelos mercados globais
- Funciona offline após coleta diária
- Arquivos portáveis — sem lock-in de banco de dados

**Cons:**
- Setup inicial de 2-3 dias para conectar todas as fontes
- PC/laptop deve estar ligado para o scheduler rodar (resolvido na Fase 2)
- Dados com delay de até 24h (aceitável para análise pré-jogo)

---

### Approach B: "On-Demand puro"

**Descrição:** Sem pré-computação. Streamlit busca tudo ao vivo quando o usuário seleciona uma partida.

**Por que não recomendado:** Consome cota de API 10x mais rápido, latência de 30-60s por consulta, impossível rastrear evolução de sentimento ao longo do tempo. Boa como feature auxiliar ("refresh agora"), não como arquitetura principal.

---

### Approach C: "ML clássico com features manuais"

**Descrição:** XGBoost/RandomForest treinado em dados históricos de Copas (1930-2022).

**Por que não recomendado:** Modelos clássicos não conseguem processar notícias e lesões em tempo real. O alpha real está em informação assimétrica (notícia local antes do mercado reagir), não em estatísticas públicas que os mercados já precificaram.

---

## Abordagem Selecionada

| Atributo | Valor |
|----------|-------|
| **Escolhida** | Approach A |
| **Confirmação** | 2026-06-19 |
| **Motivação** | Única abordagem que combina dado estruturado + não-estruturado (notícias locais em qualquer idioma) com custo mínimo e arquitetura local-first |

---

## Decisões-Chave Tomadas

| # | Decisão | Racional | Alternativa Rejeitada |
|---|---------|----------|-----------------------|
| 1 | Arquivos JSON/CSV no GCS desde o início | ~$0.01/mês storage; Streamlit Cloud acessa diretamente; pipeline roda local mas dados ficam na nuvem | PostgreSQL, Firestore, BigQuery |
| 2 | GCS desde MVP (não apenas Fase 2) | Streamlit Cloud precisa de fonte acessível publicamente; GCS resolve sem custo relevante | Local-only (impossibilitaria Streamlit Cloud) |
| 3 | Cloud Scheduler + Cloud Run (Fase 2), não Airflow/Composer | Composer custa ~$300/mês; Cloud Scheduler é $0.10/job | Cloud Composer, Airflow self-hosted em VM |
| 4 | Kafka + Apache Pinot removidos | YAGNI: nosso volume é <1.000 eventos/dia; Kafka é para milhões/segundo | Streaming em tempo real |
| 5 | Híbrido XLM-RoBERTa (local, grátis) + Claude Haiku (sinais) + Claude Sonnet 4.6 (predição final) | XLM-RoBERTa processa volume sem custo; Haiku aprofunda só quando necessário; Sonnet dá melhor raciocínio multi-fator na predição final | GPT-4o, Claude Sonnet em tudo (caro), modelo customizado (complexo) |
| 6 | Feature set completo desde MVP | Copa começa em junho; melhor construir certo uma vez do que iterar | MVP enxuto → expansão |

---

## Features Removidas (YAGNI)

| Feature Sugerida | Razão Removida | Pode Adicionar? |
|------------------|----------------|-----------------|
| Apache Kafka | Volume de dados não justifica; complexidade e custo desnecessários | Sim (se escalar para produto público) |
| Apache Pinot | OLAP real-time desnecessário; Streamlit + JSON é suficiente | Sim (V3, produto público) |
| Cloud Composer (Airflow gerenciado) | $300/mês para orquestrar 5-10 min de script = desperdício | Sim (produto empresarial) |
| Scores ao vivo durante partidas | MVP é pré-jogo; análise ao vivo é complexidade diferente | Sim (V2) |
| Integração WhatsApp/notificações | Não foi solicitado para MVP | Sim (V2 fácil) |
| Treinamento de modelo ML próprio | LLM reasoning supera ML clássico para dados não-estruturados | Sim (pesquisa futura) |
| Social media Twitter/X | API cara ($100+/mês básico) | Sim (Reddit é gratuito e suficiente) |

---

## Features do Dashboard — Escopo Completo

### Módulo 1: Análise de Partida (core)
- Seleção de duas equipes → análise side-by-side
- Odds comparadas de múltiplos bookmakers
- Recomendação do agente com grau de confiança (%)
- Score de sentimento de vestiário (0-10) para cada seleção

### Módulo 2: Estatísticas por Seleção
- Forma atual (últimos 10 jogos: W/D/L, gols marcados/sofridos)
- H2H histórico: Copa do Mundo + partidas gerais
- Defesas mais vazadas (atual + histórico)
- Times com mais gols (atual + histórico)

### Módulo 3: Jogadores
- Status de lesões e suspensões por seleção
- Artilheiros da seleção (atual + histórico em Copas)
- Jogadores com mais passes (playmakers)
- Alertas de jogadores-chave ausentes

### Módulo 4: Sentimento e Notícias
- Feed de notícias locais (últimas 48h) por seleção
- Score de sentimento de vestiário com histórico
- Alertas de "surpresa" gerados pelo LLM
- Sinalização de fatores psicológicos: pressão, conflitos, motivação

### Módulo 5: Tabela Completa Copa 2026
- Classificação em tempo real
- Estatísticas por grupo
- Artilheiros do torneio
- Histórico de campeões da Copa

---

## Arquitetura de Arquivos (Storage Schema)

```
data/
  teams/
    {COD_FIFA}/           # BRA, FRA, ARG, etc.
      profile.json        # info base: nome, ranking FIFA, confederação
      form.json           # últimos 10 jogos
      squad.json          # elenco atual + status jogadores
      stats.json          # artilheiros, passes, defesas
      news/
        {YYYY-MM-DD}.json # notícias do dia (resumidas pelo LLM)
      sentiment/
        history.json      # série temporal do score de sentimento
  matches/
    h2h/
      {COD1}_vs_{COD2}.json  # histórico de confrontos
    WC2026/
      {fase}/
        {COD1}_vs_{COD2}_analysis.json  # análise pré-jogo completa
  odds/
    {YYYY-MM-DD}/
      {COD1}_vs_{COD2}.json
  history/
    wc_results_1930_2022.csv    # bulk Kaggle
    wc_top_scorers.json
    wc_team_stats.json
```

---

## Validações Incrementais

| Seção | Apresentada | Feedback do Usuário | Ajustado? |
|-------|-------------|---------------------|-----------|
| Stack tech + YAGNI (Kafka/Airflow) | ✅ | Aprovado | Sim — local-first adicionado |
| Abordagens A/B/C | ✅ | Selecionou A | N/A |
| MVP vs V2 | ✅ | Feature set completo desde início | Sim — escopo expandido |
| Local vs Cloud | ✅ | Local pipeline + GCS opcional | Sim — arquitetura híbrida 3 fases |

---

## Requisitos Rascunhados para /define

### Problema (Draft)
Predizer resultados de partidas da Copa do Mundo 2026 combinando estatísticas históricas, forma atual, status de jogadores, odds de bookmakers e sentimento de vestiário capturado em noticiários locais de cada país, apresentado em dashboard Streamlit de custo mínimo.

### Usuários Alvo
| Usuário | Dor |
|---------|-----|
| Apostador pessoal | Falta de vantagem informacional sobre o mercado |
| Participante de bolão | Palpites baseados em feeling, não em dados |
| Pesquisador técnico | Quer explorar pipeline LLM + dados esportivos |

### Critérios de Sucesso (Draft)
- [ ] Coletar dados dos 48 times da Copa 2026 automaticamente (sem intervenção manual)
- [ ] Processar notícias em pelo menos 10 idiomas diferentes via LLM
- [ ] Score de sentimento de vestiário com histórico temporal por seleção
- [ ] Análise de partida completa gerada em < 30 segundos
- [ ] Custo mensal total < $10 (excluindo período da Copa)
- [ ] Dashboard operacional antes do início da Copa (junho 2026)

### Restrições Identificadas
- Sem banco de dados (file-based obrigatório)
- Sem Cloud Run / Composer no MVP (local-first)
- APIs gratuitas apenas, sem assinatura paga de dados esportivos
- LLM de baixo custo (Haiku); Sonnet apenas para análises críticas
- The Odds API free tier: 500 req/mês (gerenciar cuidadosamente)
- API-Football free tier: 100 calls/dia (requer cache agressivo)

### Fora do Escopo (Confirmado)
- Kafka, Apache Pinot, Apache Flink (overkill)
- Cloud Composer / Airflow gerenciado (custo)
- Modelo de ML próprio treinado
- API paga do Twitter/X
- Análise ao vivo durante as partidas (pós-MVP)
- Notificações WhatsApp/email (pós-MVP)

---

## Resumo da Sessão

| Métrica | Valor |
|---------|-------|
| Perguntas feitas | 6 |
| Abordagens exploradas | 3 |
| Features removidas (YAGNI) | 7 |
| Validações completadas | 4 |
| Custo estimado MVP | $0-5/mês |
| Stack final | Python + Task Scheduler + JSON files + Streamlit + Claude Haiku |

---

## Próximo Passo

**Pronto para:** `/define .claude/sdd/features/BRAINSTORM_COPA2026_ANALYZER.md`
