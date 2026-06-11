from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
from typing import Sequence


@dataclass(frozen=True)
class ReportPipelineConfig:
    root: Path
    python_bin: str = "python"
    callback_text: str | None = None
    dry_run: bool = False
    use_cache: bool = False


def _run(cmd: Sequence[str], cwd: Path, dry_run: bool = False) -> int:
    if dry_run:
        print("[dry-run]", " ".join(cmd))
        return 0
    proc = subprocess.run(cmd, cwd=str(cwd))
    return int(proc.returncode)


def _notify(text: str | None, ok: bool, cwd: Path, dry_run: bool = False) -> None:
    if not text:
        return
    if shutil.which("openclaw") is None:
        return

    msg = text if ok else f"Failed: {text}"
    cmd = ["openclaw", "system", "event", "--text", msg, "--mode", "now"]
    _run(cmd, cwd=cwd, dry_run=dry_run)


def _insight_outputs(root: Path, stage: str) -> list[Path]:
    base = root / "reports" / "artifacts" / "updownwave"
    if stage == "all":
        return [base / "insights_q1_q14.json", base / "insights_q1_q14.md"]
    return [base / f"insights_{stage}.json", base / f"insights_{stage}.md"]


def run_build(config: ReportPipelineConfig) -> int:
    if config.use_cache:
        report = config.root / "reports" / "site" / "factors" / "updownwave" / "report.html"
        manifest = config.root / "reports" / "artifacts" / "updownwave" / "manifest.json"
        if report.exists() and manifest.exists():
            print("[cache-hit] build stage skipped (report + manifest already exist)")
            return 0

    cmd = [config.python_bin, "scripts/build_updownwave_report.py"]
    return _run(cmd, cwd=config.root, dry_run=config.dry_run)


def run_insights(config: ReportPipelineConfig, stage: str = "all") -> int:
    if config.use_cache:
        outs = _insight_outputs(config.root, stage=stage)
        if all(p.exists() for p in outs):
            print(f"[cache-hit] insights stage skipped ({stage})")
            return 0

    cmd = [config.python_bin, "scripts/build_updownwave_insights.py", "--stage", stage]
    return _run(cmd, cwd=config.root, dry_run=config.dry_run)


def run_publish(config: ReportPipelineConfig) -> int:
    cmd = ["bash", "scripts/publish_report_site.sh"]
    return _run(cmd, cwd=config.root, dry_run=config.dry_run)


def run_pipeline(config: ReportPipelineConfig, stage: str = "all") -> int:
    stage = stage.lower()
    ok = True

    stage_insights = {"insights", "q1_q3", "q4_q6", "q7_q9", "q10_q14"}
    allowed = {"all", "build", "publish", *stage_insights}
    if stage not in allowed:
        raise ValueError(f"Unsupported stage: {stage}")

    if stage in {"all", "build"}:
        rc = run_build(config)
        ok = ok and (rc == 0)
        if rc != 0:
            _notify(config.callback_text, ok=False, cwd=config.root, dry_run=config.dry_run)
            return rc

    if stage in {"all"} | stage_insights:
        insight_stage = "all" if stage in {"all", "insights"} else stage
        rc = run_insights(config, stage=insight_stage)
        ok = ok and (rc == 0)
        if rc != 0:
            _notify(config.callback_text, ok=False, cwd=config.root, dry_run=config.dry_run)
            return rc

    if stage in {"all", "publish"}:
        rc = run_publish(config)
        ok = ok and (rc == 0)
        if rc != 0:
            _notify(config.callback_text, ok=False, cwd=config.root, dry_run=config.dry_run)
            return rc

    _notify(config.callback_text, ok=ok, cwd=config.root, dry_run=config.dry_run)
    return 0
