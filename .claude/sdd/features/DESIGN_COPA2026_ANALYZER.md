# DESIGN: Analisador de Resultados Copa do Mundo 2026

> Pipeline local → GCS → Streamlit Cloud com predição de placares específicos via LLM multi-sinal

## Metadata

| Atributo | Valor |
|----------|-------|
| **Feature** | COPA2026_ANALYZER |
| **Data** | 2026-06-19 |
| **Autor** | design-agent |
| **DEFINE** | [DEFINE_COPA2026_ANALYZER.md](./DEFINE_COPA2026_ANALYZER.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       COPA 2026 ANALYZER — SYSTEM                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  PIPELINE LOCAL (Windows Task Scheduler → 06:00 diário, ~10 min)             │
│                                                                               │
│  football-data.org ──┐                                                       │
│  API-Football ────────┼──► src/collectors/ ──► src/analyzers/               │
│  The Odds API ────────┤         │                     │                      │
│  Google News RSS ─────┤     raw JSON             XLM-RoBERTa                │
│  Reddit RSS ──────────┘     local temp          sentiment 0-10               │
│                               data/               │                          │
│                                 │           [score < 3 ou > 8]               │
│                                 │                  ▼                         │
│                                 │           Claude Haiku                     │
│                                 │           signal extraction                │
│                                 │                  │                         │
│                                 └──────────────────┘                         │
│                                          │                                   │
│                                          ▼                                   │
│                              src/storage/gcs.py (upload)                    │
│                                          │                                   │
│                         gs://bolao-copa-2026/ (GCS Bucket)                  │
│                                          │                                   │
├──────────────────────────────────────────┼───────────────────────────────────┤
│                                          │                                   │
│  STREAMLIT CLOUD (lê GCS via SA key)     │                                   │
│                                          │                                   │
│  User selects match ──► Load from GCS ◄─┘                                   │
│          │                    │                                              │
│          │              teams/{COD}/                                         │
│          │              matches/h2h/                                         │
│          │              odds/{date}/                                         │
│          │              sentiment/history.json                               │
│          │                    │                                              │
│          ▼                    ▼                                              │
│   "Analisar" btn      context assembled                                      │
│          │                    │                                              │
│          └────────────────────┘                                              │
│                    │                                                         │
│                    ▼                                                         │
│            Claude Sonnet 4.6                                                 │
│         (match prediction prompt)                                            │
│                    │                                                         │
│          ScorelinePredictions[]                                              │
│    BRA 2x0 FRA 22% | BRA 1x0 FRA 18% | ...                                 │
│                    │                                                         │
│                    ▼                                                         │
│            dashboard/app.py                                                  │
│   ┌──────┬──────┬──────┬─────┬───────────┬─────────┐                       │
│   │  M1  │  M2  │  M3  │ M4  │    M5     │   M6    │                       │
│   │Match │Team  │ H2H  │Odds │ Sentiment │ Table   │                       │
│   └──────┴──────┴──────┴─────┴───────────┴─────────┘                       │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

| Componente | Propósito | Tecnologia |
|------------|-----------|------------|
| `src/collectors/football_data.py` | Busca histórico de partidas e forma atual | football-data.org API v4 |
| `src/collectors/api_football.py` | Busca elenco, lesões e stats de jogadores | API-Football v3 |
| `src/collectors/odds.py` | Busca odds de múltiplos bookmakers | The Odds API v4 |
| `src/collectors/news.py` | Coleta notícias locais por país/idioma | Google News RSS + Reddit RSS |
| `src/collectors/historical.py` | Download único de dados bulk históricos | Kaggle WC Dataset + StatsBomb |
| `src/analyzers/sentiment.py` | Pipeline híbrido de sentimento | XLM-RoBERTa (local) + Claude Haiku |
| `src/analyzers/match_analyzer.py` | Predição de placares com 3+ cenários | Claude Sonnet 4.6 |
| `src/storage/gcs.py` | Upload/download GCS com retry e rollback | google-cloud-storage SDK |
| `src/pipeline/run_daily.py` | Orquestrador do pipeline diário | Python script + progress tracking |
| `src/config.py` | Configurações centralizadas | Pydantic BaseSettings + .env |
| `dashboard/app.py` | Entry point Streamlit Cloud | Streamlit |
| `dashboard/pages/` | 6 módulos do dashboard | Streamlit multi-page |
| `dashboard/components/` | Componentes reutilizáveis | Streamlit + Plotly |
| `scripts/init_historical.py` | Script de inicialização única | Python + Kaggle API |

---

## Data Contract (Design Token)

| Token | Arquivo | Tipo | Owner | Downstream |
|-------|---------|------|-------|------------|
| `TeamProfile` | `src/schemas/team.py` | Pydantic | `collectors/football_data.py` | dashboard M2, M6 |
| `TeamForm` | `src/schemas/team.py` | Pydantic | `collectors/football_data.py` | match_analyzer, dashboard M2 |
| `TeamSquad` | `src/schemas/team.py` | Pydantic | `collectors/api_football.py` | match_analyzer, dashboard M2 |
| `TeamStats` | `src/schemas/team.py` | Pydantic | `collectors/api_football.py` | dashboard M2 |
| `SentimentRecord` | `src/schemas/sentiment.py` | Pydantic | `analyzers/sentiment.py` | match_analyzer, dashboard M5 |
| `SentimentHistory` | `src/schemas/sentiment.py` | Pydantic | `analyzers/sentiment.py` | dashboard M5 |
| `H2HHistory` | `src/schemas/match.py` | Pydantic | `collectors/football_data.py` | match_analyzer, dashboard M3 |
| `OddsSnapshot` | `src/schemas/match.py` | Pydantic | `collectors/odds.py` | match_analyzer, dashboard M4 |
| `ScorelinePrediction` | `src/schemas/match.py` | Pydantic | `analyzers/match_analyzer.py` | dashboard M1 |
| `MatchAnalysis` | `src/schemas/match.py` | Pydantic | `analyzers/match_analyzer.py` | dashboard M1, GCS cache |

**Schema drift rule:** Qualquer alteração nos schemas acima após o ship → abrir `DEFINE_SCHEMA_UPDATE_COPA2026.md` antes de qualquer PR.

**Campos críticos (mudança = breaking change):**

| Campo | Tipo | Restrições | Impacto de mudança |
|-------|------|-----------|-------------------|
| `ScorelinePrediction.scoreline` | `str` | formato `"BRA 2x0 FRA"` | quebra parsing no dashboard |
| `ScorelinePrediction.probability` | `float` | `ge=0, le=1` | quebra cálculo de value bet |
| `SentimentRecord.overall_score` | `float` | `ge=0, le=10` | quebra gauge e histórico |
| `H2HHistory.team_a` / `team_b` | `str` | sempre ordenados A-Z | quebra lookup de arquivo |

---

## Change Delta

### ADDED

| Item | Tipo | Localização | Por quê |
|------|------|-------------|---------|
| `TeamProfile`, `TeamForm`, `TeamSquad`, `TeamStats` | Pydantic schema | `src/schemas/team.py` | Contratos de dados de seleções |
| `SentimentRecord`, `SentimentHistory` | Pydantic schema | `src/schemas/sentiment.py` | Contrato de sentimento de vestiário |
| `H2HHistory`, `OddsSnapshot`, `ScorelinePrediction`, `MatchAnalysis` | Pydantic schema | `src/schemas/match.py` | Contratos de análise de partida |
| Todos os collectors | Python module | `src/collectors/` | Coleta de dados de fontes externas |
| Pipeline de sentimento híbrido | Python module | `src/analyzers/sentiment.py` | XLM-RoBERTa + Haiku |
| Match analyzer com Sonnet 4.6 | Python module | `src/analyzers/match_analyzer.py` | Predição de placares |
| GCS storage helpers | Python module | `src/storage/gcs.py` | Upload/download com retry |
| Pipeline diário | Python script | `src/pipeline/run_daily.py` | Orquestração |
| Dashboard Streamlit (6 páginas) | Streamlit app | `dashboard/` | Interface do usuário |
| GCS bucket `bolao-copa-2026` | GCP Infrastructure | GCP Console | Storage dos dados |
| 2 service accounts GCP | GCP Infrastructure | GCP Console | Auth pipeline + Streamlit |

### MODIFIED
None — projeto novo.

### REMOVED
None — projeto novo.

---

## Key Decisions

### Decision 1: Autenticação GCS no Streamlit Cloud via Streamlit Secrets

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Data** | 2026-06-19 |

**Context:** Streamlit Cloud precisa acessar GCS sem expor credenciais em código. Q-001 do DEFINE.

**Choice:** Dois service accounts separados + Streamlit Secrets para credenciais do dashboard.

**Rationale:** 
- `pipeline-writer` SA: tem `storage.objectCreator` + `storage.objectViewer`. Usado localmente via `GOOGLE_APPLICATION_CREDENTIALS` env var.
- `streamlit-reader` SA: tem apenas `storage.objectViewer` (read-only). Credenciais adicionadas como secret JSON no Streamlit Cloud Settings → Secrets.
- Separação de permissões segue least-privilege: Streamlit nunca consegue escrever no GCS.
- Streamlit Secrets suporta nativamente estruturas TOML com JSON embutido.

```toml
# Streamlit Cloud Settings → Secrets
[gcp_service_account]
type = "service_account"
project_id = "bolao-copa-2026"
private_key_id = "KEY_ID"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
client_email = "streamlit-reader@bolao-copa-2026.iam.gserviceaccount.com"
```

**Alternatives Rejected:**
1. Workload Identity Federation — requer Streamlit Cloud configurado como OIDC provider, complexidade desnecessária para uso pessoal
2. Public bucket — inseguro; expõe dados publicamente sem necessidade
3. Hardcoded credentials — violação de segurança básica

**Consequences:**
- Rotação de chave requer atualização manual no Streamlit Secrets (aceitável para uso pessoal)
- Separação de SA garante que um comprometimento do dashboard não expõe escrita

---

### Decision 2: Predição de Placares Específicos (não apenas outcomes)

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Data** | 2026-06-19 |

**Context:** Usuário quer "Brasil 1x0 Argentina 70%", não apenas "Brasil vence 70%". Mercados de placar exato têm margens maiores dos bookmakers = mais value bets potenciais.

**Choice:** Claude Sonnet 4.6 gera top 4-6 scorelines mais prováveis com % individuais. Sum dos top scorelines ≤ 70%; restante = "outros".

**Rationale:**
- Sonnet 4.6 consegue raciocinar sobre distribuição de gols usando média histórica de gols/jogo, H2H de placares e força defensiva
- Placares específicos somam probabilidades menores (ex: 22% + 18% + 15%...) mas cobrem os outcomes mais comercialmente relevantes
- LLM é instruído a calibrar contra odds implícitas: se mercado tem BRA 2x0 FRA em 8% e nosso modelo diz 22%, é sinal de value

**Alternatives Rejected:**
1. Modelo Poisson clássico (Dixon-Coles) — preciso, mas não incorpora sentimento/lesões; seria ML clássico sem LLM
2. Apenas outcomes (W/D/L) — menos útil para apostas em mercados de placar exato

**Consequences:**
- Probabilidades de placares individuais são mais incertas que outcomes agregados — aceitar margem de erro maior
- Narrativa por placar aumenta custo de tokens do Sonnet (aceitável: ~3,000 tokens/análise)

---

### Decision 3: XLM-RoBERTa Local + Haiku Condicional para Sentimento

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Data** | 2026-06-19 |

**Context:** Precisamos processar ~200 artigos/dia (48 times × ~4 artigos) em múltiplos idiomas. Usar Haiku para todos os artigos custaria ~$1.50/dia = $45/mês. Budget é < $10/mês total.

**Choice:** XLM-RoBERTa (`cardiffnlp/twitter-xlm-roberta-base-sentiment`) processa todos os artigos localmente (grátis). Haiku só é chamado quando score < 3 ou > 8 (artigos extremos, ~20% do volume).

**Rationale:**
- XLM-RoBERTa suporta 100+ idiomas nativamente, inclui PT-BR
- Roda em CPU sem GPU em < 1s/artigo
- 80% dos artigos têm sentimento neutro/moderado → XLM-RoBERTa suficiente
- 20% com sentimento extremo são exatamente onde queremos extração profunda com Haiku
- Custo final: ~$0.03/dia em LLM calls (6% do budget)

**Alternatives Rejected:**
1. Haiku para todos — $45/mês, estoura budget
2. Apenas XLM-RoBERTa — não extrai sinais específicos (lesões, conflitos, nomes)
3. API HuggingFace Inference — latência de rede, free tier limitado, XLM local é mais rápido

**Consequences:**
- Dependência de modelo ~500MB baixado na inicialização (`transformers` library)
- Primeira execução mais lenta (download do modelo)

---

### Decision 4: H2H Key Sempre Ordenado Alfabeticamente

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Data** | 2026-06-19 |

**Context:** H2H entre BRA e FRA pode ser buscado como "BRA_FRA" ou "FRA_BRA" dependendo de quem o usuário selecionou primeiro.

**Choice:** Key = `sorted([code_a, code_b])` sempre. Arquivo sempre é `BRA_FRA.json` (B < F).

**Rationale:** Evita duplicação de dados e lookup inconsistente. Simples e determinístico.

**Consequences:**
- Ao ler, precisamos lembrar qual time é "team_a" e qual é "team_b" para exibição correta
- Schema `H2HHistory` mantém campos `team_a` e `team_b` com os códigos para referência

---

### Decision 5: Reddit só para Nações com Subreddit Ativo (≥ 1K membros)

| Atributo | Valor |
|----------|-------|
| **Status** | Accepted |
| **Data** | 2026-06-19 |

**Context:** Q-005 — Reddit não tem subreddits para todos os 48 países.

**Choice:** Reddit RSS apenas para países com subreddit de futebol ativo (≥ 1K membros). Para os demais, Google News RSS é a única fonte. Lista mantida em `config.yaml`.

**Subreddits mapeados:**
- América: r/brazil, r/argentina, r/mexico, r/usa, r/canada, r/colombia, r/chile, r/uruguay, r/ecuador, r/peru, r/paraguay, r/costarica, r/honduras, r/panama, r/jamaica, r/venezuela, r/bolivia
- Europa: r/france, r/england, r/germany, r/spain, r/portugal, r/netherlands, r/belgium, r/croatia, r/switzerland, r/austria, r/poland, r/serbia, r/czechrepublic, r/hungary, r/scotland, r/wales, r/ireland
- Geral: r/worldcup, r/soccer
- África/Ásia/Oceania: Google News RSS somente

---

## File Manifest

| # | Arquivo | Ação | Propósito | Agente | Deps |
|---|---------|------|-----------|--------|------|
| 1 | `src/schemas/__init__.py` | Create | Package init | @python-developer | — |
| 2 | `src/schemas/team.py` | Create | TeamProfile, TeamForm, TeamSquad, TeamStats | @python-developer | — |
| 3 | `src/schemas/sentiment.py` | Create | SentimentRecord, SentimentDimensions, SentimentHistory | @python-developer | — |
| 4 | `src/schemas/match.py` | Create | H2HHistory, OddsSnapshot, ScorelinePrediction, MatchAnalysis | @python-developer | — |
| 5 | `src/config.py` | Create | BaseSettings + todas as configurações | @python-developer | — |
| 6 | `src/storage/__init__.py` | Create | Package init | @python-developer | — |
| 7 | `src/storage/gcs.py` | Create | GCS read/write/upload com retry e rollback | @python-developer | 5 |
| 8 | `src/collectors/__init__.py` | Create | Package init | @python-developer | — |
| 9 | `src/collectors/football_data.py` | Create | football-data.org client: histórico, form, standings | @ai-data-engineer | 2, 5, 7 |
| 10 | `src/collectors/api_football.py` | Create | API-Football client: squad, injuries, stats | @ai-data-engineer | 2, 5, 7 |
| 11 | `src/collectors/odds.py` | Create | The Odds API client: odds por partida | @ai-data-engineer | 4, 5, 7 |
| 12 | `src/collectors/news.py` | Create | Google News RSS + Reddit RSS: artigos por seleção | @ai-data-engineer | 5, 7 |
| 13 | `src/collectors/historical.py` | Create | Kaggle WC dataset + StatsBomb: download único | @ai-data-engineer | 2, 4, 7 |
| 14 | `src/analyzers/__init__.py` | Create | Package init | @python-developer | — |
| 15 | `src/analyzers/sentiment.py` | Create | XLM-RoBERTa + Haiku: pipeline de sentimento | @ai-prompt-specialist | 3, 5, 7 |
| 16 | `src/analyzers/match_analyzer.py` | Create | Sonnet 4.6: predição de placares com 3+ cenários | @ai-prompt-specialist | 2, 3, 4, 5, 7 |
| 17 | `src/pipeline/__init__.py` | Create | Package init | @python-developer | — |
| 18 | `src/pipeline/run_daily.py` | Create | Orquestrador: coleta → processa → upload GCS | @ai-data-engineer | 9-16 |
| 19 | `scripts/init_historical.py` | Create | Download único: Kaggle + StatsBomb → GCS | @python-developer | 13 |
| 20 | `dashboard/__init__.py` | Create | Package init | @python-developer | — |
| 21 | `dashboard/app.py` | Create | Streamlit entry point + GCS auth + navegação | @ui-designer | 5, 7 |
| 22 | `dashboard/components/__init__.py` | Create | Package init | @python-developer | — |
| 23 | `dashboard/components/prediction_card.py` | Create | Card de placar com % e value bet highlight | @ui-designer | 4 |
| 24 | `dashboard/components/sentiment_gauge.py` | Create | Gauge de sentimento 0-10 com tendência | @ui-designer | 3 |
| 25 | `dashboard/pages/match_analyzer.py` | Create | M1: análise de partida → 3+ placares | @ui-designer | 16, 23, 24 |
| 26 | `dashboard/pages/team_profile.py` | Create | M2: perfil de seleção + elenco + stats | @ui-designer | 2 |
| 27 | `dashboard/pages/h2h_explorer.py` | Create | M3: H2H histórico com filtros | @ui-designer | 4 |
| 28 | `dashboard/pages/odds_monitor.py` | Create | M4: odds + implied probability + value bets | @ui-designer | 4 |
| 29 | `dashboard/pages/sentiment.py` | Create | M5: mapa de calor + série temporal de sentimento | @ui-designer | 3 |
| 30 | `dashboard/pages/tournament.py` | Create | M6: tabela Copa 2026 + artilheiros + histórico | @ui-designer | 2, 4 |
| 31 | `tests/test_schemas.py` | Create | Testes unitários de todos os schemas Pydantic | @test-generator | 2, 3, 4 |
| 32 | `tests/test_collectors.py` | Create | Testes de collectors com mocks de API | @test-generator | 9-13 |
| 33 | `tests/test_sentiment.py` | Create | Testes do pipeline de sentimento | @test-generator | 15 |
| 34 | `tests/test_match_analyzer.py` | Create | Testes do analisador de partida | @test-generator | 16 |
| 35 | `tests/test_gcs.py` | Create | Testes de storage com GCS mock | @test-generator | 7 |
| 36 | `pyproject.toml` | Create | Dependências + configuração Ruff + pytest | @python-developer | — |
| 37 | `config.yaml` | Create | Todas as configurações externalizadas | @python-developer | — |
| 38 | `.env.example` | Create | Template de variáveis de ambiente | @python-developer | — |
| 39 | `data/teams_48.json` | Create | Lista dos 48 times da Copa 2026 com metadados | @python-developer | — |
| 40 | `.streamlit/secrets.toml.example` | Create | Template de secrets para Streamlit Cloud | @python-developer | — |

**Total de arquivos:** 40

---

## Agent Assignment Rationale

| Agente | Arquivos | Por quê |
|--------|----------|---------|
| @python-developer | 1-8, 17, 20, 22, 36-40 | Schemas Pydantic, config, storage helpers, boilerplate |
| @ai-data-engineer | 9-13, 18 | Collectors de APIs externas, rate limiting, pipeline orquestrador |
| @ai-prompt-specialist | 15, 16 | Prompts LLM para sentimento (Haiku) e predição (Sonnet) |
| @ui-designer | 21, 23-30 | Streamlit pages, componentes visuais, layout do dashboard |
| @test-generator | 31-35 | pytest com mocks de API e GCS |

---

## Code Patterns

### Pattern 1: Schemas Pydantic (Design Tokens)

```python
# src/schemas/team.py
from __future__ import annotations
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field, computed_field


class MatchResult(BaseModel):
    date: date
    opponent_code: str
    home_or_away: Literal["home", "away", "neutral"]
    goals_scored: int = Field(ge=0)
    goals_conceded: int = Field(ge=0)
    competition: str
    result: Literal["W", "D", "L"]


class TeamForm(BaseModel):
    code: str
    matches: list[MatchResult]
    updated_at: datetime

    @computed_field
    @property
    def avg_goals_scored(self) -> float:
        if not self.matches:
            return 0.0
        return round(sum(m.goals_scored for m in self.matches) / len(self.matches), 2)

    @computed_field
    @property
    def avg_goals_conceded(self) -> float:
        if not self.matches:
            return 0.0
        return round(sum(m.goals_conceded for m in self.matches) / len(self.matches), 2)

    @computed_field
    @property
    def record(self) -> str:
        w = sum(1 for m in self.matches if m.result == "W")
        d = sum(1 for m in self.matches if m.result == "D")
        l = sum(1 for m in self.matches if m.result == "L")
        return f"{w}W-{d}D-{l}L"
```

```python
# src/schemas/match.py
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class ScorelinePrediction(BaseModel):
    scoreline: str          # "Brasil 2x0 França"
    probability: float = Field(ge=0.0, le=1.0)
    market_implied: float | None = Field(default=None, ge=0.0, le=1.0)
    narrative: str

    @computed_field
    @property
    def value_pp(self) -> float | None:
        if self.market_implied is None:
            return None
        return round((self.probability - self.market_implied) * 100, 1)

    @computed_field
    @property
    def is_value_bet(self) -> bool:
        return self.value_pp is not None and self.value_pp > 5.0


class MatchAnalysis(BaseModel):
    match_key: str          # "BRA_FRA" (ordenado A-Z)
    team_a_code: str
    team_b_code: str
    generated_at: datetime
    cached_until: datetime
    scoreline_predictions: list[ScorelinePrediction]
    outcome_summary: dict[str, float]   # {team_a_wins, draw, team_b_wins}
    signals_used: dict
    confidence_level: Literal["high", "medium", "low"]
    data_freshness_hours: float

    @model_validator(mode="after")
    def validate_probabilities(self) -> MatchAnalysis:
        total = sum(p.probability for p in self.scoreline_predictions)
        if total > 1.01:
            raise ValueError(f"Scoreline probabilities sum to {total:.2f} > 1.0")
        return self
```

### Pattern 2: GCS Storage com Rollback

```python
# src/storage/gcs.py
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

logger = logging.getLogger(__name__)


class GCSStorage:
    def __init__(self, bucket_name: str, client: storage.Client) -> None:
        self._bucket = client.bucket(bucket_name)

    def upload_json(self, gcs_path: str, data: dict | list, overwrite: bool = True) -> bool:
        blob = self._bucket.blob(gcs_path)
        if not overwrite and blob.exists():
            logger.debug("Skip upload (exists): %s", gcs_path)
            return False
        try:
            blob.upload_from_string(
                json.dumps(data, ensure_ascii=False, default=str),
                content_type="application/json",
            )
            logger.info("Uploaded: gs://%s/%s", self._bucket.name, gcs_path)
            return True
        except GoogleCloudError as exc:
            logger.error("GCS upload failed for %s: %s", gcs_path, exc)
            return False

    def download_json(self, gcs_path: str) -> dict | list | None:
        blob = self._bucket.blob(gcs_path)
        try:
            return json.loads(blob.download_as_text())
        except Exception as exc:
            logger.warning("GCS download failed for %s: %s", gcs_path, exc)
            return None

    def upload_batch(self, items: list[tuple[str, dict]]) -> dict[str, bool]:
        """Upload lista de (gcs_path, data); retorna {path: success}. Não aborta em falha parcial."""
        results = {}
        for gcs_path, data in items:
            results[gcs_path] = self.upload_json(gcs_path, data)
        return results
```

### Pattern 3: Collector com Rate Limiting e Cache

```python
# src/collectors/football_data.py
from __future__ import annotations
import time
import logging
from datetime import datetime, timedelta
import httpx
from src.schemas.team import TeamForm, MatchResult
from src.storage.gcs import GCSStorage
from src.config import Settings

logger = logging.getLogger(__name__)

SLEEP_BETWEEN_CALLS = 6.1  # 10 calls/min = 6s/call (+ buffer)


class FootballDataCollector:
    def __init__(self, settings: Settings, storage: GCSStorage) -> None:
        self._settings = settings
        self._storage = storage
        self._client = httpx.Client(
            base_url="https://api.football-data.org/v4",
            headers={"X-Auth-Token": settings.football_data_api_key},
            timeout=30,
        )

    def collect_team_form(self, team_code: str, team_id: int) -> TeamForm | None:
        gcs_path = f"teams/{team_code}/form.json"

        # Cache: só recoleta se dado tem > 20h (margem antes das 24h)
        cached = self._storage.download_json(gcs_path)
        if cached:
            form = TeamForm.model_validate(cached)
            age_hours = (datetime.utcnow() - form.updated_at).total_seconds() / 3600
            if age_hours < 20:
                logger.debug("Using cached form for %s (age: %.1fh)", team_code, age_hours)
                return form

        time.sleep(SLEEP_BETWEEN_CALLS)
        try:
            resp = self._client.get(f"/teams/{team_id}/matches", params={"limit": 10, "status": "FINISHED"})
            resp.raise_for_status()
            matches = [self._parse_match(m, team_id) for m in resp.json().get("matches", [])]
            form = TeamForm(code=team_code, matches=matches, updated_at=datetime.utcnow())
            self._storage.upload_json(gcs_path, form.model_dump(mode="json"))
            return form
        except httpx.HTTPError as exc:
            logger.error("football-data.org error for %s: %s", team_code, exc)
            return TeamForm.model_validate(cached) if cached else None

    def _parse_match(self, raw: dict, team_id: int) -> MatchResult:
        home_id = raw["homeTeam"]["id"]
        is_home = home_id == team_id
        home_score = raw["score"]["fullTime"]["home"] or 0
        away_score = raw["score"]["fullTime"]["away"] or 0
        goals_scored = home_score if is_home else away_score
        goals_conceded = away_score if is_home else home_score
        result = "W" if goals_scored > goals_conceded else ("D" if goals_scored == goals_conceded else "L")
        opponent_id = raw["awayTeam"]["id"] if is_home else raw["homeTeam"]["id"]
        return MatchResult(
            date=raw["utcDate"][:10],
            opponent_code=str(opponent_id),
            home_or_away="home" if is_home else "away",
            goals_scored=goals_scored,
            goals_conceded=goals_conceded,
            competition=raw["competition"]["name"],
            result=result,
        )
```

### Pattern 4: Pipeline de Sentimento Híbrido

```python
# src/analyzers/sentiment.py
from __future__ import annotations
import logging
from datetime import date, datetime
from transformers import pipeline as hf_pipeline
import anthropic
from src.schemas.sentiment import SentimentRecord, SentimentDimensions, SentimentHistory
from src.config import Settings

logger = logging.getLogger(__name__)

_SENTIMENT_PIPELINE = None  # lazy load


def _get_xlm_pipeline():
    global _SENTIMENT_PIPELINE
    if _SENTIMENT_PIPELINE is None:
        _SENTIMENT_PIPELINE = hf_pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            device=-1,  # CPU
        )
    return _SENTIMENT_PIPELINE


def score_articles(articles: list[dict], team_name: str, settings: Settings) -> SentimentRecord:
    if len(articles) < 3:
        return SentimentRecord(
            date=date.today(),
            overall_score=5.0,
            dimensions=SentimentDimensions(cohesion=5, media_pressure=5, motivation=5, coach_confidence=5),
            alerts=[],
            articles_analyzed=len(articles),
            data_quality="insufficient",
        )

    xlm = _get_xlm_pipeline()
    scores = []
    extreme_articles = []

    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')}"[:512]
        result = xlm(text)[0]
        raw_score = {"positive": 10, "neutral": 5, "negative": 0}[result["label"].lower()]
        weighted = raw_score * result["score"] + 5 * (1 - result["score"])
        scores.append(weighted)
        if weighted < 3.0 or weighted > 8.0:
            extreme_articles.append((article, weighted))

    overall = round(sum(scores) / len(scores), 1)

    if not extreme_articles:
        return SentimentRecord(
            date=date.today(),
            overall_score=overall,
            dimensions=SentimentDimensions(cohesion=overall, media_pressure=10 - overall, motivation=overall, coach_confidence=overall),
            alerts=[],
            articles_analyzed=len(articles),
            data_quality="good",
        )

    return _deep_analysis_haiku(extreme_articles, overall, team_name, len(articles), settings)


def _deep_analysis_haiku(
    extreme_articles: list[tuple[dict, float]],
    overall_score: float,
    team_name: str,
    total_articles: int,
    settings: Settings,
) -> SentimentRecord:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    articles_text = "\n\n---\n\n".join(
        f"Score: {score:.1f}/10\nTitle: {a['title']}\nSummary: {a.get('summary', '')}"
        for a, score in extreme_articles[:5]
    )
    prompt = f"""Analyze these news articles about {team_name} national football team.
Extract structured intelligence signals.

Articles:
{articles_text}

Return JSON with this exact structure:
{{
  "dimensions": {{
    "cohesion": <0-10, squad unity>,
    "media_pressure": <0-10, press scrutiny>,
    "motivation": <0-10, team drive>,
    "coach_confidence": <0-10, manager trust>
  }},
  "alerts": ["<specific issue 1>", "<specific issue 2>"]
}}

Alerts must be concrete: "Striker X doubtful with muscle injury", not "team has problems".
Max 3 alerts. Return only valid JSON, no markdown."""

    msg = client.messages.create(
        model=settings.haiku_model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    import json
    data = json.loads(msg.content[0].text)
    return SentimentRecord(
        date=date.today(),
        overall_score=overall_score,
        dimensions=SentimentDimensions(**data["dimensions"]),
        alerts=data.get("alerts", []),
        articles_analyzed=total_articles,
        data_quality="good",
    )
```

### Pattern 5: Match Analyzer com Sonnet 4.6

```python
# src/analyzers/match_analyzer.py
from __future__ import annotations
import json
import logging
from datetime import datetime, timedelta
import anthropic
from src.schemas.match import MatchAnalysis, ScorelinePrediction
from src.schemas.team import TeamForm, TeamSquad
from src.schemas.sentiment import SentimentHistory
from src.config import Settings

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """\
You are an elite football match analyst. Predict the most likely scorelines for this match.

Match: {team_a_name} vs {team_b_name}
Competition: FIFA World Cup 2026 — {phase}

## HEAD-TO-HEAD ({h2h_total} matches)
{h2h_table}
Most frequent scorelines: {common_scorelines}
{team_a_name} wins: {h2h_a_wins} | Draws: {h2h_draws} | {team_b_name} wins: {h2h_b_wins}

## RECENT FORM (last 10 games)
{team_a_name}: {form_a_record} | Avg goals scored: {form_a_scored} | Avg conceded: {form_a_conceded}
{team_b_name}: {form_b_record} | Avg goals scored: {form_b_scored} | Avg conceded: {form_b_conceded}

## SQUAD ALERTS
{team_a_name} absences: {alerts_a}
{team_b_name} absences: {alerts_b}

## SQUAD MORALE (0=very negative, 10=very positive)
{team_a_name}: {sentiment_a}/10 (trend: {trend_a}) | Signals: {signals_a}
{team_b_name}: {sentiment_b}/10 (trend: {trend_b}) | Signals: {signals_b}

## MARKET REFERENCE (use as calibration only)
Bookmaker implied probabilities: {team_a_name} wins {odds_a}% | Draw {odds_draw}% | {team_b_name} wins {odds_b}%

## YOUR TASK
Generate the 5 most probable specific scorelines.
Requirements:
- Format scoreline as "{team_a_name} 2x1 {team_b_name}" (always team_a first)
- Probabilities must sum to ≤ 0.70 (remaining = other outcomes)
- Each narrative: 2-3 sentences explaining WHY this exact score
- Flag if your probability differs from market by >5pp (potential value bet)

Return ONLY valid JSON:
{{
  "scoreline_predictions": [
    {{
      "scoreline": "string",
      "probability": 0.00,
      "market_implied": 0.00 or null,
      "narrative": "string"
    }}
  ],
  "outcome_summary": {{"team_a_wins": 0.00, "draw": 0.00, "team_b_wins": 0.00}},
  "confidence_level": "high|medium|low",
  "reasoning": "1-2 sentence overall assessment"
}}"""


class MatchAnalyzer:
    def __init__(self, settings: Settings) -> None:
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._settings = settings

    def analyze(
        self,
        team_a_code: str, team_b_code: str,
        form_a: TeamForm, form_b: TeamForm,
        squad_a: TeamSquad, squad_b: TeamSquad,
        sentiment_a: SentimentHistory, sentiment_b: SentimentHistory,
        h2h: dict, odds: dict | None,
        phase: str = "Group Stage",
    ) -> MatchAnalysis:
        match_key = "_".join(sorted([team_a_code, team_b_code]))
        prompt = self._build_prompt(
            team_a_code, team_b_code, form_a, form_b,
            squad_a, squad_b, sentiment_a, sentiment_b,
            h2h, odds, phase,
        )
        msg = self._client.messages.create(
            model=self._settings.sonnet_model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = json.loads(msg.content[0].text)
        predictions = [ScorelinePrediction(**p) for p in raw["scoreline_predictions"]]
        return MatchAnalysis(
            match_key=match_key,
            team_a_code=team_a_code,
            team_b_code=team_b_code,
            generated_at=datetime.utcnow(),
            cached_until=datetime.utcnow() + timedelta(hours=24),
            scoreline_predictions=predictions,
            outcome_summary=raw["outcome_summary"],
            signals_used={"form_a": form_a.record, "form_b": form_b.record},
            confidence_level=raw["confidence_level"],
            data_freshness_hours=0.0,
        )

    def _build_prompt(self, team_a_code: str, team_b_code: str, *args, **kwargs) -> str:
        # format ANALYSIS_PROMPT with all context data
        ...
```

### Pattern 6: Dashboard — Autenticação GCS

```python
# dashboard/app.py
from __future__ import annotations
import streamlit as st
from google.oauth2 import service_account
from google.cloud import storage
from src.config import Settings


@st.cache_resource
def get_gcs_client() -> storage.Client:
    """Usa Streamlit Secrets em produção; GOOGLE_APPLICATION_CREDENTIALS localmente."""
    if "gcp_service_account" in st.secrets:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        return storage.Client(credentials=credentials)
    return storage.Client()  # usa GOOGLE_APPLICATION_CREDENTIALS local


@st.cache_resource
def get_settings() -> Settings:
    return Settings()
```

### Pattern 7: Config Centralizado

```python
# src/config.py
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # GCP
    gcs_bucket: str = "bolao-copa-2026"
    gcs_project: str = "bolao-copa-2026"

    # APIs
    football_data_api_key: str
    api_football_key: str
    odds_api_key: str
    anthropic_api_key: str

    # LLM models
    haiku_model: str = "claude-haiku-4-5-20251001"
    sonnet_model: str = "claude-sonnet-4-6"

    # Sentiment thresholds
    sentiment_low_threshold: float = 3.0
    sentiment_high_threshold: float = 8.0

    # Rate limits
    football_data_sleep_seconds: float = 6.1
    api_football_daily_limit: int = 100
    odds_api_monthly_limit: int = 500
    odds_cache_hours: int = 12

    # Cache TTL
    form_cache_hours: int = 20
    squad_cache_hours: int = 20
    h2h_cache_days: int = 7
    analysis_cache_hours: int = 24
```

```yaml
# config.yaml (valores não-secretos; override via .env para segredos)
teams:
  count: 48
  wc2026_group_stage_matches: 104

reddit:
  active_subreddits:
    - brazil
    - argentina
    - mexico
    - usa
    - france
    - england
    - germany
    - spain
    - portugal
    - worldcup
    - soccer

news:
  languages_by_country:
    BRA: ["pt-BR", "pt"]
    ARG: ["es-AR", "es"]
    FRA: ["fr-FR", "fr"]
    DEU: ["de-DE", "de"]
    JPN: ["ja-JP", "ja"]
    KOR: ["ko-KR", "ko"]
    MAR: ["ar-MA", "fr-MA"]
    SEN: ["fr-SN", "fr"]
    # ... todos os 48

pipeline:
  run_hour: 6
  progress_file: "data/.upload_progress.json"
  log_file: "data/.pipeline_log.json"
```

---

## Data Flow Detalhado

```
COLETA DIÁRIA (06:00 local)
│
├── 1. Verificar progresso anterior (.upload_progress.json)
│       └── Se encontrado: retomar a partir de onde parou
│
├── 2. Download histórico (apenas se não existe no GCS)
│       └── scripts/init_historical.py → Kaggle WC + StatsBomb → GCS history/
│
├── 3. Para cada seleção (48 times, com throttling):
│   │
│   ├── 3a. football-data.org → form.json (últimos 10 jogos)
│   │       └── Rate: 6.1s entre calls / Cache: 20h
│   │
│   ├── 3b. API-Football → squad.json + stats.json
│   │       └── Rate: tracking diário de 100 calls / Cache: 20h
│   │
│   ├── 3c. Google News RSS + Reddit RSS → news/{date}.json (raw)
│   │       └── Sem rate limit / Deduplicar por URL
│   │
│   └── 3d. Sentimento:
│           ├── XLM-RoBERTa (local) → score por artigo
│           ├── [se score extremo] Claude Haiku → extração de sinais
│           └── → sentiment/history.json (append ao histórico)
│
├── 4. Odds (por partida agendada):
│       ├── The Odds API → odds/{date}/{match}.json
│       └── Rate: cache 12h / tracking mensal de 500 req
│
├── 5. H2H (on-demand, cache 7 dias):
│       └── football-data.org → matches/h2h/{COD_A}_{COD_B}.json
│
├── 6. Upload batch para GCS:
│       ├── Salvar progresso a cada 10 times
│       └── Em falha: não sobrescrever dados anteriores
│
└── 7. Atualizar _meta/last_updated.json + collection_log.json

ANÁLISE SOB DEMANDA (via Streamlit)
│
├── 1. Usuário seleciona Time A vs Time B
│
├── 2. Verificar cache de análise no GCS:
│       └── matches/wc2026/{phase}/{key}_analysis.json
│           Se cached_until > now: retornar cache direto
│
├── 3. Carregar contexto do GCS (paralelo):
│       ├── teams/{A}/form.json
│       ├── teams/{A}/squad.json
│       ├── teams/{A}/sentiment/history.json
│       ├── teams/{B}/form.json
│       ├── teams/{B}/squad.json
│       ├── teams/{B}/sentiment/history.json
│       ├── matches/h2h/{key}.json
│       └── odds/{today}/{key}.json
│
├── 4. Claude Sonnet 4.6 → MatchAnalysis (JSON)
│       └── Validar com Pydantic antes de exibir
│
├── 5. Salvar análise em GCS (cache 24h)
│       └── matches/wc2026/{phase}/{key}_analysis.json
│
└── 6. Renderizar dashboard M1 com ScorelinePredictions
```

---

## Agent Communication Contract

| Step | Sender | Receiver | Conteúdo | Metadata Chave |
|------|--------|----------|----------|----------------|
| 1 | `news.py` | `sentiment.py` | `list[dict]` — artigos raw | `team_code`, `collected_at` |
| 2 | `sentiment.py` (XLM) | `sentiment.py` (Haiku) | Artigos com score extremo | `team_code`, `score`, `article_url` |
| 3 | `sentiment.py` | GCS | `SentimentRecord` JSON | `team_code`, `date` |
| 4 | `run_daily.py` | `match_analyzer.py` | Contexto completo (5 sinais) | `match_key`, `team_a_code`, `team_b_code` |
| 5 | `match_analyzer.py` | Sonnet 4.6 | Prompt estruturado | `match_key`, `phase` |
| 6 | Sonnet 4.6 | `match_analyzer.py` | `MatchAnalysis` JSON | `generated_at` |
| 7 | `dashboard/app.py` | GCS | Download de contexto | `team_codes`, `date` |
| 8 | `match_analyzer.py` | `dashboard/M1` | `MatchAnalysis` validado | `cached_until`, `confidence_level` |

---

## Integration Points

| Sistema Externo | Tipo | Autenticação | Rate Limit |
|-----------------|------|--------------|------------|
| football-data.org | REST API | API Key header | 10 calls/min |
| API-Football | REST API | API Key header | 100 calls/dia |
| The Odds API | REST API | API Key query param | 500 req/mês |
| Google News RSS | RSS Feed | Nenhuma | Sem limite documentado |
| Reddit RSS | RSS Feed | Nenhuma | Sem limite para feeds públicos |
| Kaggle | CLI / HTTP | Kaggle API token (`.kaggle/kaggle.json`) | Download único |
| Anthropic API | SDK | API Key env var | Tier 1 padrão |
| GCS | SDK | Service Account JSON | Sem limite prático |
| Streamlit Cloud | Deploy | GitHub + Streamlit Secrets | Sem limite |

---

## Testing Strategy

| Tipo | Escopo | Arquivos | Ferramentas | Meta de Cobertura |
|------|--------|----------|-------------|-------------------|
| Unit | Schemas Pydantic | `tests/test_schemas.py` | pytest | 100% dos schemas |
| Unit | Parsers de API (sem HTTP) | `tests/test_collectors.py` | pytest + `respx` (mock HTTP) | 80% das funções |
| Unit | Pipeline de sentimento | `tests/test_sentiment.py` | pytest + mock XLM + mock Haiku | Happy path + insufficient data |
| Unit | Match analyzer prompt | `tests/test_match_analyzer.py` | pytest + mock Sonnet | Validação do JSON output |
| Integration | GCS upload/download | `tests/test_gcs.py` | pytest + `google-cloud-testutils` ou mock | Upload, download, batch, rollback |
| Manual E2E | Pipeline completo 3 times | Manual | Executar `run_daily.py --teams BRA,FRA,ARG` | Verificar GCS e Streamlit |

---

## Error Handling

| Tipo de Erro | Estratégia | Retry? |
|--------------|------------|--------|
| API HTTP 429 (rate limit) | Esperar `Retry-After` header ou 60s; usar cache GCS | Sim (1x) |
| API HTTP 5xx | Log + usar dados do cache GCS | Sim (1x, após 30s) |
| API HTTP 401/403 | Log CRITICAL + parar pipeline; não há fallback sem auth | Não |
| GCS upload failure | Log + salvar progresso local; retomar na próxima execução | Não (retomada manual) |
| GCS download failure (Streamlit) | Mostrar aviso "dados indisponíveis" + timestamp do último dado | Não |
| LLM JSON inválido (Haiku/Sonnet) | `try/except json.JSONDecodeError` → retry com temperatura 0 | Sim (1x) |
| XLM-RoBERTa CUDA/CPU error | Fallback: score neutro 5.0 para o artigo | Não |
| Pydantic ValidationError | Log com payload + skip do item (não crashar pipeline inteiro) | Não |
| Streamlit auth GCS falha | Mostrar mensagem de erro clara + instrução de configuração | Não |

---

## Configuration

| Config Key | Tipo | Default | Descrição |
|------------|------|---------|-----------|
| `gcs_bucket` | str | `"bolao-copa-2026"` | Nome do bucket GCS |
| `haiku_model` | str | `"claude-haiku-4-5-20251001"` | Modelo Haiku para sentimento |
| `sonnet_model` | str | `"claude-sonnet-4-6"` | Modelo Sonnet para predição |
| `sentiment_low_threshold` | float | `3.0` | Score abaixo → deep analysis com Haiku |
| `sentiment_high_threshold` | float | `8.0` | Score acima → deep analysis com Haiku |
| `football_data_sleep_seconds` | float | `6.1` | Delay entre calls à football-data.org |
| `api_football_daily_limit` | int | `100` | Limite diário de calls à API-Football |
| `odds_cache_hours` | int | `12` | TTL de cache das odds |
| `form_cache_hours` | int | `20` | TTL de cache da forma dos times |
| `analysis_cache_hours` | int | `24` | TTL de cache da análise de partida |
| `h2h_cache_days` | int | `7` | TTL de cache do H2H histórico |

---

## Security Considerations

- **Nunca commitar credenciais**: `.env` no `.gitignore`; `.streamlit/secrets.toml` no `.gitignore`
- **Service accounts com least-privilege**: `pipeline-writer` tem `objectCreator` + `objectViewer`; `streamlit-reader` tem apenas `objectViewer`
- **API keys em variáveis de ambiente**: nunca hardcoded; nunca logadas
- **GCS bucket não público**: ACL padrão privado; acesso apenas via service accounts
- **Reddit/Google News RSS**: dados públicos, sem PII — sem preocupação de GDPR
- **Streamlit Secrets**: criptografado em repouso pelo Streamlit Cloud; não aparece em logs

---

## Observability

| Aspecto | Implementação |
|---------|---------------|
| Logging | `logging.getLogger(__name__)` em todos os módulos; formato JSON em produção; nível INFO por padrão, DEBUG via env var |
| Pipeline metrics | `_meta/collection_log.json` no GCS: timestamp, times coletados, erros, calls de API usados, custo LLM estimado |
| Sentimento trend | `teams/{COD}/sentiment/history.json` é a série temporal — inspecionável diretamente |
| LLM costs | Cada call LLM loga `input_tokens` e `output_tokens`; `collection_log.json` acumula por execução |
| Dashboard freshness | Footer do Streamlit mostra `last_updated` do GCS (`_meta/last_updated.json`) |
| Erros de coleta | Lista de times com fallback para cache visível no dashboard (badge vermelho no M2) |

---

## Estrutura de Diretórios Final

```
bolao_copa/
├── src/
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── team.py             # TeamProfile, TeamForm, TeamSquad, TeamStats
│   │   ├── sentiment.py        # SentimentRecord, SentimentDimensions, SentimentHistory
│   │   └── match.py            # H2HHistory, OddsSnapshot, ScorelinePrediction, MatchAnalysis
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── football_data.py    # form, standings, H2H
│   │   ├── api_football.py     # squad, injuries, player stats
│   │   ├── odds.py             # odds por partida
│   │   ├── news.py             # Google News RSS + Reddit RSS
│   │   └── historical.py       # Kaggle + StatsBomb (download único)
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── sentiment.py        # XLM-RoBERTa + Haiku
│   │   └── match_analyzer.py   # Sonnet 4.6 prediction
│   ├── storage/
│   │   ├── __init__.py
│   │   └── gcs.py              # GCS helpers com retry e rollback
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── run_daily.py        # Orquestrador principal
│   └── config.py               # Pydantic BaseSettings
├── dashboard/
│   ├── app.py                  # Entry point + GCS auth
│   ├── components/
│   │   ├── __init__.py
│   │   ├── prediction_card.py  # Card de placar com value bet
│   │   └── sentiment_gauge.py  # Gauge de sentimento
│   └── pages/
│       ├── match_analyzer.py   # M1: análise de partida
│       ├── team_profile.py     # M2: perfil de seleção
│       ├── h2h_explorer.py     # M3: H2H histórico
│       ├── odds_monitor.py     # M4: odds + value bets
│       ├── sentiment.py        # M5: mapa de calor + série temporal
│       └── tournament.py       # M6: tabela WC2026
├── scripts/
│   └── init_historical.py      # Download único Kaggle + StatsBomb
├── tests/
│   ├── test_schemas.py
│   ├── test_collectors.py
│   ├── test_sentiment.py
│   ├── test_match_analyzer.py
│   └── test_gcs.py
├── data/                       # gitignored — cache local temporário
│   └── teams_48.json           # lista dos 48 times com IDs das APIs
├── config.yaml                 # configurações não-secretas
├── .env.example                # template de variáveis de ambiente
├── .streamlit/
│   └── secrets.toml.example    # template de secrets Streamlit
└── pyproject.toml              # deps + Ruff + pytest config
```

---

## Revision History

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 2026-06-19 | design-agent | Versão inicial completa |

---

## Next Step

**Pronto para:** `/build .claude/sdd/features/DESIGN_COPA2026_ANALYZER.md`
