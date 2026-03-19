# Banco Agil - Sistema Multi-Agente Inteligente

## Visao Geral

Sistema de atendimento ao cliente para o banco digital ficticio "Banco Agil", composto por agentes de IA especializados com orquestracao propria (sem frameworks de agentes), arquitetura LLM-agnostica e avaliacao sistematica.

## User Stories

### P1 - Core (MVP)

**US-01**: Como cliente, quero ser autenticado pelo agente de triagem informando CPF e data de nascimento, para acessar os servicos do banco.

**US-02**: Como cliente autenticado, quero ser direcionado automaticamente para o agente correto conforme minha necessidade, sem perceber a transicao entre agentes.

**US-03**: Como cliente, quero consultar meu limite de credito disponivel.

**US-04**: Como cliente, quero solicitar aumento de limite de credito e receber resposta imediata baseada no meu score.

**US-05**: Como cliente com solicitacao rejeitada, quero ser oferecido a opcao de fazer uma entrevista de credito para recalcular meu score.

**US-06**: Como cliente, quero realizar uma entrevista financeira e ter meu score recalculado e atualizado.

**US-07**: Como cliente, quero consultar a cotacao de moedas em tempo real.

**US-08**: Como cliente, quero encerrar o atendimento a qualquer momento.

### P2 - Engenharia

**US-09**: Como desenvolvedor, quero trocar o provider de LLM (Gemini, OpenAI, Anthropic) alterando apenas a configuracao.

**US-10**: Como desenvolvedor, quero que cada agente tenha guardrails que impedem atuacao fora do escopo definido.

**US-11**: Como desenvolvedor, quero avaliar sistematicamente a qualidade dos agentes via evals automatizados.

### P3 - UI

**US-12**: Como cliente, quero interagir com o sistema via interface de chat (Chainlit) que simula um atendimento bancario completo.

---

## Requirements

### AUTH - Autenticacao

- **AUTH-01**: O agente de triagem DEVE saudar o cliente e coletar CPF.
- **AUTH-02**: O agente de triagem DEVE coletar a data de nascimento apos o CPF.
- **AUTH-03**: O sistema DEVE validar CPF + data de nascimento contra `clientes.csv`.
- **AUTH-04**: WHEN autenticacao falha, THEN o sistema DEVE permitir ate 2 novas tentativas (3 total).
- **AUTH-05**: WHEN 3 tentativas falham consecutivamente, THEN o sistema DEVE encerrar o atendimento de forma amigavel.
- **AUTH-06**: WHEN autenticacao bem-sucedida, THEN o sistema DEVE identificar a necessidade do cliente e rotear para o agente correto.

### ROUTE - Roteamento

- **ROUTE-01**: O orquestrador DEVE rotear para o agente correto baseado na intencao do cliente.
- **ROUTE-02**: O handoff entre agentes DEVE ser transparente (cliente nao percebe a troca).
- **ROUTE-03**: O cliente DEVE poder voltar ao fluxo de triagem para acessar outro servico.

### CREDIT - Credito

- **CREDIT-01**: O agente de credito DEVE consultar e informar o limite atual do cliente.
- **CREDIT-02**: WHEN cliente solicita aumento, THEN o sistema DEVE registrar em `solicitacoes_aumento_limite.csv` com colunas: cpf_cliente, data_hora_solicitacao (ISO 8601), limite_atual, novo_limite_solicitado, status_pedido.
- **CREDIT-03**: WHEN score do cliente permite o novo limite (conforme `score_limite.csv`), THEN status = 'aprovado'.
- **CREDIT-04**: WHEN score do cliente NAO permite o novo limite, THEN status = 'rejeitado'.
- **CREDIT-05**: WHEN status = 'rejeitado', THEN o agente DEVE oferecer redirecionamento para o Agente de Entrevista de Credito.

### INTERVIEW - Entrevista de Credito

- **INTERVIEW-01**: O agente DEVE coletar: renda mensal, tipo de emprego (formal/autonomo/desempregado), despesas fixas mensais, numero de dependentes, existencia de dividas ativas.
- **INTERVIEW-02**: O agente DEVE calcular o novo score usando a formula ponderada definida (0-1000).
- **INTERVIEW-03**: O agente DEVE atualizar o score do cliente em `clientes.csv`.
- **INTERVIEW-04**: Apos atualizacao, o agente DEVE redirecionar para o Agente de Credito para nova analise.

### EXCHANGE - Cambio

- **EXCHANGE-01**: O agente DEVE consultar cotacao de moedas via API externa.
- **EXCHANGE-02**: O agente DEVE apresentar a cotacao ao cliente de forma clara.
- **EXCHANGE-03**: O agente DEVE encerrar o atendimento de cambio com mensagem amigavel.

### GUARD - Guardrails

- **GUARD-01**: Cada agente DEVE recusar solicitacoes fora do seu escopo definido.
- **GUARD-02**: O sistema DEVE sanitizar inputs do usuario (prevenir injection no prompt).
- **GUARD-03**: O sistema DEVE tratar erros de forma controlada (CSV inacessivel, API indisponivel, input invalido) sem interromper a interacao.

### LLM - Abstração de Provider

- **LLM-01**: O sistema DEVE definir uma interface abstrata LLMProvider com metodos: chat(), chat_with_tools().
- **LLM-02**: DEVE existir pelo menos uma implementacao concreta (GeminiProvider).
- **LLM-03**: Trocar de provider DEVE exigir apenas mudanca de configuracao, sem alterar codigo de agentes.

### EVAL - Avaliações

- **EVAL-01**: DEVE existir suite de eval para routing accuracy (intencao -> agente correto).
- **EVAL-02**: DEVE existir suite de eval para tool calling accuracy (input -> tool + params corretos).
- **EVAL-03**: DEVE existir suite de eval para guardrail pass rate (prompt adversarial -> recusa).
- **EVAL-04**: DEVE existir suite de eval para fluxos end-to-end (conversa completa -> resultado esperado).

### DATA - Geracao de Dados

- **DATA-01**: DEVE existir script de seed (`scripts/seed_data.py`) que gera dados fake usando Faker pt_BR.
- **DATA-02**: `clientes.csv` DEVE ter pelo menos 50 registros com distribuicao variada de scores (0-1000).
- **DATA-03**: `score_limite.csv` DEVE definir faixas de score -> limite maximo permitido.
- **DATA-04**: O script DEVE ser reprodutivel (seed fixa) para testes consistentes.
- **DATA-05**: `solicitacoes_aumento_limite.csv` DEVE ser criado vazio (apenas headers) pelo seed.

### UI - Interface

- **UI-01**: A aplicacao DEVE ter interface de chat via Chainlit.
- **UI-02**: A interface DEVE suportar streaming de respostas.
- **UI-03**: A interface DEVE manter historico da conversa durante a sessao.

---

## Edge Cases

- Cliente informa CPF em formatos diferentes (com/sem pontuacao).
- Cliente tenta solicitar limite negativo ou zero.
- API de cambio indisponivel.
- CSV corrompido ou inacessivel.
- Cliente tenta acessar servico sem autenticacao.
- Cliente pede algo completamente fora do escopo bancario.
- Cliente tenta manipular o prompt do agente (prompt injection).
- Score calculado ultrapassa o range 0-1000.

## Fora de Escopo

- Transferencias/PIX.
- Consulta de saldo.
- Abertura de conta.
- Persistencia em banco de dados (usa CSV conforme especificado).
- Deploy em producao.
- Autenticacao multi-fator.
