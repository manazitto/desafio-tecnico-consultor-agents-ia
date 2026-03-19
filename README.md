# Banco Agil

Sistema multi-agente inteligente para atendimento bancario virtual, construido com **LangGraph** e **LangChain**.

O Banco Agil simula o atendimento digital de um banco, onde um unico chatbot orquestra multiplos agentes especializados de forma transparente — o cliente percebe uma conversa fluida, sem "transferencias" visiveis entre departamentos.

## O Problema

Chatbots bancarios tradicionais sofrem de:

- **Roteamento rigido por keywords** — "limite" vai pra credito, "dolar" vai pra cambio, mas "quero saber quanto posso gastar" nao vai pra lugar nenhum
- **Handoffs que quebram contexto** — "vou te transferir para o setor de credito" e o cliente precisa repetir tudo
- **Prompts estaticos** — o agente nao sabe quem eh o cliente, mesmo apos autenticacao
- **Seguranca reativa** — injection e escopo tratados depois, nao antes

## A Solucao

Uma arquitetura multi-agente com **LangGraph StateGraph**, onde cada agente eh um node no grafo com roteamento semantico (via LLM), estado compartilhado, e guardrails deterministicos na entrada.

### Por que LangGraph?

| Abordagem | Problema |
|-----------|----------|
| Orchestrator custom com if/else | Roteamento fragil, manutencao pesada |
| LangChain AgentExecutor | Agente unico, sem multi-agent nativo |
| CrewAI / AutoGen | Overhead de framework, agentes "conversam entre si" |
| **LangGraph StateGraph** | Grafo explicito, estado tipado, edges condicionais, tool calling nativo |

O LangGraph nos da controle total: cada agente eh uma funcao pura que recebe estado e retorna estado. O grafo define as transicoes. Nao ha magica — cada edge eh explicita e testavel.

## Arquitetura

```
                    +──────────────+
                    │    START     │
                    +──────┬───────+
                           │
                    +──────▼───────+
                    │  Guardrail   │──── injection? ──→ RECUSA → END
                    +──────┬───────+
                           │ clean
                    +──────▼───────+
              ┌────→│   Triage     │←────┐
              │     +──────┬───────+     │
              │            │             │
         route_to_agent    │        route_to_agent
              │     +──────▼───────+     │
              ├────→│   Credit     │─────┤
              │     +──────────────+     │
              │     +──────────────+     │
              ├────→│  Exchange    │─────┤
              │     +──────────────+     │
              │     +──────────────+     │
              └────→│  Interview   │─────┘
                    +──────┬───────+
                           │
                    +──────▼───────+
                    │   ToolNode   │
                    +──────┬───────+
                           │
                    +──────▼───────+
                    │     END      │
                    +──────────────+
```

### Fluxo de uma conversa real

1. Cliente envia "meu cpf eh 123.456.789-00, nasci em 15 de maio de 1990"
2. **Guardrail node** — checa injection patterns (deterministico, sem LLM) → limpo
3. **Triage node** — LLM normaliza CPF e data, chama `authenticate_client` tool
4. **ToolNode** — executa autenticacao contra CSV, retorna dados do cliente
5. **Triage node** — recebe resultado, injeta dados no prompt: "Cliente: Maria Silva, Score: 720, Limite: R$8000"
6. Cliente: "quero aumentar meu limite pra 12 mil"
7. **Triage node** — LLM entende intencao, chama `route_to_agent(target_agent="credit")`
8. **Credit node** — ja tem dados do cliente no state, chama `request_credit_increase` direto
9. Resposta fluida, sem "transferencia"

### Decisoes tecnicas relevantes

**Guardrails deterministicos como node de entrada** — Regex-based, zero latencia, zero custo de token. Injection patterns sao checados antes de qualquer chamada ao LLM. Guardrails de escopo ficam no prompt (LLM-driven), porque exigem compreensao semantica.

**Prompts dinamicos com dados do cliente** — Apos autenticacao, `build_system_prompt()` injeta nome, CPF, score e limite no system prompt de cada agente. O LLM sabe com quem esta falando e usa esses dados nas tool calls sem pedir de novo.

**Tool deduplication** — Agentes compartilham tools (`route_to_agent`, `end_conversation`). O Gemini rejeita declaracoes duplicadas de funcao. A `build_agent_graph()` deduplica por nome antes do `bind_tools()`.

**@tool factories com closure** — Cada factory (`create_auth_tools`, `create_credit_tools`, etc.) recebe o servico por closure, evitando globals e facilitando testes.

**Handoffs transparentes** — O prompt instrui o agente a nunca dizer "vou transferir". O cliente percebe um unico atendente que sabe de tudo.

## Servicos

| Servico | Descricao |
|---------|-----------|
| **Autenticacao** | CPF + data de nascimento contra base CSV. Lock apos 3 tentativas |
| **Credito** | Consulta de limite atual e solicitacao de aumento (aprovado/rejeitado por faixa de score) |
| **Entrevista de Credito** | Recalculo de score com formula ponderada: renda, emprego, despesas, dependentes, dividas |
| **Cambio** | Cotacao de moedas em tempo real via API externa |

### Formula do Score

```
score = (renda / (despesas + 1)) * 30
      + emprego_peso                    # formal=300, autonomo=200, desempregado=0
      + dependentes_peso                # 0=100, 1=80, 2=60, 3+=30
      + divida_peso                     # sem=-100, com=100
```

