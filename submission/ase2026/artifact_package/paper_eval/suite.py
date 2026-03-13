"""Task-suite loading and validation."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .common import EXPECTED_CATEGORY_COUNTS, EXPORTED_FILES, TASK_DIR, load_json

REQUIRED_TASK_FIELDS = [
    "task_id",
    "category",
    "title",
    "goal",
    "input_payload",
    "expected_artifacts",
    "budget_policy",
    "approval_policy",
    "tamper_case",
    "notes",
]


def load_tasks(task_dir: Path | None = None) -> list[dict[str, Any]]:
    directory = task_dir or TASK_DIR
    return [load_json(path) for path in sorted(directory.glob("task-*.json"))]


def validate_task_suite(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    counts: Counter[str] = Counter()
    seen_ids: set[str] = set()

    for task in tasks:
        task_id = task.get("task_id")
        if not isinstance(task_id, str):
            errors.append("task is missing a string task_id")
            continue
        if task_id in seen_ids:
            errors.append(f"{task_id}: duplicate task_id")
        seen_ids.add(task_id)

        for field in REQUIRED_TASK_FIELDS:
            if field not in task:
                errors.append(f"{task_id}: missing required field {field}")

        category = task.get("category")
        if category not in EXPECTED_CATEGORY_COUNTS:
            errors.append(f"{task_id}: invalid category {category!r}")
        else:
            counts[category] += 1

        for field in ("title", "goal", "notes"):
            if field in task and not isinstance(task[field], str):
                errors.append(f"{task_id}: field {field} must be a string")

        for field in ("input_payload", "budget_policy", "approval_policy"):
            if field in task and not isinstance(task[field], dict):
                errors.append(f"{task_id}: field {field} must be an object")

        expected_artifacts = task.get("expected_artifacts")
        if expected_artifacts != EXPORTED_FILES:
            errors.append(f"{task_id}: expected_artifacts must exactly equal {EXPORTED_FILES}")

        tamper_case = task.get("tamper_case")
        if category == "tamper_scenario" and not isinstance(tamper_case, dict):
            errors.append(f"{task_id}: tamper_scenario tasks must define a tamper_case object")
        if category != "tamper_scenario" and tamper_case is not None:
            errors.append(f"{task_id}: non-tamper tasks must set tamper_case to null")

        approval_policy = task.get("approval_policy", {})
        if category == "approval_required" and approval_policy.get("requires_approval") is not True:
            errors.append(f"{task_id}: approval_required tasks must require approval")

        budget_policy = task.get("budget_policy", {})
        if category == "budget_constrained":
            if budget_policy.get("usd_limit") is None and budget_policy.get("token_limit") is None:
                errors.append(f"{task_id}: budget_constrained tasks must set a usd_limit or token_limit")

    if len(tasks) != sum(EXPECTED_CATEGORY_COUNTS.values()):
        errors.append(
            f"task suite must contain {sum(EXPECTED_CATEGORY_COUNTS.values())} tasks, found {len(tasks)}"
        )

    for category, expected_count in EXPECTED_CATEGORY_COUNTS.items():
        actual_count = counts.get(category, 0)
        if actual_count != expected_count:
            errors.append(f"category {category} must contain {expected_count} tasks, found {actual_count}")

    return {
        "valid": not errors,
        "errors": errors,
        "counts": {category: counts.get(category, 0) for category in EXPECTED_CATEGORY_COUNTS},
        "total_tasks": len(tasks),
    }


def find_task(task_id: str, tasks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    for task in tasks or load_tasks():
        if task["task_id"] == task_id:
            return task
    raise KeyError(f"unknown task_id: {task_id}")
