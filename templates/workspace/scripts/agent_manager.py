#!/usr/bin/env python3
"""Task orchestration manager for Codex workforce routing."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

DEFAULT_CONFIG = Path("orchestrator/manager-config.json")


@dataclass
class DispatchPacket:
    team: str
    stage: str
    action: str
    agent_id: str | None
    message: str


def load_config(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_intent(task: str, intent_keywords: Dict[str, List[str]], forced: str | None) -> str:
    if forced:
        return forced

    lowered = task.lower()
    scores: List[Tuple[int, str]] = []
    for intent, words in intent_keywords.items():
        score = sum(1 for word in words if word in lowered)
        scores.append((score, intent))

    scores.sort(reverse=True)
    top_score, top_intent = scores[0]
    if top_score == 0:
        return "feature"
    return top_intent


def choose_builders(intent: str, task: str, config: Dict[str, Any]) -> List[str]:
    builders = list(config["workflows"][intent]["builders"])
    lowered = task.lower()

    # Bias builder selection based on lexical hints.
    wants_frontend = any(k in lowered for k in ["ui", "frontend", "react", "css", "page", "component"])
    wants_backend = any(k in lowered for k in ["api", "backend", "service", "database", "endpoint"]) 
    wants_ops = any(k in lowered for k in ["deploy", "pipeline", "infra", "docker", "script", "ci", "cd"])

    selected: List[str] = []
    if "team-backend" in builders and (wants_backend or not wants_frontend):
        selected.append("team-backend")
    if "team-frontend" in builders and wants_frontend:
        selected.append("team-frontend")
    if "team-ops" in builders and wants_ops:
        selected.append("team-ops")

    if not selected:
        selected = builders[:1]

    return selected


def build_dispatch_message(team: str, stage: str, objective: str, intent: str) -> str:
    if stage == "recon":
        return (
            f"Objective: {objective}\n"
            f"Intent: {intent}\n"
            "Task: map impacted files, dependencies, and risks; return concise implementation plan."
        )
    if stage == "build":
        return (
            f"Objective: {objective}\n"
            f"Intent: {intent}\n"
            "Task: implement scoped changes, keep edits isolated, and return changed files + checks run."
        )
    if stage == "security":
        return (
            f"Objective: {objective}\n"
            "Task: review and patch security issues in produced changes. Return findings by severity first."
        )
    if stage == "qa":
        return (
            f"Objective: {objective}\n"
            "Task: validate behavior with focused tests/smokes. Return failures first and residual risks."
        )
    return (
        f"Objective: {objective}\n"
        "Task: update docs/runbook/changelog and summarize operator impact concisely."
    )


def plan_dispatch(task: str, intent: str, config: Dict[str, Any]) -> Dict[str, Any]:
    workflow = config["workflows"][intent]
    team_registry = config["team_registry"]

    packets: List[DispatchPacket] = []

    # Stage 1: recon
    recon_id = team_registry.get("team-recon", {}).get("agent_id")
    packets.append(
        DispatchPacket(
            team="team-recon",
            stage="recon",
            action="send_input" if recon_id else "spawn_required",
            agent_id=recon_id,
            message=build_dispatch_message("team-recon", "recon", task, intent),
        )
    )

    assigned_teams = {"team-recon"}

    # Stage 2: builders (parallel)
    for team in choose_builders(intent, task, config):
        if team not in workflow["include"]:
            continue
        if team in assigned_teams:
            continue
        team_id = team_registry.get(team, {}).get("agent_id")
        packets.append(
            DispatchPacket(
                team=team,
                stage="build",
                action="send_input" if team_id else "spawn_required",
                agent_id=team_id,
                message=build_dispatch_message(team, "build", task, intent),
            )
        )
        assigned_teams.add(team)

    # Stage 3: security
    if workflow.get("needs_security"):
        team = "team-security"
        if team in assigned_teams:
            pass
        else:
            team_id = team_registry.get(team, {}).get("agent_id")
            packets.append(
                DispatchPacket(
                    team=team,
                    stage="security",
                    action="send_input" if team_id else "spawn_required",
                    agent_id=team_id,
                    message=build_dispatch_message(team, "security", task, intent),
                )
            )
            assigned_teams.add(team)

    # Stage 4: qa
    if workflow.get("needs_qa"):
        team = "team-qa"
        if team not in assigned_teams:
            team_id = team_registry.get(team, {}).get("agent_id")
            packets.append(
                DispatchPacket(
                    team=team,
                    stage="qa",
                    action="send_input" if team_id else "spawn_required",
                    agent_id=team_id,
                    message=build_dispatch_message(team, "qa", task, intent),
                )
            )
            assigned_teams.add(team)

    # Stage 5: docs
    if workflow.get("needs_docs"):
        team = "team-docs"
        if team not in assigned_teams:
            team_id = team_registry.get(team, {}).get("agent_id")
            packets.append(
                DispatchPacket(
                    team=team,
                    stage="docs",
                    action="send_input" if team_id else "spawn_required",
                    agent_id=team_id,
                    message=build_dispatch_message(team, "docs", task, intent),
                )
            )
            assigned_teams.add(team)

    stages: Dict[str, List[Dict[str, Any]]] = {}
    for packet in packets:
        stages.setdefault(packet.stage, []).append(
            {
                "team": packet.team,
                "action": packet.action,
                "agent_id": packet.agent_id,
                "message": packet.message,
            }
        )

    return {
        "task": task,
        "intent": intent,
        "stages": stages,
        "audit_command": config["runtime"]["default_check_command"],
    }


def render_text(plan: Dict[str, Any]) -> str:
    out: List[str] = []
    out.append(f"Intent: {plan['intent']}")
    for stage in ["recon", "build", "security", "qa", "docs"]:
        entries = plan["stages"].get(stage, [])
        if not entries:
            continue
        out.append(f"\n[{stage.upper()}]")
        for item in entries:
            out.append(
                f"- {item['team']} | {item['action']}"
                + (f" | agent_id={item['agent_id']}" if item["agent_id"] else "")
            )
    out.append(f"\nPost-check: {plan['audit_command']}")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto-route tasks to workforce teams")
    parser.add_argument("--task", required=True, help="Task or response objective")
    parser.add_argument("--intent", choices=["feature", "bugfix", "security", "docs", "ops", "response"], help="Override auto intent classification")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to manager config JSON")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--write-plan", help="Optional path to write JSON plan")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(Path(args.config))
    intent = classify_intent(args.task, config["intent_keywords"], args.intent)
    plan = plan_dispatch(args.task, intent, config)

    if args.write_plan:
        Path(args.write_plan).write_text(json.dumps(plan, indent=2), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(plan, separators=(",", ":"), sort_keys=True))
    else:
        print(render_text(plan))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
