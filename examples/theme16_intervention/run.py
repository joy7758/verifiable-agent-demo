"""Local operational fixture / 本地操作性小样；逻辑时钟不代表真人反应时间。"""
from __future__ import annotations

import argparse
import json
import platform
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from paper_eval.common import sha256_digest, write_json

HERE = Path(__file__).resolve().parent


def provider(db: Path, event: dict) -> dict:
    """Write actual local state / 写入实际本地状态；不接收案例编号或预期答案。"""
    with sqlite3.connect(db) as con:
        if event["command"] == "INIT":
            con.execute("CREATE TABLE state (status TEXT, digest TEXT, deadline INTEGER, applied INTEGER, committed INTEGER, value INTEGER)")
            con.execute("INSERT INTO state VALUES ('QUEUED', ?, ?, NULL, NULL, 0)",
                        (event["action_digest"], event["commitment_tick"]))
            return {"status": "QUEUED"}
        status, digest, deadline, applied, committed, value = con.execute("SELECT * FROM state").fetchone()
        tick = event["tick"]
        # Deadline ordering is declared before the run / 截止点的处理顺序在运行前固定。
        if status == "QUEUED" and tick >= deadline:
            con.execute("UPDATE state SET status='EXECUTED', committed=?, value=1", (deadline,))
            status = "EXECUTED"
        if event["command"] == "CANCEL":
            if event["action_digest"] != digest:
                return {"received_tick": tick, "applied_tick": None, "reason": "ACTION_MISMATCH"}
            if status == "QUEUED":
                con.execute("UPDATE state SET status='CANCELLED', applied=?", (tick,))
                return {"received_tick": tick, "applied_tick": tick, "reason": "APPLIED"}
            return {"received_tick": tick, "applied_tick": None, "reason": "TOO_LATE_OR_TERMINAL"}
        return {"status": status}


def observer(db: Path) -> dict:
    """Separate read-only process / 单独只读进程；不读取执行确认。"""
    with sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True) as con:
        con.row_factory = sqlite3.Row
        return dict(con.execute("SELECT * FROM state").fetchone())


def invoke(mode: str, db: Path, payload: dict | None = None) -> dict:
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), mode, str(db)],
        input=json.dumps(payload), text=True, capture_output=True, check=True,
        timeout=15,
    )
    return json.loads(completed.stdout)


def assess(evidence: dict) -> dict:
    """Use observable facts only / 仅使用可观察事实；不接收实验分支或预期答案。"""
    observed = evidence["observation"]
    decision = evidence["decision"]
    if observed is None:
        return {"effect": "UNKNOWN", "intervention": "NOT_ESTABLISHED"}
    intent = evidence["intent"]
    if observed["digest"] != intent["action_digest"] or observed["deadline"] != intent["commitment_tick"]:
        return {"effect": "UNKNOWN", "intervention": "NOT_ESTABLISHED"}
    if observed["status"] == "EXECUTED" and observed["value"] == 1 and observed["committed"] == intent["commitment_tick"]:
        return {"effect": "EXECUTED", "intervention": "INEFFECTIVE" if decision else "NOT_REQUESTED"}
    if (decision and decision["action_digest"] == intent["action_digest"]
            and observed["status"] == "CANCELLED" and observed["value"] == 0
            and observed["committed"] is None and observed["applied"] is not None
            and decision["tick"] <= observed["applied"] < intent["commitment_tick"]):
        return {"effect": "CANCELLED", "intervention": "EFFECTIVE"}
    return {"effect": "UNKNOWN", "intervention": "NOT_ESTABLISHED"}


