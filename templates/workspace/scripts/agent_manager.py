#!/usr/bin/env python3
"""Task orchestration manager for Codex workforce routing."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Dict, List, Tuple

DEFAULT_CONFIG = Path("orchestrator/manager-config.json")
DEFAULT_CODEX_AGENT_TEAM_ROOTS = [
    Path("/mnt/u/home/ttracx/codex_agents/teams"),
    Path("/home/ttracx/codex_agents/teams"),
]


@dataclass
class DispatchPacket:
    team: str
    stage: str
    action: str
    agent_id: str | None
    message: str


def load_config(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze_requirements(task: str) -> Dict[str, bool]:
    lowered = task.lower()
    def has_term(text: str, term: str) -> bool:
        if re.search(r"^[a-z0-9]+$", term) and len(term) <= 3:
            return re.search(rf"\b{re.escape(term)}\b", text) is not None
        return term in text

    signals = {
        "web": ["web", "website", "frontend", "ui", "landing page"],
        "backend": ["api", "backend", "service", "database", "endpoint"],
        "ops": ["deploy", "pipeline", "ci", "cd", "infra", "docker"],
        "security": ["security", "auth", "oauth", "compliance", "vulnerability"],
        "branding": ["brand", "campaign", "social media", "linkedin", "graphics", "content"],
        "data": ["data", "analytics", "etl", "warehouse", "reporting"],
        "ai": ["ai", "llm", "agent", "rag", "model"],
        "ios": ["ios", "swift", "swiftui", "macos", "apple"],
        "quantum": ["quantum", "qubit", "circuit"],
        "verification": ["test", "verify", "validate", "qa", "proof"],
    }
    return {k: any(has_term(lowered, w) for w in words) for k, words in signals.items()}


def _resolve_codex_agent_root(config: Dict[str, Any]) -> Path | None:
    roots = config.get("codex_agents", {}).get("teams_root_candidates", [])
    candidates = [Path(p) for p in roots] if roots else DEFAULT_CODEX_AGENT_TEAM_ROOTS
    for root in candidates:
        if root.is_dir():
            return root
    return None


def load_codex_team_catalog(config: Dict[str, Any]) -> Dict[str, List[str]]:
    root = _resolve_codex_agent_root(config)
    if not root:
        return {}

    catalog: Dict[str, List[str]] = {}
    for team_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        members = sorted([f.stem for f in team_dir.glob("*.md") if f.is_file()])
        catalog[team_dir.name] = members
    return catalog


def select_codex_teams(requirements: Dict[str, bool], catalog: Dict[str, List[str]]) -> List[str]:
    mapped: List[str] = []
    map_rules = [
        ("web", "web-development"),
        ("backend", "web-development"),
        ("ops", "devops-infrastructure"),
        ("security", "security"),
        ("branding", "branding"),
        ("data", "data-science"),
        ("ai", "ai-development"),
        ("ios", "ios-development"),
        ("quantum", "quantum-computing"),
        ("verification", "cov-verification"),
    ]
    for key, team_name in map_rules:
        if requirements.get(key) and team_name in catalog and team_name not in mapped:
            mapped.append(team_name)

    # Always include orchestration brains when available.
    for orchestration_team in ("auto-orchestration", "orchestration"):
        if orchestration_team in catalog and orchestration_team not in mapped:
            mapped.insert(0, orchestration_team)
            break

    return mapped


def build_automation_pipeline(
    task: str,
    intent: str,
    selected_codex_teams: List[str],
    stages: Dict[str, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    build_teams = [entry["team"] for entry in stages.get("build", [])]
    security_teams = [entry["team"] for entry in stages.get("security", [])]
    qa_teams = [entry["team"] for entry in stages.get("qa", [])]
    docs_teams = [entry["team"] for entry in stages.get("docs", [])]

    return [
        {
            "phase": "requirements_understanding",
            "objective": "understand task requirements and constraints before routing",
            "task": task,
            "intent": intent,
            "codex_agent_teams": selected_codex_teams,
            "workforce_stage": "recon",
        },
        {
            "phase": "demo_ready_app_planning",
            "objective": "produce a demo-ready app plan for the feature",
            "deliverables": [
                "feature scope",
                "MVP slice definition",
                "demo flow storyboard",
                "acceptance checklist",
            ],
            "workforce_stage": "build",
            "assigned_workforce_teams": build_teams,
            "codex_agent_teams": selected_codex_teams,
        },
        {
            "phase": "route_and_assignment_creation",
            "objective": "create assignments and stage routing from requirements",
            "workforce_stage": "build",
            "assigned_workforce_teams": build_teams,
        },
        {
            "phase": "automation_pipeline_execution",
            "objective": "run build then gates then docs automation",
            "workforce_stages": ["build", "security", "qa", "docs"],
            "assigned_security_teams": security_teams,
            "assigned_qa_teams": qa_teams,
            "assigned_docs_teams": docs_teams,
        },
    ]


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
    workflow = config["workflows"].get(intent) or config["workflows"]["feature"]
    builders = list(workflow["builders"])
    lowered = task.lower()

    # Bias builder selection based on lexical hints.
    wants_frontend = any(k in lowered for k in ["ui", "frontend", "react", "css", "page", "component"])
    wants_backend = any(k in lowered for k in ["api", "backend", "service", "database", "endpoint"]) 
    wants_ops = any(k in lowered for k in ["deploy", "pipeline", "infra", "docker", "script"])
    if re.search(r"\bci\b|\bcd\b", lowered):
        wants_ops = True
    wants_app = any(k in lowered for k in ["app", "web app", "mobile app", "saas", "full stack", "full-stack"])

    if intent == "app_generation" or wants_app:
        selected = [team for team in ["team-backend", "team-frontend", "team-ops"] if team in builders]
        return selected if selected else builders[:1]

    if intent == "marketing_campaign":
        selected = [team for team in ["team-frontend", "team-docs", "team-ops"] if team in builders]
        return selected if selected else builders[:1]

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
    # Enforce feature-first handling for every task.
    workflow = config["workflows"]["feature"]
    resolved_intent = "feature"
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

    requirements = analyze_requirements(task)
    codex_catalog = load_codex_team_catalog(config)
    selected_codex_teams = select_codex_teams(requirements, codex_catalog)
    pipeline = build_automation_pipeline(task, resolved_intent, selected_codex_teams, stages)
    route_assignments = [
        {"stage": stage_name, "team": entry["team"], "action": entry["action"], "agent_id": entry["agent_id"]}
        for stage_name, entries in stages.items()
        for entry in entries
    ]
    codex_root = _resolve_codex_agent_root(config)

    return {
        "task": task,
        "intent_requested": intent,
        "intent": resolved_intent,
        "mode": "feature_first_demo_ready",
        "requirement_analysis": {
            "categories": requirements,
            "matched_categories": [k for k, v in requirements.items() if v],
            "mode": "requirements_first",
        },
        "codex_agents": {
            "teams_root": str(codex_root) if codex_root else None,
            "catalog_size": len(codex_catalog),
            "selected_teams": selected_codex_teams,
        },
        "route_assignments": route_assignments,
        "pipeline_automation": {
            "mode": "requirements_then_routing_then_automation",
            "phases": pipeline,
        },
        "stages": stages,
        "audit_command": config["runtime"]["default_check_command"],
    }


def render_text(plan: Dict[str, Any]) -> str:
    out: List[str] = []
    out.append(f"Intent: {plan['intent']}")
    matched = plan.get("requirement_analysis", {}).get("matched_categories", [])
    out.append("Requirements: " + (", ".join(matched) if matched else "none-signaled"))
    codex_selected = plan.get("codex_agents", {}).get("selected_teams", [])
    if codex_selected:
        out.append("Codex Teams: " + ", ".join(codex_selected))
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
    parser.add_argument("--intent", help="Override auto intent classification")
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
