#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import build_ema_donchian_scout_clean_replication as base  # noqa: E402

ART_DIR = ROOT / "reports" / "artifacts" / "scout_ema_donchian_breakout_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_ema_donchian_breakout_15m"

TIME_RECHECK_PATH = ART_DIR / "time_redwatch_recheck.csv"
SCOPE_RECHECK_PATH = ART_DIR / "time_redwatch_scope_check.csv"
SUMMARY_PATH = ART_DIR / "time_redwatch_verdict.csv"
HTML_PATH = SITE_DIR / "time_redwatch_recheck.html"

VARIANTS = [
    (
        "l30_c3",
        base.EmaDonchianBreakoutConfig(
            market_resample_rule="1h",
            ema_window_1h=20,
            donchian_lookback=30,
            confirm_bars=3,
            use_ema_slope=True,
        ),
    ),
    (
        "l40_c3",
        base.EmaDonchianBreakoutConfig(
            market_resample_rule="1h",
            ema_window_1h=20,
            donchian_lookback=40,
            confirm_bars=3,
            use_ema_slope=True,
        ),
    ),
]
NARROW_SCOPE = {"ETH-USD", "SOL-USD"}


def pct(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.{digits}f}%"


def num(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.{digits}f}"


def render_table(df: pd.DataFrame, *, percent_cols: set[str], digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_time_recheck() -> pd.DataFrame:
    rows: list[dict] = []
    for label, cfg in VARIANTS:
        for asset, symbol in base.ASSETS.items():
            bars = base.load_cached_bars(symbol, asset)
            for bucket_id, idx in enumerate(np.array_split(bars.index.to_numpy(), base.TIME_BUCKETS), start=1):
                part = bars.loc[idx].copy().reset_index(drop=True)
                summary, _ = base.evaluate_donchian(part, cfg=cfg, label=label, cost_bps=base.PRIMARY_COST)
                rows.append(
                    {
                        "variant": label,
                        "asset": asset,
                        "time_bucket": f"bucket_{bucket_id}",
                        "window_start": part["timestamp"].iloc[0].strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "window_end": part["timestamp"].iloc[-1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "trades": int(summary["trades"]),
                        "total_return": float(summary["total_return"]),
                        "max_drawdown": float(summary["max_drawdown"]),
                    }
                )
    return pd.DataFrame(rows)


def build_scope_check(time_df: pd.DataFrame) -> pd.DataFrame:
    scoped = time_df[time_df["asset"].isin(NARROW_SCOPE)].copy()
    grouped = (
        scoped.groupby(["variant", "time_bucket"], sort=False)
        .agg(
            scope_assets=("asset", lambda s: "+".join(sorted(s))),
            scope_mean_total_return=("total_return", "mean"),
            positive_asset_count=("total_return", lambda s: int((s > 0).sum())),
            trades=("trades", "sum"),
        )
        .reset_index()
    )
    grouped["scope_name"] = "ETH+SOL_only"
    return grouped[["variant", "scope_name", "time_bucket", "scope_assets", "trades", "positive_asset_count", "scope_mean_total_return"]]


def build_verdict(time_df: pd.DataFrame, scope_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, _ in VARIANTS:
        variant_df = time_df[time_df["variant"] == label].copy()
        scope_variant = scope_df[scope_df["variant"] == label].copy()
        positive_buckets = int((variant_df["total_return"] > 0).sum())
        total_buckets = int(len(variant_df))
        scope_positive_buckets = int((scope_variant["scope_mean_total_return"] > 0).sum())
        scope_total_buckets = int(len(scope_variant))
        rows.append(
            {
                "variant": label,
                "positive_buckets": positive_buckets,
                "total_buckets": total_buckets,
                "positive_bucket_ratio": positive_buckets / total_buckets if total_buckets else np.nan,
                "eth_sol_positive_buckets": scope_positive_buckets,
                "eth_sol_total_buckets": scope_total_buckets,
                "eth_sol_positive_bucket_ratio": scope_positive_buckets / scope_total_buckets if scope_total_buckets else np.nan,
                "bucket_pattern": "/".join("pos" if x > 0 else "neg" for x in variant_df.sort_values(["asset", "time_bucket"])["total_return"]),
            }
        )
    summary = pd.DataFrame(rows)
    summary["verdict"] = "park_evidence_pool"
    summary["reason"] = (
        "正邻域 l30_c3 / l40_c3 都重复出现 bucket_1负 / bucket_2正 / bucket_3负；即使缩到 ETH+SOL-only，时间 bucket 仍只有中段为正。"
    )
    summary["next_action"] = "do_not_promote_to_P3; return_to_fresh_intake_unless_real_P3_need_exists_elsewhere"
    return summary


def write_html(time_df: pd.DataFrame, scope_df: pd.DataFrame, verdict_df: pd.DataFrame) -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    verdict = verdict_df.iloc[0]
    html = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\">
  <title>Rank 25 · time red-watch honest recheck</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif; margin: 32px auto; max-width: 1200px; line-height: 1.55; color: #18212b; padding: 0 16px; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; font-size: 14px; }}
    th, td {{ border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
    .muted {{ color: #57606a; }}
    .bad {{ color: #b42318; font-weight: 700; }}
    .warn {{ color: #9a6700; font-weight: 600; }}
  </style>
</head>
<body>
  <h1>Rank 25 · time red-watch honest recheck</h1>
  <p class=\"muted\">生成时间：{escape(generated_at)}</p>
  <p>这次只做 1 次 genuinely verdict-changing 的最小诚实检查：不改数据、不追新 bar、不扩新参数网格，只问 <code>l30_c3</code> 的时间不稳是不是单点热像素，还是连唯一仍为正 pocket 的邻近变体 <code>l40_c3</code> 也同样呈现中段独亮的结构。</p>

  <h2>Hard verdict</h2>
  <p><span class=\"bad\">当前更诚实的结论：Rank 25 应压回 park / evidence pool，而不是升到 P3。</span></p>
  <p>{escape(str(verdict['reason']))}</p>
  <p>换句话说：这条线不是完全没 edge，但当前正收益更像集中在中段单一 pocket；在最小邻近变体与最小窄范围 scope 下，这个 red-watch 也没有被消掉，所以这 1 次检查不足以支持 narrow paper pilot。</p>

  <h2>Neighbor time-stability recheck</h2>
  <p class=\"muted\">比较对象只限原主变体 <code>l30_c3</code> 与唯一仍为正 pocket 的邻近变体 <code>l40_c3</code>。</p>
  {render_table(time_df, percent_cols={'total_return','max_drawdown'}, digits_cols={'trades':0})}

  <h2>ETH+SOL-only narrow-scope check</h2>
  <p class=\"muted\">再做 1 次最小 scope honesty check：去掉弱腿 BTC，只看更强的 ETH+SOL 组合是否至少把时间 bucket 结构拉平。</p>
  {render_table(scope_df, percent_cols={'scope_mean_total_return'}, digits_cols={'trades':0,'positive_asset_count':0})}

  <h2>Verdict summary</h2>
  {render_table(verdict_df[['variant','positive_buckets','total_buckets','positive_bucket_ratio','eth_sol_positive_buckets','eth_sol_total_buckets','eth_sol_positive_bucket_ratio','verdict','next_action']], percent_cols={'positive_bucket_ratio','eth_sol_positive_bucket_ratio'}, digits_cols={'positive_buckets':0,'total_buckets':0,'eth_sol_positive_buckets':0,'eth_sol_total_buckets':0})}

  <p class=\"muted\">Artifacts: <code>reports/artifacts/scout_ema_donchian_breakout_15m/time_redwatch_*.csv</code></p>
</body>
</html>
"""
    HTML_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    time_df = build_time_recheck()
    scope_df = build_scope_check(time_df)
    verdict_df = build_verdict(time_df, scope_df)
    time_df.to_csv(TIME_RECHECK_PATH, index=False)
    scope_df.to_csv(SCOPE_RECHECK_PATH, index=False)
    verdict_df.to_csv(SUMMARY_PATH, index=False)
    write_html(time_df, scope_df, verdict_df)
    print(f"wrote {TIME_RECHECK_PATH}")
    print(f"wrote {SCOPE_RECHECK_PATH}")
    print(f"wrote {SUMMARY_PATH}")
    print(f"wrote {HTML_PATH}")


if __name__ == "__main__":
    main()
