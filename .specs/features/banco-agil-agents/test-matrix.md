# Banco Agil - Test Matrix

**Spec**: `.specs/features/banco-agil-agents/spec.md`
**Status**: 33 requirements, 33 mapped, 0 GREEN

## Services (logica pura, deterministico)

| Req ID | Test Location | Test Name | RED | GREEN | Notes |
|--------|---------------|-----------|-----|-------|-------|
| AUTH-03 | tests/services/test_auth.py | test_authenticate_valid_cpf_and_dob | - | - | - |
| AUTH-03 | tests/services/test_auth.py | test_authenticate_invalid_cpf | - | - | - |
| AUTH-03 | tests/services/test_auth.py | test_authenticate_wrong_dob | - | - | - |
| AUTH-03 | tests/services/test_auth.py | test_authenticate_cpf_with_punctuation | - | - | Edge case |
| AUTH-04 | tests/services/test_auth.py | test_authenticate_allows_3_attempts | - | - | - |
| AUTH-05 | tests/services/test_auth.py | test_authenticate_locks_after_3_failures | - | - | - |
| CREDIT-01 | tests/services/test_credit.py | test_get_credit_limit_returns_current_limit | - | - | - |
| CREDIT-02 | tests/services/test_credit.py | test_request_increase_creates_csv_record | - | - | - |
| CREDIT-02 | tests/services/test_credit.py | test_request_increase_record_has_correct_columns | - | - | - |
| CREDIT-03 | tests/services/test_credit.py | test_request_increase_approved_when_score_sufficient | - | - | - |
| CREDIT-04 | tests/services/test_credit.py | test_request_increase_rejected_when_score_insufficient | - | - | - |
| CREDIT-04 | tests/services/test_credit.py | test_request_increase_negative_amount_rejected | - | - | Edge case |
| INTERVIEW-02 | tests/services/test_score.py | test_calculate_score_formal_no_debts | - | - | - |
| INTERVIEW-02 | tests/services/test_score.py | test_calculate_score_unemployed_with_debts | - | - | - |
| INTERVIEW-02 | tests/services/test_score.py | test_calculate_score_clamped_to_0_1000 | - | - | Edge case |
| INTERVIEW-02 | tests/services/test_score.py | test_calculate_score_autonomous_worker | - | - | - |
| INTERVIEW-03 | tests/services/test_score.py | test_update_score_persists_to_csv | - | - | - |

## Tools (I/O, CSV, API)

| Req ID | Test Location | Test Name | RED | GREEN | Notes |
|--------|---------------|-----------|-----|-------|-------|
| DATA-01 | tests/tools/test_csv_ops.py | test_read_csv_returns_list_of_dicts | - | - | - |
| DATA-01 | tests/tools/test_csv_ops.py | test_write_csv_appends_row | - | - | - |
| DATA-01 | tests/tools/test_csv_ops.py | test_update_csv_row_by_key | - | - | - |
| GUARD-03 | tests/tools/test_csv_ops.py | test_read_csv_missing_file_raises_error | - | - | Edge case |
| EXCHANGE-01 | tests/tools/test_exchange_api.py | test_fetch_exchange_rate_returns_float | - | - | - |
| EXCHANGE-01 | tests/tools/test_exchange_api.py | test_fetch_exchange_rate_api_unavailable | - | - | Edge case |

## Models (dataclasses, validacao)

| Req ID | Test Location | Test Name | RED | GREEN | Notes |
|--------|---------------|-----------|-----|-------|-------|
| AUTH-03 | tests/models/test_cliente.py | test_cliente_from_csv_row | - | - | - |
| AUTH-03 | tests/models/test_cliente.py | test_cliente_cpf_normalized | - | - | - |
| CREDIT-02 | tests/models/test_solicitacao.py | test_solicitacao_has_required_fields | - | - | - |
| CREDIT-02 | tests/models/test_solicitacao.py | test_solicitacao_timestamp_is_iso8601 | - | - | - |

## Core (orquestrador, guardrails, LLM abstraction)

| Req ID | Test Location | Test Name | RED | GREEN | Notes |
|--------|---------------|-----------|-----|-------|-------|
| LLM-01 | tests/core/test_llm_provider.py | test_llm_provider_interface_has_required_methods | - | - | - |
| LLM-03 | tests/core/test_llm_provider.py | test_factory_creates_provider_from_config | - | - | - |
| GUARD-01 | tests/core/test_guardrails.py | test_agent_rejects_out_of_scope_request | - | - | - |
| GUARD-02 | tests/core/test_guardrails.py | test_input_sanitization_strips_injection | - | - | - |
| ROUTE-01 | tests/core/test_orchestrator.py | test_orchestrator_routes_credit_intent | - | - | - |
| ROUTE-01 | tests/core/test_orchestrator.py | test_orchestrator_routes_exchange_intent | - | - | - |

## Data Seed

| Req ID | Test Location | Test Name | RED | GREEN | Notes |
|--------|---------------|-----------|-----|-------|-------|
| DATA-01 | tests/test_seed.py | test_seed_generates_clientes_csv | - | - | - |
| DATA-02 | tests/test_seed.py | test_seed_generates_at_least_50_clients | - | - | - |
| DATA-03 | tests/test_seed.py | test_seed_generates_score_limite_csv | - | - | - |
| DATA-04 | tests/test_seed.py | test_seed_is_reproducible | - | - | - |
| DATA-05 | tests/test_seed.py | test_seed_creates_empty_solicitacoes_csv | - | - | - |
