"""Paper evaluation harness for the execution-evidence demo."""

from .compare import compare_runs
from .falsification import run_falsification_checks
from .review import review_run_directory
from .runner import run_suite
from .modes import DEFAULT_COMPARISON_MODES, EXTERNAL_COMPARISON_MODES, FRAMEWORK_PAIR_MODES, LANGCHAIN_PAIR_MODES, TOP_JOURNAL_MODES, list_modes
from .suite import load_tasks, validate_task_suite

__all__ = [
    "compare_runs",
    "DEFAULT_COMPARISON_MODES",
    "EXTERNAL_COMPARISON_MODES",
    "FRAMEWORK_PAIR_MODES",
    "LANGCHAIN_PAIR_MODES",
    "TOP_JOURNAL_MODES",
    "load_tasks",
    "list_modes",
    "run_falsification_checks",
    "review_run_directory",
    "run_suite",
    "validate_task_suite",
]
