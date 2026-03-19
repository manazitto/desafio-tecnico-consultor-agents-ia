"""CLI para execucao de evals.

Uso:
    python -m evals.run --suite routing
    python -m evals.run --suite tool_calling
    python -m evals.run --suite guardrails
    python -m evals.run --suite all
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from banco_agil.config import GEMINI_API_KEY, LLM_MODEL, CLIENTES_CSV, SCORE_LIMITE_CSV, SOLICITACOES_CSV
from banco_agil.core.llm.gemini import GeminiProvider
from banco_agil.services.auth import AuthService
from banco_agil.services.credit import CreditService
from banco_agil.services.score import ScoreService
from banco_agil.agents.triage import TriageAgent
from banco_agil.agents.credit import CreditAgent
from banco_agil.agents.credit_interview import CreditInterviewAgent
from banco_agil.agents.exchange import ExchangeAgent
from evals.runners.single_turn import SingleTurnRunner
from evals.report import EvalReport

EVALS_DIR = Path(__file__).parent
DATASETS_DIR = EVALS_DIR / "datasets"
REPORTS_DIR = EVALS_DIR / "reports"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def setup():
    """Configura LLM e agentes para os evals."""
    llm = GeminiProvider(api_key=GEMINI_API_KEY, model=LLM_MODEL)
    auth_service = AuthService(csv_path=CLIENTES_CSV)
    credit_service = CreditService(score_limite_path=SCORE_LIMITE_CSV, solicitacoes_path=SOLICITACOES_CSV)
    score_service = ScoreService()

    agents = {
        "triage": TriageAgent(auth_service=auth_service),
        "credit": CreditAgent(credit_service=credit_service),
        "credit_interview": CreditInterviewAgent(score_service=score_service, clientes_csv_path=CLIENTES_CSV),
        "exchange": ExchangeAgent(),
    }
    return llm, agents


def save_report(report: EvalReport):
    """Salva relatorio em JSON."""
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"{report.suite}_{timestamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report.to_json())
    logger.info(f"Relatorio salvo em: {path}")


def run_routing(llm, agents):
    """Executa eval de routing."""
    runner = SingleTurnRunner(llm_provider=llm)
    report = runner.run_routing_eval(
        dataset_path=str(DATASETS_DIR / "routing_cases.jsonl"),
        agents=agents,
    )
    return report


def run_tool_calling(llm, agents):
    """Executa eval de tool calling."""
    runner = SingleTurnRunner(llm_provider=llm)
    reports = []

    agent_map = {
        "triage": agents["triage"],
        "credit": agents["credit"],
        "exchange": agents["exchange"],
    }

    from evals.datasets.loader import load_dataset
    all_cases = load_dataset(str(DATASETS_DIR / "tool_calling_cases.jsonl"))

    for agent_name, agent in agent_map.items():
        agent_cases = [c for c in all_cases if c.get("agent") == agent_name]
        if not agent_cases:
            continue

        tmp_path = DATASETS_DIR / f"_tmp_{agent_name}_tools.jsonl"
        with open(tmp_path, "w") as f:
            for case in agent_cases:
                f.write(json.dumps(case, ensure_ascii=False) + "\n")

        report = runner.run_tool_calling_eval(
            dataset_path=str(tmp_path),
            agent=agent,
        )
        report.suite = f"tool_calling_{agent_name}"
        reports.append(report)
        tmp_path.unlink()

    total = sum(r.total for r in reports)
    passed = sum(r.passed for r in reports)
    all_results = [r for report in reports for r in report.results]

    return EvalReport(
        suite="tool_calling",
        total=total,
        passed=passed,
        failed=total - passed,
        accuracy=passed / total if total else 0.0,
        results=all_results,
    )


def run_guardrails(llm, agents):
    """Executa eval de guardrails."""
    runner = SingleTurnRunner(llm_provider=llm)

    from evals.datasets.loader import load_dataset
    all_cases = load_dataset(str(DATASETS_DIR / "guardrail_cases.jsonl"))

    all_results = []
    for case in all_cases:
        agent_name = case.get("agent", "triage")
        agent = agents[agent_name]

        tmp_path = DATASETS_DIR / f"_tmp_guard.jsonl"
        with open(tmp_path, "w") as f:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

        report = runner.run_guardrail_eval(str(tmp_path), agent)
        all_results.extend(report.results)
        tmp_path.unlink()

    passed = sum(1 for r in all_results if r["pass"])
    return EvalReport(
        suite="guardrails",
        total=len(all_results),
        passed=passed,
        failed=len(all_results) - passed,
        accuracy=passed / len(all_results) if all_results else 0.0,
        results=all_results,
    )


SUITE_RUNNERS = {
    "routing": run_routing,
    "tool_calling": run_tool_calling,
    "guardrails": run_guardrails,
}


def main():
    parser = argparse.ArgumentParser(description="Banco Agil - Eval Runner")
    parser.add_argument("--suite", choices=[*SUITE_RUNNERS.keys(), "all"], required=True)
    parser.add_argument("--save", action="store_true", help="Salvar relatorio em JSON")
    parser.add_argument("--langsmith", action="store_true", help="Enviar resultados para LangSmith")
    args = parser.parse_args()

    llm, agents = setup()

    suites = SUITE_RUNNERS.keys() if args.suite == "all" else [args.suite]

    for suite_name in suites:
        logger.info(f"\n{'='*60}")
        logger.info(f"  EVAL: {suite_name.upper()}")
        logger.info(f"{'='*60}\n")

        report = SUITE_RUNNERS[suite_name](llm, agents)

        logger.info(f"\n{report.summary()}")

        for r in report.results:
            status = "PASS" if r["pass"] else "FAIL"
            logger.info(f"  [{status}] {r['input'][:60]}")
            if not r["pass"]:
                logger.info(f"         expected: {r['expected']}")
                logger.info(f"         actual:   {r['actual']}")

        if args.save:
            save_report(report)

        if args.langsmith:
            from evals.langsmith_integration import push_eval_to_langsmith
            push_eval_to_langsmith(report)


if __name__ == "__main__":
    main()
