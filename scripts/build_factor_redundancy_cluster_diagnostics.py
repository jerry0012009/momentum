#!/usr/bin/env python3
"""Build redundancy cluster and marginal information diagnostics — PM-31.

Reads pairwise redundancy matrix and quality scorecard, builds a redundancy
graph (edges where abs_spearman_corr >= threshold), finds connected components
as clusters, and computes marginal information scores for each factor.

Outputs (6 files):
  factor_redundancy_cluster_summary.csv
  factor_redundancy_cluster_members.csv
  factor_redundancy_cluster_representatives.csv
  factor_marginal_information_summary.csv
  factor_redundancy_cluster_payload.json
  factor_redundancy_cluster_manifest.json

Usage:
    python scripts/build_factor_redundancy_cluster_diagnostics.py
    python scripts/build_factor_redundancy_cluster_diagnostics.py --threshold 0.75

NOT production. NOT live trading. Research diagnostics only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
STATE_PATH = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_library_state.json"

# Input file names (relative to DIAG_DIR)
PAIRWISE_CSV = "factor_pairwise_redundancy.csv"
SCORECARD_CSV = "factor_quality_scorecard.csv"
REDUNDANCY_SUMMARY_CSV = "factor_redundancy_summary.csv"
DIAG_SUMMARY_CSV = "factor_diagnostics_summary.csv"
REGIME_CSV = "factor_regime_exposure_summary.csv"
CAPACITY_CSV = "factor_capacity_liquidity_summary.csv"
QUANTILE_CSV = "factor_quantile_shape_summary.csv"
STABILITY_CSV = "factor_rolling_stability_summary.csv"
DECILE_CSV = "factor_decile_shape_summary.csv"

# Default thresholds
DEFAULT_STRONG_THRESHOLD = 0.80
STRONG_EDGE_THRESHOLD = 0.90

# ── Helpers ────────────────────────────────────────────────────────────────

def _safe(val, default="N/A"):
    """Return default if val is NaN/None."""
    if val is None or (not isinstance(val, str) and pd.isna(val)):
        return default
    return val


def _families_in_cluster(factor_ids: list[str], family_map: dict[str, str]) -> list[str]:
    """Return sorted unique family list for a set of factor ids."""
    fams = set()
    for fid in factor_ids:
        f = family_map.get(fid)
        if f and not pd.isna(f):
            fams.add(str(f))
    return sorted(fams)


def _cluster_quality_class(size: int, avg_redundancy: float, n_strong: int) -> str:
    """Classify cluster quality based on size and redundancy level."""
    if size == 1:
        return "SINGLETON"
    if size >= 8 and avg_redundancy >= 0.85:
        return "LARGE_TIGHT_CLUSTER"
    if size >= 8:
        return "LARGE_CLUSTER"
    if size >= 4 and avg_redundancy >= 0.85:
        return "MEDIUM_TIGHT_CLUSTER"
    if size >= 4:
        return "MEDIUM_CLUSTER"
    if avg_redundancy >= 0.90:
        return "SMALL_TIGHT_CLUSTER"
    return "SMALL_CLUSTER"


def _member_role(is_representative: bool, cluster_size: int,
                 redundancy_to_rep: float) -> str:
    """Determine member role within cluster."""
    if cluster_size == 1:
        return "DISTINCT_SINGLETON"
    if is_representative:
        return "CLUSTER_REPRESENTATIVE"
    if redundancy_to_rep >= 0.90:
        return "REDUNDANT_HIGH_QUALITY_ALTERNATIVE"
    return "LOWER_MARGINAL_INFORMATION_MEMBER"


def _marginal_info_class(score: float, cluster_size: int) -> str:
    """Map marginal information score to class."""
    if cluster_size == 1:
        return "DISTINCT_SINGLETON"
    if score >= 0.70:
        return "HIGH_MARGINAL_INFO"
    if score >= 0.45:
        return "MODERATE_MARGINAL_INFO"
    if score >= 0.25:
        return "LOW_MARGINAL_INFO"
    return "MOSTLY_REDUNDANT"


def _interpret_cluster_zh(cluster_class: str, size: int, families: list[str]) -> str:
    fam_str = ", ".join(families) if families else "未知"
    if size == 1:
        return f"独立因子，无高冗余关联。家族: {fam_str}"
    if "LARGE" in cluster_class:
        return f"大型冗余簇({size}个因子)，该簇存在较高信息重叠，代表因子可作为后续比较基准；其他成员需结合边际信息、稳定性、容量与状态表现进一步评估。家族: {fam_str}"
    if "MEDIUM" in cluster_class:
        return f"中型冗余簇({size}个因子)，存在显著信息重叠。家族: {fam_str}"
    return f"小型冗余簇({size}个因子)。家族: {fam_str}"


def _interpret_cluster_en(cluster_class: str, size: int, families: list[str]) -> str:
    fam_str = ", ".join(families) if families else "unknown"
    if size == 1:
        return f"Standalone factor with no high-redundancy links. Families: {fam_str}"
    if "LARGE" in cluster_class:
        return f"Large redundancy cluster ({size} factors) — high information overlap. Representative factor provides a useful reference point for this cluster. Families: {fam_str}"
    if "MEDIUM" in cluster_class:
        return f"Medium redundancy cluster ({size} factors) — significant information overlap. Families: {fam_str}"
    return f"Small redundancy cluster ({size} factors). Families: {fam_str}"


def _interpret_member_zh(role: str, rep_id: str, red_score: float) -> str:
    if role == "DISTINCT_SINGLETON":
        return "独立因子，提供独特信息"
    if role == "CLUSTER_REPRESENTATIVE":
        return "该簇的质量最高因子，作为簇代表"
    if role == "REDUNDANT_HIGH_QUALITY_ALTERNATIVE":
        return f"与代表因子 {rep_id} 相关性 {red_score:.2f}，信息冗余度高，需结合边际信息、稳定性、容量与状态表现进一步评估"
    return f"与代表因子 {rep_id} 相关性 {red_score:.2f}，信息冗余度中等，需结合边际信息、稳定性、容量与状态表现进一步评估"


def _interpret_member_en(role: str, rep_id: str, red_score: float) -> str:
    if role == "DISTINCT_SINGLETON":
        return "Standalone factor providing unique information"
    if role == "CLUSTER_REPRESENTATIVE":
        return "Highest quality factor in cluster — serves as cluster representative"
    if role == "REDUNDANT_HIGH_QUALITY_ALTERNATIVE":
        return f"Redundancy {red_score:.2f} with representative {rep_id} — high overlap; requires marginal-information review before combination"
    return f"Redundancy {red_score:.2f} with representative {rep_id} — moderate overlap; requires marginal-information review before combination"


def _marginal_reason_zh(cls: str, score: float) -> str:
    reasons = {
        "DISTINCT_SINGLETON": "独立因子，无冗余关联，边际信息最高",
        "HIGH_MARGINAL_INFO": f"边际信息评分 {score:.2f}，即使存在冗余簇也有显著增量价值",
        "MODERATE_MARGINAL_INFO": f"边际信息评分 {score:.2f}，有一定增量价值但与簇内其他因子重叠",
        "LOW_MARGINAL_INFO": f"边际信息评分 {score:.2f}，增量价值有限",
        "MOSTLY_REDUNDANT": f"边际信息评分 {score:.2f}，大部分信息已被更好因子覆盖",
    }
    return reasons.get(cls, f"边际信息评分 {score:.2f}")


def _marginal_reason_en(cls: str, score: float) -> str:
    reasons = {
        "DISTINCT_SINGLETON": "Standalone factor — maximum marginal information",
        "HIGH_MARGINAL_INFO": f"Marginal info score {score:.2f} — significant incremental value despite cluster",
        "MODERATE_MARGINAL_INFO": f"Marginal info score {score:.2f} — some incremental value but overlaps with cluster peers",
        "LOW_MARGINAL_INFO": f"Marginal info score {score:.2f} — limited incremental value",
        "MOSTLY_REDUNDANT": f"Marginal info score {score:.2f} — most information captured by better factors",
    }
    return reasons.get(cls, f"Marginal info score {score:.2f}")


# ── Connected components (union-find) ─────────────────────────────────────

class UnionFind:
    """Simple union-find for cluster detection."""

    def __init__(self, elements: list[str]):
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}

    def find(self, x: str) -> str:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x: str, y: str) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1

    def components(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = defaultdict(list)
        for e in self.parent:
            groups[self.find(e)].append(e)
        return dict(groups)


# ── Main logic ─────────────────────────────────────────────────────────────

def load_inputs(diag_dir: Path, state_path: Path) -> dict:
    """Load all input data frames."""
    state = json.loads(state_path.read_text())
    expected_count = state.get("registered_factors", 71)

    pairwise = pd.read_csv(diag_dir / PAIRWISE_CSV)
    scorecard = pd.read_csv(diag_dir / SCORECARD_CSV)
    redundancy = pd.read_csv(diag_dir / REDUNDANCY_SUMMARY_CSV)
    diag = pd.read_csv(diag_dir / DIAG_SUMMARY_CSV)
    regime = pd.read_csv(diag_dir / REGIME_CSV)
    capacity = pd.read_csv(diag_dir / CAPACITY_CSV)
    quantile = pd.read_csv(diag_dir / QUANTILE_CSV)
    stability = pd.read_csv(diag_dir / STABILITY_CSV)
    decile = pd.read_csv(diag_dir / DECILE_CSV)

    return {
        "state": state,
        "expected_count": expected_count,
        "pairwise": pairwise,
        "scorecard": scorecard,
        "redundancy": redundancy,
        "diag": diag,
        "regime": regime,
        "capacity": capacity,
        "quantile": quantile,
        "stability": stability,
        "decile": decile,
    }


def build_best_horizon_lookup(scorecard: pd.DataFrame) -> dict[str, str]:
    """Map factor_id -> best_horizon from scorecard."""
    return dict(zip(scorecard["factor_id"], scorecard["best_horizon"]))


def get_best_horizon_row(df: pd.DataFrame, factor_id: str, best_horizon: str) -> pd.Series | None:
    """Get the row for a factor at its best horizon, or fall back to first available."""
    subset = df[df["factor_id"] == factor_id]
    if subset.empty:
        return None
    match = subset[subset["horizon"] == best_horizon]
    if not match.empty:
        return match.iloc[0]
    return subset.iloc[0]


def build_redundancy_graph(pairwise: pd.DataFrame, all_factors: list[str],
                           threshold: float) -> tuple[UnionFind, dict, dict]:
    """Build graph and find connected components."""
    uf = UnionFind(all_factors)
    # adjacency: factor -> list of (neighbor, correlation)
    adj: dict[str, list[tuple[str, float]]] = defaultdict(list)

    edges_above_threshold = pairwise[pairwise["abs_spearman_corr"] >= threshold]
    for _, row in edges_above_threshold.iterrows():
        fi, fj = row["factor_i"], row["factor_j"]
        corr = row["abs_spearman_corr"]
        uf.union(fi, fj)
        adj[fi].append((fj, corr))
        adj[fj].append((fi, corr))

    components = uf.components()
    return uf, adj, components


def compute_cluster_summaries(components: dict[str, list[str]],
                              adj: dict, scorecard: pd.DataFrame,
                              family_map: dict[str, str],
                              threshold: float) -> tuple[list[dict], dict[str, dict]]:
    """Compute per-cluster summaries and per-member details."""
    # Build quality score lookup
    quality_map = dict(zip(scorecard["factor_id"], scorecard["final_quality_score"]))
    class_map = dict(zip(scorecard["factor_id"], scorecard["final_quality_class"]))

    cluster_summaries = []
    member_details: dict[str, dict] = {}  # factor_id -> detail dict

    # Sort clusters by representative quality descending
    cluster_list = []
    for root, members in components.items():
        cluster_list.append(members)
    cluster_list.sort(key=lambda m: max(quality_map.get(fid, 0) for fid in m), reverse=True)

    for cid, members in enumerate(cluster_list):
        size = len(members)
        families = _families_in_cluster(members, family_map)

        # Representative = highest quality score
        rep_id = max(members, key=lambda f: quality_map.get(f, 0))

        # Intra-cluster edge statistics
        intra_corrs = []
        n_strong = 0
        member_set = set(members)
        for fi in members:
            for fj, corr in adj.get(fi, []):
                if fj in member_set and fi < fj:  # count each pair once
                    intra_corrs.append(corr)
                    if corr >= STRONG_EDGE_THRESHOLD:
                        n_strong += 1

        avg_intra = sum(intra_corrs) / len(intra_corrs) if intra_corrs else 0.0
        max_intra = max(intra_corrs) if intra_corrs else 0.0

        cluster_class = _cluster_quality_class(size, avg_intra, n_strong)

        # Compute redundancy to representative for each member
        rep_quality = quality_map.get(rep_id, 0)
        for fid in members:
            red_to_rep = 0.0
            if fid != rep_id:
                # Find correlation to representative in adjacency
                for neighbor, corr in adj.get(fid, []):
                    if neighbor == rep_id:
                        red_to_rep = max(red_to_rep, corr)
                # If no direct edge, use 0 (they're still in same component via path)
                # For transitive clusters, we set a floor based on path
                if red_to_rep == 0.0 and size > 1:
                    red_to_rep = 0.5  # default for transitive connection

            # Nearest redundant factor (highest correlation neighbor)
            nearest = None
            nearest_corr = 0.0
            for neighbor, corr in adj.get(fid, []):
                if corr > nearest_corr:
                    nearest_corr = corr
                    nearest = neighbor

            novelty_score = 1.0 - nearest_corr if nearest_corr > 0 else 1.0

            role = _member_role(fid == rep_id, size, red_to_rep)

            member_details[fid] = {
                "factor_id": fid,
                "cluster_id": cid,
                "cluster_size": size,
                "family": family_map.get(fid, ""),
                "quality_score": quality_map.get(fid, 0),
                "scorecard_class": class_map.get(fid, ""),
                "redundancy_score_to_representative": round(red_to_rep, 6),
                "nearest_redundant_factor": nearest or "",
                "novelty_score": round(novelty_score, 6),
                "member_role": role,
                "interpretation_notes_zh": _interpret_member_zh(role, rep_id, red_to_rep),
                "interpretation_notes_en": _interpret_member_en(role, rep_id, red_to_rep),
                "_rep_id": rep_id,
            }

        cluster_summaries.append({
            "cluster_id": cid,
            "cluster_size": size,
            "representative_factor_id": rep_id,
            "representative_quality_score": round(rep_quality, 2),
            "avg_intra_redundancy": round(avg_intra, 6),
            "max_intra_redundancy": round(max_intra, 6),
            "n_strong_edges": n_strong,
            "family_count": len(families),
            "families": "; ".join(families),
            "cluster_quality_class": cluster_class,
            "interpretation_notes_zh": _interpret_cluster_zh(cluster_class, size, families),
            "interpretation_notes_en": _interpret_cluster_en(cluster_class, size, families),
        })

    return cluster_summaries, member_details


def enrich_members(member_details: dict[str, dict],
                   inputs: dict, scorecard: pd.DataFrame) -> list[dict]:
    """Add per-factor diagnostic fields from other input tables."""
    best_hz = build_best_horizon_lookup(scorecard)
    capacity_map = {r["factor_id"]: r for _, r in inputs["capacity"].iterrows()}
    regime_map = {r["factor_id"]: r for _, r in inputs["regime"].iterrows()}
    diag_map = {r["factor_id"]: r for _, r in inputs["diag"].iterrows()}

    rows = []
    for fid, md in member_details.items():
        hz = best_hz.get(fid, "72h")

        # Diagnostics summary
        drow = diag_map.get(fid)
        paper_return = drow["long_short_annualized_return"] if drow is not None else None

        # Capacity / liquidity
        crow = capacity_map.get(fid)
        cost_class = crow["cost_sensitivity_class"] if crow is not None else ""
        cap_class = crow["capacity_liquidity_class"] if crow is not None else ""

        # Regime
        rrow = regime_map.get(fid)
        regime_class = rrow["regime_dependency_class"] if rrow is not None else ""

        # Quantile shape at best horizon
        qrow = get_best_horizon_row(inputs["quantile"], fid, hz)
        qshape = qrow["quantile_shape_class"] if qrow is not None else ""

        # Stability at best horizon
        srow = get_best_horizon_row(inputs["stability"], fid, hz)
        stab_class = srow["stability_class"] if srow is not None else ""

        # Decile shape at best horizon
        dsrow = get_best_horizon_row(inputs["decile"], fid, hz)
        dshape = dsrow["decile_shape_class"] if dsrow is not None else ""

        md.update({
            "paper_net_return_10bps": round(float(_safe(paper_return, 0)), 6) if paper_return is not None else None,
            "cost_sensitivity_class": str(_safe(cost_class, "")),
            "regime_dependency_class": str(_safe(regime_class, "")),
            "capacity_liquidity_class": str(_safe(cap_class, "")),
            "quantile_shape_class": str(_safe(qshape, "")),
            "stability_class": str(_safe(stab_class, "")),
            "decile_shape_class": str(_safe(dshape, "")),
        })
        # Remove internal key
        md.pop("_rep_id", None)
        rows.append(md)

    return rows


def compute_marginal_information(member_rows: list[dict],
                                 inputs: dict) -> list[dict]:
    """Compute marginal information score for each factor.

    Score components (each 0-1):
      - redundancy_penalty: 1 - max_correlation_to_any_factor (higher = more novel)
      - quality_component: quality_score / 100
      - paper_component: clipped |paper_return| / 0.10 (cap at 1)
      - stability_component: stability score / 100
      - regime_component: 1 if ROBUST, 0.5 if moderate, 0 if dependent
      - capacity_component: 1 if FRIENDLY, 0.5 if moderate, 0 if fragile

    Marginal info = weighted sum, then penalized by cluster redundancy.
    """
    # Build lookup for redundancy summary
    red_map = {r["factor_id"]: r for _, r in inputs["redundancy"].iterrows()}
    cap_map = {r["factor_id"]: r for _, r in inputs["capacity"].iterrows()}

    results = []
    for md in member_rows:
        fid = md["factor_id"]
        cluster_size = md["cluster_size"]
        quality = md["quality_score"] / 100.0  # already 0-100 range

        # Redundancy penalty from redundancy summary
        rrow = red_map.get(fid)
        if rrow is not None:
            nearest_corr = rrow.get("nearest_abs_spearman_corr", 0)
            if pd.isna(nearest_corr):
                nearest_corr = 0
            redundancy_novelty = 1.0 - float(nearest_corr)
        else:
            redundancy_novelty = 1.0

        # Paper component
        pr = abs(md.get("paper_net_return_10bps") or 0)
        paper_comp = min(pr / 0.10, 1.0)

        # Stability component from member's stability_class
        stab_class = md.get("stability_class", "")
        if "STABLE_POSITIVE" in stab_class or "STABLE_WEAK" in stab_class:
            stab_comp = 0.8
        elif "STABLE" in stab_class:
            stab_comp = 0.6
        elif "UNSTABLE" in stab_class:
            stab_comp = 0.3
        else:
            stab_comp = 0.5

        # Regime component
        regime_class = md.get("regime_dependency_class", "")
        if "ROBUST" in regime_class:
            regime_comp = 1.0
        elif "DEPENDENT" in regime_class:
            regime_comp = 0.3
        else:
            regime_comp = 0.5

        # Capacity component
        cap_cls = md.get("capacity_liquidity_class", "")
        if "FRIENDLY" in cap_cls:
            cap_comp = 1.0
        elif "FRAGILE" in cap_cls or "WATCH" in cap_cls:
            cap_comp = 0.4
        else:
            cap_comp = 0.5

        # Nearest better factor (higher quality in same cluster or globally)
        # For simplicity: if in cluster >1, find nearest factor with higher quality
        nearest_better = ""
        if cluster_size > 1:
            rep_id = ""
            for r in member_rows:
                if r["cluster_id"] == md["cluster_id"] and r["member_role"] == "CLUSTER_REPRESENTATIVE":
                    rep_id = r["factor_id"]
                    break
            nearest_better = rep_id if rep_id != fid else ""

        # Weighted combination
        redundancy_penalty = redundancy_novelty * (1.0 if cluster_size == 1 else 0.85)
        raw_score = (
            redundancy_penalty * 0.30
            + quality * 0.25
            + paper_comp * 0.15
            + stab_comp * 0.10
            + regime_comp * 0.10
            + cap_comp * 0.10
        )
        # Singletons get bonus
        if cluster_size == 1:
            raw_score = min(raw_score * 1.15, 1.0)

        mi_score = round(min(max(raw_score, 0), 1.0), 4)
        mi_class = _marginal_info_class(mi_score, cluster_size)

        results.append({
            "factor_id": fid,
            "cluster_id": md["cluster_id"],
            "cluster_size": cluster_size,
            "marginal_information_score": mi_score,
            "marginal_information_class": mi_class,
            "redundancy_penalty": round(redundancy_penalty, 4),
            "quality_component": round(quality, 4),
            "paper_component": round(paper_comp, 4),
            "stability_component": round(stab_comp, 4),
            "regime_component": round(regime_comp, 4),
            "capacity_component": round(cap_comp, 4),
            "nearest_better_factor": nearest_better,
            "reason_notes_zh": _marginal_reason_zh(mi_class, mi_score),
            "reason_notes_en": _marginal_reason_en(mi_class, mi_score),
        })

    return results


def write_outputs(diag_dir: Path, cluster_summaries: list[dict],
                  member_rows: list[dict], marginal_rows: list[dict],
                  payload: dict, expected_count: int) -> None:
    """Write all 6 output files."""
    # 1. Cluster summary
    pd.DataFrame(cluster_summaries).to_csv(
        diag_dir / "factor_redundancy_cluster_summary.csv", index=False)

    # 2. Cluster members (full detail)
    pd.DataFrame(member_rows).to_csv(
        diag_dir / "factor_redundancy_cluster_members.csv", index=False)

    # 3. Representatives only
    reps = [m for m in member_rows if m["member_role"] == "CLUSTER_REPRESENTATIVE"]
    pd.DataFrame(reps).to_csv(
        diag_dir / "factor_redundancy_cluster_representatives.csv", index=False)

    # 4. Marginal information
    pd.DataFrame(marginal_rows).to_csv(
        diag_dir / "factor_marginal_information_summary.csv", index=False)

    # 5. Payload JSON
    payload_path = diag_dir / "factor_redundancy_cluster_payload.json"
    payload_path.write_text(json.dumps(payload, indent=2, default=str))

    # 6. Manifest JSON
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": "build_factor_redundancy_cluster_diagnostics.py",
        "version": "PM-31",
        "expected_factor_count": expected_count,
        "actual_factor_count": len(member_rows),
        "coverage": len(member_rows) / expected_count if expected_count > 0 else 0,
        "n_clusters": len(cluster_summaries),
        "n_singletons": sum(1 for c in cluster_summaries if c["cluster_size"] == 1),
        "n_multi_factor_clusters": sum(1 for c in cluster_summaries if c["cluster_size"] > 1),
        "largest_cluster_size": max((c["cluster_size"] for c in cluster_summaries), default=0),
        "redundancy_field": "abs_spearman_corr",
        "redundancy_threshold": payload.get("redundancy_threshold", DEFAULT_STRONG_THRESHOLD),
        "outputs": [
            "factor_redundancy_cluster_summary.csv",
            "factor_redundancy_cluster_members.csv",
            "factor_redundancy_cluster_representatives.csv",
            "factor_marginal_information_summary.csv",
            "factor_redundancy_cluster_payload.json",
            "factor_redundancy_cluster_manifest.json",
        ],
        "disclaimer": "Factor library redundancy cluster diagnostics. NOT production. NOT live trading.",
    }
    (diag_dir / "factor_redundancy_cluster_manifest.json").write_text(
        json.dumps(manifest, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--threshold", type=float, default=DEFAULT_STRONG_THRESHOLD,
                        help=f"abs_spearman_corr threshold for graph edges (default: {DEFAULT_STRONG_THRESHOLD})")
    parser.add_argument("--diag-dir", type=str, default=str(DIAG_DIR))
    parser.add_argument("--state-path", type=str, default=str(STATE_PATH))
    args = parser.parse_args()

    diag_dir = Path(args.diag_dir)
    state_path = Path(args.state_path)

    print(f"[PM-31] Loading inputs from {diag_dir} ...")
    inputs = load_inputs(diag_dir, state_path)
    expected = inputs["expected_count"]
    print(f"[PM-31] Expected factors: {expected}")

    # Get all factor ids from state
    all_factors = inputs["state"].get("registered_factor_ids", [])
    if not all_factors:
        all_factors = list(inputs["scorecard"]["factor_id"].unique())
    print(f"[PM-31] Loaded {len(all_factors)} factor ids")

    # Build family map
    family_map = dict(zip(inputs["scorecard"]["factor_id"], inputs["scorecard"]["family"]))

    # Build graph
    print(f"[PM-31] Building redundancy graph (threshold={args.threshold}) ...")
    uf, adj, components = build_redundancy_graph(
        inputs["pairwise"], all_factors, args.threshold)
    print(f"[PM-31] Found {len(components)} connected components")

    # Cluster summaries + member details
    cluster_summaries, member_details = compute_cluster_summaries(
        components, adj, inputs["scorecard"], family_map, args.threshold)

    # Enrich members with diagnostic fields
    member_rows = enrich_members(member_details, inputs, inputs["scorecard"])

    # Marginal information
    marginal_rows = compute_marginal_information(member_rows, inputs)

    # Build payload
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "redundancy_threshold": args.threshold,
        "strong_edge_threshold": STRONG_EDGE_THRESHOLD,
        "expected_factor_count": expected,
        "actual_factor_count": len(member_rows),
        "coverage": len(member_rows) / expected if expected > 0 else 0,
        "n_clusters": len(cluster_summaries),
        "cluster_summaries": cluster_summaries,
        "member_count": len(member_rows),
        "marginal_class_distribution": pd.Series(
            [m["marginal_information_class"] for m in marginal_rows]
        ).value_counts().to_dict(),
        "disclaimer": "Factor library redundancy cluster diagnostics. NOT production. NOT live trading.",
    }

    # Write outputs
    write_outputs(diag_dir, cluster_summaries, member_rows, marginal_rows,
                  payload, expected)

    # Print summary
    print(f"\n[PM-31] ═══ Summary ═══")
    print(f"  Coverage: {len(member_rows)}/{expected}")
    print(f"  Clusters: {len(cluster_summaries)}")
    print(f"  Singletons: {sum(1 for c in cluster_summaries if c['cluster_size'] == 1)}")
    print(f"  Multi-factor clusters: {sum(1 for c in cluster_summaries if c['cluster_size'] > 1)}")
    largest = max(cluster_summaries, key=lambda c: c["cluster_size"])
    print(f"  Largest cluster: {largest['cluster_size']} factors (rep: {largest['representative_factor_id']})")
    print(f"\n  Marginal information class distribution:")
    for cls, count in sorted(payload["marginal_class_distribution"].items()):
        print(f"    {cls}: {count}")
    print(f"\n  Outputs written to: {diag_dir}")
    print("[PM-31] Done.")


if __name__ == "__main__":
    main()