def run_case(case: dict, config: dict, directory: Path) -> dict:
    action = {"operation": "set_local_value", "target": "isolated-local-row", "value": 1, "version": "action-v1"}
    digest = sha256_digest(action)
    intent = {"action": action, "action_digest": digest,
              "commitment_tick": config["commitment_tick"],
              "governing_reference": config["profile"],
              "authority_applicability": "ASSUMED_CURRENT_FOR_SYNTHETIC_CANCEL",
              "evidence_presented": {"action_digest": digest, "commitment_tick": config["commitment_tick"]}}
    with tempfile.TemporaryDirectory(prefix="theme16-provider-") as temp:
        db = Path(temp) / "provider.sqlite"
        invoke("--provider", db, {"command": "INIT", "action_digest": digest, "commitment_tick": config["commitment_tick"]})
        decision = None if case["decision_tick"] is None else {
            "response": "CANCEL", "tick": case["decision_tick"],
            "action_digest": digest, "version": "action-v1", "human_authentication": "NOT_TESTED"}
        execution_confirmation = None
        if decision and not case["drop_delivery"]:
            execution_confirmation = invoke("--provider", db, {
                "command": "CANCEL", "tick": case["delivery_tick"], "action_digest": digest})
        invoke("--provider", db, {"command": "ADVANCE", "tick": config["terminal_observation_tick"]})
        observed = invoke("--observer", db) if case["observe"] else None
        evidence = {"intent": intent, "decision": decision,
                    "acknowledgement": {"received": case["acknowledgement"], "scope": "RECEIPT_ONLY"},
                    "execution_confirmation": execution_confirmation,
                    "observation": observed,
                    "observation_tick": config["terminal_observation_tick"] if observed else None,
                    "observation_scope": "one local terminal row; trusted same-host fixture"}
    verdict = assess(evidence)
    # Expected answers remain outside the evaluated mechanism / 预期答案留在被测机制之外。
    matches = verdict == case["expected"]
    audit = {"case_id": case["id"], "evidence_status": "LOCALLY_CAPTURED" if observed else "OBSERVATION_UNAVAILABLE",
             "human_decision": decision, "execution_verdict": verdict,
             "evidence_digest": sha256_digest(evidence), "signature": None,
             "comparison": "MATCH" if matches else "MISMATCH"}
    write_json(directory / "intent.json", intent)
    write_json(directory / "trace.json", evidence)
    write_json(directory / "evidence-bundle.json", {"evidence": evidence, "digest": sha256_digest(evidence)})
    write_json(directory / "replay-verdict.json", verdict)
    write_json(directory / "audit-receipt.json", audit)
    return {"case_id": case["id"], "expected": case["expected"], "observed": verdict,
            "acknowledged": case["acknowledgement"], "matches": matches,
            "decision_tick": case["decision_tick"],
            "cancel_applied_tick": observed["applied"] if observed else None,
            "commitment_tick": config["commitment_tick"],
            "response_margin_ticks": config["commitment_tick"] - observed["applied"] if observed and observed["applied"] is not None else None,
            "evidence_digest": audit["evidence_digest"]}


def campaign(output: Path) -> dict:
    config = json.loads((HERE / "cases.json").read_text())
    results = [run_case(case, config, output / case["id"]) for case in config["cases"]]
    # Deliberately defective comparator / 故意错误的对照：把收到确认当作成功。
    ack_only_mismatches = sum(
        ({"effect": "EXECUTED", "intervention": "NOT_REQUESTED"} if row["decision_tick"] is None else
         {"effect": "CANCELLED", "intervention": "EFFECTIVE"} if row["acknowledged"] else
         {"effect": "UNKNOWN", "intervention": "NOT_ESTABLISHED"}) != row["expected"]
        for row in results)
    report = {"profile": config["profile"], "clock": config["clock"],
              "cases_digest": sha256_digest(config), "python": platform.python_version(),
              "platform": platform.platform(), "cases": results,
              "matches": sum(row["matches"] for row in results), "total": len(results),
              "acknowledgement_only_comparator_mismatches": ack_only_mismatches,
              "human_participants": 0, "production_services": 0,
              "claims": "local logical-clock operational fixture only; no human capacity or wall-clock guarantee"}
    write_json(output / "report.json", report)
    return report


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in {"--provider", "--observer"}:
        path = Path(sys.argv[2])
        result = provider(path, json.load(sys.stdin)) if sys.argv[1] == "--provider" else observer(path)
        print(json.dumps(result, sort_keys=True))
    else:
        parser = argparse.ArgumentParser(description="Local intervention fixture / 本地干预小样")
        parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "theme16_intervention")
        args = parser.parse_args()
        report = campaign(args.output)
        print(json.dumps({"matches": report["matches"], "total": report["total"],
                          "ack_only_mismatches": report["acknowledgement_only_comparator_mismatches"]}))
        sys.exit(0 if report["matches"] == report["total"] else 1)
