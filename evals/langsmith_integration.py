"""Integracao dos evals com LangSmith."""
import os
import logging
from datetime import datetime, timezone

from evals.report import EvalReport

logger = logging.getLogger(__name__)

try:
    from langsmith import Client as LangSmithClient
    _HAS_LANGSMITH = True
except ImportError:
    _HAS_LANGSMITH = False


def push_eval_to_langsmith(report: EvalReport) -> str | None:
    """Envia resultados de eval para o LangSmith como um experiment.

    Returns:
        URL do experiment no LangSmith, ou None se nao configurado.
    """
    api_key = os.getenv("LANGSMITH_API_KEY", "")
    if not api_key or not _HAS_LANGSMITH:
        logger.info("LangSmith nao configurado, pulando upload")
        return None

    client = LangSmithClient()
    project_name = os.getenv("LANGSMITH_PROJECT", "case-banco-agil")

    dataset_name = f"eval_{report.suite}"

    # Cria ou busca o dataset
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except Exception:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description=f"Dataset de eval para suite: {report.suite}",
        )

    # Registra cada case como exemplo no dataset (se nao existir)
    existing_examples = list(client.list_examples(dataset_id=dataset.id))
    existing_inputs = {str(ex.inputs) for ex in existing_examples}

    for result in report.results:
        inputs = {"input": result["input"]}
        outputs = {"expected": result["expected"]}

        if str(inputs) not in existing_inputs:
            client.create_example(
                inputs=inputs,
                outputs=outputs,
                dataset_id=dataset.id,
            )

    # Cria run de avaliacao
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    experiment_name = f"{report.suite}_{timestamp}"

    for result in report.results:
        run = client.create_run(
            name=f"eval_{report.suite}",
            run_type="chain",
            inputs={"input": result["input"]},
            outputs={
                "actual": result.get("actual", ""),
                "expected": result.get("expected", ""),
                "pass": result.get("pass", False),
            },
            project_name=project_name,
            tags=[f"eval:{report.suite}", f"experiment:{experiment_name}"],
            extra={
                "metadata": {
                    "suite": report.suite,
                    "accuracy": report.accuracy,
                    "experiment": experiment_name,
                }
            },
        )

    logger.info(f"Eval '{report.suite}' enviado ao LangSmith (project: {project_name})")
    logger.info(f"  Experiment: {experiment_name}")
    logger.info(f"  {report.total} runs criados")

    return experiment_name