Score final: clamped entre 0 e 1000.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Orquestracao | LangGraph StateGraph |
| LLM | Google Gemini (`gemini-3-flash-preview`) via `langchain-google-genai` |
| Tools | LangChain `@tool` decorator + `ToolNode` |
| UI | Chainlit |
| Dados | CSV (clientes, score_limite, solicitacoes) |
| Testes | pytest (75 testes) |
| Evals | Suite propria: routing, tool_calling, guardrails (33 cases, 100% accuracy) |
| Container | Docker + docker-compose |

## Estrutura do Projeto

```
banco_agil/
├── agents/                  # Prompts e definicao dos agentes
│   ├── triage.py            # Autenticacao e roteamento
│   ├── credit.py            # Consulta e aumento de limite
│   ├── credit_interview.py  # Recalculo de score
│   ├── exchange.py          # Cotacao de moedas
│   └── common.py            # Tools compartilhadas
├── core/
│   ├── graph.py             # StateGraph LangGraph (orquestracao principal)
│   ├── tools_bridge.py      # @tool factories (ponte servicos → LangChain)
│   ├── prompts.py           # Prompts dinamicos com dados do cliente
│   ├── guardrails.py        # Injection patterns + guardrail node
│   ├── orchestrator.py      # Orchestrator legacy (mantido para evals)
│   └── llm/                 # Provider LLM (Gemini via langchain-google-genai)
├── services/                # Logica de negocio pura
│   ├── auth.py              # Autenticacao com lock
│   ├── credit.py            # Credito e faixas de score
│   └── score.py             # Calculo de score ponderado
├── models/                  # Dataclasses (Cliente, Solicitacao)
├── tools/                   # Utilitarios (CSV ops, exchange API)
├── ui/
│   └── app.py               # Interface Chainlit (async graph.ainvoke)
├── data/                    # CSVs com dados de clientes
└── config.py                # Configuracao centralizada

evals/
├── datasets/                # 33 test cases em JSONL
│   ├── routing_cases.jsonl       # 15 cenarios de roteamento
│   ├── tool_calling_cases.jsonl  # 8 cenarios de tool calling
│   └── guardrail_cases.jsonl     # 10 cenarios de seguranca
├── runners/                 # SingleTurnRunner
├── run.py                   # CLI: python -m evals.run --suite all
└── report.py                # Gerador de relatorios

tests/                       # 75 testes unitarios
```

## Como Rodar

### Pre-requisitos

- Python 3.11+
- Chave da API Gemini (`GEMINI_API_KEY`)

### Setup local

```bash
# Clonar e instalar
git clone https://github.com/mana-gsoares/GenNext.git
cd GenNext
pip install -e ".[dev]"

# Configurar chave da API
echo "GEMINI_API_KEY=sua-chave-aqui" > banco_agil/.env

# Rodar a UI
chainlit run banco_agil/ui/app.py -w
```

Acesse `http://localhost:8000`.

### Docker

```bash
docker compose up --build
```

### Testes

```bash
# Unitarios (75 testes, ~1.5s)
pytest tests/ -v

# Evals com LLM (requer GEMINI_API_KEY)
python -m evals.run --suite all --save
```

### Evals

As evals validam o comportamento do LLM em 3 dimensoes:

| Suite | O que testa | Cases |
|-------|-------------|-------|
| `routing` | LLM roteia para o agente correto dado um input | 15 |
| `tool_calling` | LLM chama a tool certa com parametros corretos | 8 |
| `guardrails` | LLM recusa inputs fora de escopo e injection | 10 |

```bash
python -m evals.run --suite routing --save
python -m evals.run --suite tool_calling --save
python -m evals.run --suite guardrails --save
python -m evals.run --suite all --save
```

## Evolucao do Projeto

O projeto passou por uma refatoracao significativa. O historico de commits conta a historia:

1. **`feat: refactor orchestration to LangGraph + LangChain`** — Substituicao do Orchestrator custom por StateGraph. Criacao do grafo de agentes, tools bridge, prompts dinamicos e guardrail node.

2. **`fix: improve tool_calling accuracy with directive prompts`** — Descoberta: o Gemini respeita *descricoes de tools* mais que system prompts na hora de decidir se chama uma tool. Adicionamos "REGRA PRINCIPAL - TOOL CALLING IMEDIATO" nos prompts.

3. **`refactor: unify LLM to langchain-google-genai`** — Removemos o SDK `google-genai` e unificamos toda comunicacao LLM via `langchain-google-genai`, eliminando duas abstractions concorrentes.

4. **`fix: handle multi-part content from gemini-3-flash-preview`** — O `gemini-3-flash-preview` retorna `response.content` como `list` ao inves de `str` em certos cenarios. Criamos normalizadores `_extract_text()` e `_to_str()`.

5. **`fix: deduplicate tools in graph`** — Tools compartilhadas (`route_to_agent`, `end_conversation`) causavam erro 400 do Gemini por declaracao duplicada. Deduplicacao por nome antes do `bind_tools()`.

6. **`feat: seamless agent handoffs + Agibank-inspired UI`** — Handoffs transparentes (sem "vou transferir") e tema visual inspirado no Agibank com CSS customizado.

7. **`feat: add Docker containerization`** — Dockerfile, docker-compose.yml para deploy em container.

## Licenca

MIT
