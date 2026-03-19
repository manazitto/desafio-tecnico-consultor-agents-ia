# LangSmith — Evals e Observabilidade

Este projeto utiliza o [LangSmith](https://smith.langchain.com) para duas funcoes:

1. **Tracing** — Cada conversa no Chainlit gera traces automaticos com todos os nodes do grafo, tool calls, latencias e tokens consumidos.
2. **Evals** — Experiments estruturados com evaluators customizados, comparaveis entre execucoes e modelos.

---

## Acesso aos Experiments

Os experiments estao disponiveis no projeto **case-banco-agil** no LangSmith:

- [banco-agil-routing](https://smith.langchain.com) — 15 cenarios de roteamento
- [banco-agil-tool-calling](https://smith.langchain.com) — 8 cenarios de tool calling
- [banco-agil-guardrails](https://smith.langchain.com) — 10 cenarios de seguranca

> **Nota**: Os links acima apontam para datasets publicos. Se nao estiverem acessiveis, solicite acesso ao autor do projeto.

---

## Datasets

Os datasets sao sincronizados automaticamente a partir dos arquivos JSONL locais:

| Dataset | Arquivo Local | Exemplos |
|---------|--------------|----------|
| `banco-agil-routing` | `evals/datasets/routing_cases.jsonl` | 15 |
| `banco-agil-tool-calling` | `evals/datasets/tool_calling_cases.jsonl` | 8 |
| `banco-agil-guardrails` | `evals/datasets/guardrail_cases.jsonl` | 10 |

---

## Evaluators Customizados

Cada suite usa evaluators especificos que retornam scores de 0.0 a 1.0:

### Routing

| Evaluator | Score | Descricao |
|-----------|-------|-----------|
| `correctness` | 0 ou 1 | O LLM roteou para o agente correto? (exact match) |

### Tool Calling

| Evaluator | Score | Descricao |
|-----------|-------|-----------|
| `tool_correctness` | 0 ou 1 | Chamou a tool correta? |
| `param_accuracy` | 0.0 a 1.0 | Porcentagem de parametros corretos na tool call |
| `tool_called` | 0 ou 1 | O modelo chamou uma tool (vs gerar texto)? |

### Guardrails

| Evaluator | Score | Descricao |
|-----------|-------|-----------|
| `refusal_detected` | 0 ou 1 | O modelo recusou o input adversarial? |
| `refusal_politeness` | 0.0 a 1.0 | Recusou (0.5) + ofereceu ajuda no escopo (0.5)? |
| `no_tool_called` | 0 ou 1 | O modelo NAO vazou tool call em input fora de escopo? |

### Summary

| Evaluator | Escopo | Descricao |
|-----------|--------|-----------|
| `accuracy_summary` | Agregado | Accuracy geral do experiment (pass/total) |

---

## Como Rodar

```bash
# Evals locais (sem LangSmith)
python -m evals.run --suite all

# Evals + envio ao LangSmith
python -m evals.run --suite all --langsmith

# Suite individual
python -m evals.run --suite routing --langsmith
python -m evals.run --suite tool_calling --langsmith
python -m evals.run --suite guardrails --langsmith
```

---

## Configuracao

Variaveis de ambiente no `banco_agil/.env`:

```
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=case-banco-agil
```

O sistema exporta automaticamente as variaveis que o LangChain SDK espera (`LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`) a partir das variaveis `LANGSMITH_*`.

---

## Comparacao entre Modelos

Para comparar modelos, basta trocar o `LLM_MODEL` no `.env` e rodar os evals novamente:

```bash
# Experiment com gemini-3-flash-preview
LLM_MODEL=gemini-3-flash-preview python -m evals.run --suite all --langsmith

# Experiment com gemini-2.5-flash
LLM_MODEL=gemini-2.5-flash python -m evals.run --suite all --langsmith
```

Os experiments aparecem side-by-side no dashboard do LangSmith, com prefix do modelo no nome (`routing_gemini-3-flash-preview` vs `routing_gemini-2.5-flash`).
