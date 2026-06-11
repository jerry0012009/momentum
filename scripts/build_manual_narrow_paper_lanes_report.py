#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "manual_narrow_paper_lanes"
OUT_PATH = SITE_DIR / "report.html"

STATUS_PATH = ART_DIR / "manual_narrow_paper_status.csv"
OPEN_POSITIONS_PATH = ART_DIR / "manual_narrow_paper_open_positions.csv"
LEDGER_PATH = ART_DIR / "manual_narrow_paper_closed_trades.csv"
RUN_SUMMARY_PATH = ART_DIR / "manual_narrow_paper_last_run_summary.json"
STATE_PATH = ART_DIR / "manual_narrow_paper_state.json"
RECONCILIATION_PATH = ART_DIR / "manual_narrow_paper_desk_reconciliation.csv"
BOT3_TRIGGER_PATH = ART_DIR / "manual_narrow_paper_bot3_reentry_queue.csv"
CRON_FRESHNESS_AUDIT_PATH = ART_DIR / "manual_narrow_paper_cron_freshness_audit.csv"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def pct(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.2f}%"


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def fmt_ts(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "-"
    text = str(v).strip()
    return text or "-"


def render_table(df: pd.DataFrame, *, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            v = row[col]
            if col in percent_cols:
                text = pct(v)
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(col, 2))
            else:
                text = fmt_ts(v)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_reconciliation(status_df: pd.DataFrame, open_df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        'candidate_rank', 'candidate_id', 'scope_tag', 'tracked_assets', 'open_positions',
        'latest_sample_end_utc', 'bot3_append_review_need', 'default_owner', 'desk_read', 'next_operator_action'
    ]
    if status_df.empty:
        return pd.DataFrame(columns=columns)

    rows: list[dict[str, object]] = []
    grouped = status_df.groupby(['candidate_rank', 'candidate_id', 'scope_tag'], dropna=False)
    for (candidate_rank, candidate_id, scope_tag), group in grouped:
        open_count = int((group['open_position'].fillna('') == 'open').sum()) if 'open_position' in group.columns else 0
        tracked_assets = '/'.join(group['asset'].astype(str).tolist()) if 'asset' in group.columns else '-'
        latest_sample_end = '-'
        if 'sample_end_utc' in group.columns and not group['sample_end_utc'].dropna().empty:
            latest_sample_end = str(group['sample_end_utc'].dropna().iloc[0])

        if candidate_id == 'rank17_pullback_ethsol_narrow_pilot':
            desk_read = 'Rank 17 仍属 P3 narrow paper；当前 open 头寸只是 paper continuity，不自动构成 bot3 append/review need。'
        elif candidate_id == 'rank29_trendline_breakout_navigator':
            desk_read = 'Rank 29 已降为 P0 archived：strict-causal 复盘确认主样本存在未来函数污染，旧 P3 narrow paper 结论全部撤销。'
        elif candidate_id == 'rank29_trendline_breakout_gate_shadow':
            desk_read = 'Rank 29 gate shadow 同步降为 P0 archived：仅保留作历史审计材料，不再视为有效 pilot 或 baseline 辅助线。'
        elif candidate_id == 'rank2_combo_all':
            desk_read = 'Rank 2 仍属 P3 narrow paper；当前没有 append-ready refresh/review row。'
        elif candidate_id == 'rank32b_slope_floor_continuation':
            desk_read = 'Rank 32b 现属 P3 narrow paper；日常 continuity 已并入专属 narrow-paper refresh 链，不再默认占用 bot3 主资源。'
        else:
            desk_read = '当前 lane 继续由 narrow-paper 专属刷新链维护。'

        next_operator_action = (
            '继续由 manual narrow-paper cron / 人工 refresh 续写；仅当出现新的 closed trade append 或 review row 时再回到 bot3 默认主资源。'
        )
        if candidate_id in {'rank29_trendline_breakout_navigator', 'rank29_trendline_breakout_gate_shadow'}:
            next_operator_action = '维持 archived / no-reentry：不再追加 P3 refresh，不再回到 bot3 主资源；仅在重写信号定义后另立新候选。'
        rows.append({
            'candidate_rank': int(candidate_rank),
            'candidate_id': candidate_id,
            'scope_tag': scope_tag,
            'tracked_assets': tracked_assets,
            'open_positions': open_count,
            'latest_sample_end_utc': latest_sample_end,
            'bot3_append_review_need': 'no_default',
            'default_owner': 'manual_narrow_paper_runner',
            'desk_read': desk_read,
            'next_operator_action': next_operator_action,
        })

    recon_df = pd.DataFrame(rows, columns=columns).sort_values(['candidate_rank', 'candidate_id'])
    RECONCILIATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    recon_df.to_csv(RECONCILIATION_PATH, index=False)
    return recon_df


def build_bot3_reentry_queue(status_df: pd.DataFrame, open_df: pd.DataFrame, run_summary: dict[str, object]) -> pd.DataFrame:
    columns = [
        'candidate_rank', 'candidate_id', 'current_owner', 'bot3_reentry_now', 'trigger_type',
        'trigger_condition', 'current_state', 'latest_sample_end_utc', 'evidence_note'
    ]
    if status_df.empty:
        return pd.DataFrame(columns=columns)

    new_closed = int(run_summary.get('new_closed_trades_appended', 0) or 0)
    rows: list[dict[str, object]] = []
    grouped = status_df.groupby(['candidate_rank', 'candidate_id'], dropna=False)
    for (candidate_rank, candidate_id), group in grouped:
        latest_sample_end = '-'
        if 'sample_end_utc' in group.columns and not group['sample_end_utc'].dropna().empty:
            latest_sample_end = str(group['sample_end_utc'].dropna().iloc[0])
        open_count = int((group['open_position'].fillna('') == 'open').sum()) if 'open_position' in group.columns else 0

        if candidate_id == 'rank17_pullback_ethsol_narrow_pilot':
            trigger_type = 'closed_trade_append_or_weekly_review_row'
            current_state = 'open_positions_waiting_manual_refresh'
            evidence_note = f'当前仍有 {open_count} 个 open paper positions，但它们只属于 continuity；只有后续 refresh 真正追加 closed trade 或 weekly-review row 才需要 bot3 回补。'
        elif candidate_id == 'rank29_trendline_breakout_navigator':
            trigger_type = 'no_reentry_archived'
            current_state = 'p0_archived_due_future_leak'
            evidence_note = 'strict-causal 复盘后确认旧口径受未来函数污染；Rank 29 baseline 已撤销，不再等待 append/review。'
        elif candidate_id == 'rank29_trendline_breakout_gate_shadow':
            trigger_type = 'no_reentry_archived'
            current_state = 'p0_archived_due_future_leak'
            evidence_note = 'gate shadow 仅保留作历史审计对照；Rank 29 全线不再进入 bot3 回补队列。'
        elif candidate_id == 'rank2_combo_all':
            trigger_type = 'new_closed_trade_append_or_new_review_row'
            current_state = 'narrow_paper_seeded_waiting_real_append'
            evidence_note = 'ledger / refresh / review seed 已具备；当前没有新的 append-ready 行。'
        elif candidate_id == 'rank32b_slope_floor_continuation':
            trigger_type = 'new_closed_trade_append_or_new_review_row'
            current_state = 'full_scope_p3_under_dedicated_refresh'
            evidence_note = 'full-scope P3 已接入专属 narrow-paper refresh 链；只有后续 refresh 真正追加 closed trade 或 review row 时才需要 bot3 回补。'
        else:
            trigger_type = 'new_closed_trade_append_or_new_review_row'
            current_state = 'waiting_manual_refresh'
            evidence_note = '当前 lane 继续由专属 narrow-paper refresh 链维护。'

        rows.append({
            'candidate_rank': int(candidate_rank),
            'candidate_id': candidate_id,
            'current_owner': 'manual_narrow_paper_runner',
            'bot3_reentry_now': 'yes' if new_closed > 0 else 'no',
            'trigger_type': trigger_type,
            'trigger_condition': 'manual narrow-paper refresh 新增 closed trade append 或 weekly-review row',
            'current_state': current_state,
            'latest_sample_end_utc': latest_sample_end,
            'evidence_note': evidence_note,
        })

    trigger_df = pd.DataFrame(rows, columns=columns).sort_values(['candidate_rank', 'candidate_id'])
    BOT3_TRIGGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    trigger_df.to_csv(BOT3_TRIGGER_PATH, index=False)
    return trigger_df


def _path_mtime_utc(path: Path) -> datetime | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _ts_or_none(value: object) -> datetime | None:
    ts = pd.to_datetime(value, utc=True, errors='coerce')
    if pd.isna(ts):
        return None
    return ts.to_pydatetime()


def _iso_or_dash(ts: datetime | None) -> str:
    if ts is None:
        return '-'
    return ts.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def build_cron_freshness_audit(run_summary: dict[str, object]) -> pd.DataFrame:
    now = datetime.now(timezone.utc)
    expected_max_age_min = 25

    inferred_refresh_ts = _ts_or_none(run_summary.get('run_at_utc')) or _path_mtime_utc(RUN_SUMMARY_PATH)
    rows: list[dict[str, object]] = []

    subjects = [
        (
            'manual runner last summary',
            inferred_refresh_ts,
            'refresh runner summary 若明显落后，就说明 narrow-paper 续跑已经停住。',
            '查看 reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json',
            f'path={RUN_SUMMARY_PATH.relative_to(ROOT)}',
        ),
        (
            'manual narrow-paper status csv',
            _path_mtime_utc(STATUS_PATH),
            'status csv 若不更新，页面看到的 sample_end / watermark / open_position 都会一起陈旧。',
            '查看 status csv 是否随 refresh 同步更新',
            f'path={STATUS_PATH.relative_to(ROOT)}',
        ),
        (
            'bot3 re-entry queue csv',
            _path_mtime_utc(BOT3_TRIGGER_PATH),
            're-entry queue 若不更新，会误导 desk 对 bot3 是否该回补的判断。',
            '查看 bot3 queue 是否随 refresh 同步更新',
            f'path={BOT3_TRIGGER_PATH.relative_to(ROOT)}',
        ),
        (
            'manual narrow-paper report html',
            _path_mtime_utc(OUT_PATH),
            'report html 若落后于 artifacts，说明 build/publish 链没有跟上 refresh。',
            '查看 build/publish 链是否断在 report 阶段',
            f'path={OUT_PATH.relative_to(ROOT)}',
        ),
        (
            'narrow-paper refresh cadence (inferred)',
            inferred_refresh_ts,
            '这里只根据 artifact 时间反推 refresh cadence；若超过 20~25m 仍没动，优先怀疑 scheduler / runner / publish 链断了。',
            '若持续超窗，检查 scheduler / runner / publish 链',
            'source=inferred_from_artifacts',
        ),
    ]

    for subject, last_update_ts, why_it_matters, next_action, evidence_note in subjects:
        if last_update_ts is None:
            rows.append({
                'subject': subject,
                'observed_at_utc': _iso_or_dash(now),
                'last_update_utc': '-',
                'expected_max_age_min': expected_max_age_min,
                'observed_age_min': pd.NA,
                'current_state': 'missing',
                'hard_verdict': 'investigate_refresh_chain',
                'why_it_matters': why_it_matters,
                'next_action': next_action,
                'evidence_note': evidence_note,
            })
            continue

        observed_age_min = max((now - last_update_ts).total_seconds() / 60.0, 0.0)
        if observed_age_min <= expected_max_age_min:
            current_state = 'fresh_within_window'
            hard_verdict = 'keep cron-managed continuity'
        else:
            current_state = 'stale_beyond_window'
            hard_verdict = 'investigate refresh chain'

        rows.append({
            'subject': subject,
            'observed_at_utc': _iso_or_dash(now),
            'last_update_utc': _iso_or_dash(last_update_ts),
            'expected_max_age_min': expected_max_age_min,
            'observed_age_min': observed_age_min,
            'current_state': current_state,
            'hard_verdict': hard_verdict,
            'why_it_matters': why_it_matters,
            'next_action': next_action,
            'evidence_note': evidence_note,
        })

    cron_freshness_df = pd.DataFrame(rows)
    CRON_FRESHNESS_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cron_freshness_df.to_csv(CRON_FRESHNESS_AUDIT_PATH, index=False)
    return cron_freshness_df


def main() -> int:
    ensure_dir(SITE_DIR)
    status_df = read_csv(STATUS_PATH)
    open_df = read_csv(OPEN_POSITIONS_PATH)
    ledger_df = read_csv(LEDGER_PATH)
    run_summary = json.loads(RUN_SUMMARY_PATH.read_text()) if RUN_SUMMARY_PATH.exists() else {}
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    reconciliation_df = build_reconciliation(status_df, open_df)
    bot3_trigger_df = build_bot3_reentry_queue(status_df, open_df, run_summary)
    cron_freshness_df = build_cron_freshness_audit(run_summary)

    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    total_lanes = int(len(status_df)) if not status_df.empty else 0
    open_positions = int((status_df.get('open_position') == 'open').sum()) if not status_df.empty and 'open_position' in status_df.columns else 0
    new_closed = int(run_summary.get('new_closed_trades_appended', 0) or 0)
    last_run = run_summary.get('run_at_utc', '-')
    initialized_at = state.get('initialized_at_utc', '-')

    summary_cards = f"""
    <div class=\"grid\">
      <div class=\"card\"><div class=\"k\">Tracked lanes</div><div class=\"v\">{total_lanes}</div><div class=\"s\">Rank 2 / 17 / 32b active；Rank 29 baseline+shadow 已归档为 P0</div></div>
      <div class=\"card\"><div class=\"k\">Open positions</div><div class=\"v\">{open_positions}</div><div class=\"s\">最新样本尾部仍未正式闭合</div></div>
      <div class=\"card\"><div class=\"k\">New closed trades</div><div class=\"v\">{new_closed}</div><div class=\"s\">最近一次 refresh 新增</div></div>
      <div class=\"card\"><div class=\"k\">Last run</div><div class=\"v\">{escape(str(last_run))}</div><div class=\"s\">初始化于 {escape(str(initialized_at))}</div></div>
    </div>
    """

    lane_view = status_df.copy()
    if not lane_view.empty:
        lane_view = lane_view[[
            'candidate_rank','candidate_id','asset','stage','scope_tag','sample_end_utc',
            'latest_closed_exit_ts_utc','lifetime_total_return_6bps','new_trades_appended',
            'open_position','open_entry_ts_utc','open_side','watermark_exit_ts_utc'
        ]]

    rank29_shadow_view = status_df.copy()
    if not rank29_shadow_view.empty:
        rank29_shadow_view = rank29_shadow_view[
            rank29_shadow_view['candidate_id'].isin(['rank29_trendline_breakout_navigator', 'rank29_trendline_breakout_gate_shadow'])
        ].copy()
        keep = [
            c for c in [
                'candidate_id', 'asset', 'stage', 'lifetime_total_return_6bps', 'new_trades_appended',
                'open_position', 'watermark_exit_ts_utc', 'gate_hit_trades', 'mean_exposure_weight', 'shadow_bad_regime_weight'
            ] if c in rank29_shadow_view.columns
        ]
        rank29_shadow_view = rank29_shadow_view[keep]

    recent_ledger = ledger_df.copy()
    if not recent_ledger.empty and 'exit_ts' in recent_ledger.columns:
        recent_ledger = recent_ledger.sort_values('exit_ts', ascending=False).head(30)
        keep = [c for c in ['candidate_rank','candidate_id','asset','entry_ts','exit_ts','direction','side','net_ret','hold_bars','exit_reason'] if c in recent_ledger.columns]
        recent_ledger = recent_ledger[keep]

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Manual Narrow Paper Lanes</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 20px 56px; }}
    h1,h2 {{ margin: 0 0 12px; }}
    p {{ line-height: 1.6; }}
    .muted {{ color: #94a3b8; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 18px 0 28px; }}
    .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 16px; }}
    .k {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }}
    .v {{ font-size: 24px; font-weight: 700; margin-top: 8px; word-break: break-word; }}
    .s {{ margin-top: 8px; color: #9ca3af; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; margin: 12px 0 28px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }}
    th {{ background: #0f172a; color: #cbd5e1; position: sticky; top: 0; }}
    tr:last-child td {{ border-bottom: none; }}
    code {{ background: #0f172a; color: #cbd5e1; padding: 2px 6px; border-radius: 6px; }}
    a {{ color: #60a5fa; }}
    .list li {{ margin: 6px 0; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p class=\"muted\">Generated: {escape(generated_at)}</p>
    <h1>Rank 2 / 17 / 29 / 32b Narrow Paper Lanes</h1>
    <p>这页负责汇报 narrow-paper / archived lanes 的运行状态。当前仍属 <code>P3 / narrow paper pilot</code> 的只有 <b>Rank 2</b>、<b>Rank 17</b>、<b>Rank 32b</b>；<b>Rank 29 baseline</b> 与 <b>Rank 29 gate shadow</b> 已因 strict-causal 复盘确认存在未来函数污染，正式降为 <code>P0 archived</code>，仅保留作历史审计材料。</p>
    <ul class=\"list muted\">
      <li>数据源：<code>Binance spot 15m klines</code></li>
      <li>范围：Rank 2 = BTC/ETH/SOL；Rank 17 = ETH/SOL only；Rank 29 = BTC/ETH/SOL baseline + low_trend_high_noise_w25 shadow（已归档）；Rank 32b = BTC/ETH/SOL</li>
      <li>口径：Rank 29 的 baseline / shadow 历史收益不再视为有效验证；仅保留作 future-leak 审计与后续重写时的反例材料。</li>
    </ul>
    {summary_cards}

    <h2>Rank29 这页现在怎么读</h2>
    <p class="muted">这张页面保留 <b>baseline</b> 与 <b>regime gate shadow</b> 两条历史 paper 线，但它们现在都属于 <b>P0 archived</b>。你只能把这里当成“当年我们如何被未来函数误导、后来又如何拆解问题”的审计材料，不能再把这些曲线当作可继续推进的 pilot 证据。订单簿执行问题仍在 <a href="../rank29_orderbook_shadow/report.html">orderbook shadow execution</a> 页面，但也只作研究辅助。</p>
    <ul class="list muted">
      <li><b>baseline</b>：原始 Rank29 narrow paper 主线（已撤销，不再视为有效基准）。</li>
      <li><b>gate shadow</b>：若命中 <code>low_trend_high_noise</code>，则该笔按 <code>25%</code> 曝险记账（同样已归档，只保留审计价值）。</li>
      <li><b>这里没有</b>：L2 orderbook 逐档吃单、spread/impact、拒单统计、perp 执行仿真。</li>
      <li><b>如果你想一页看完</b>：请看 <a href="../rank29_shadow_dashboard/report.html">baseline vs shadows dashboard</a>。</li>
    </ul>

    <h2>Desk reconciliation / operator reading</h2>
    <p class="muted">这张表回答的不是“paper 有没有 open 头寸”，而是“这些 open / P3 lane 现在是否默认还需要 bot3 继续补 append/review”。当前答案统一按 <code>no_default</code> 处理：专属 narrow-paper refresh 链负责 continuity，bot3 只在真的出现新的 closed-trade append 或 weekly-review row 时才回补。</p>
    {render_table(reconciliation_df, digits_cols={'candidate_rank':0,'open_positions':0})}

    <h2>Bot3 re-entry trigger queue</h2>
    <p class="muted">这张表把“什么时候才值得让 bot3 重新接管 P3 lane”写成显式触发器，而不是继续把 open position 本身误读成默认动作。当前这些 lane 默认都是 <code>bot3_reentry_now = no</code>；只有 manual narrow-paper refresh 真正追加 <code>closed trade</code> 或新的 <code>weekly-review row</code> 时，才重新回到 bot3 默认排班。</p>
    {render_table(bot3_trigger_df, digits_cols={'candidate_rank':0})}

    <h2>Cron / report freshness audit</h2>
    <p class="muted">这张表只回答一个运维问题：专属 narrow-paper 托管链现在是不是还在真实续写、状态页是不是跟得上、以及当前有没有因为 freshness 异常而需要 bot3 介入。只要 cron / artifacts / page 都在可接受窗口内，就应继续把它们视作 <code>cron-managed continuity</code>，而不是重新拉回 bot3 主资源。</p>
    {render_table(cron_freshness_df, digits_cols={'expected_max_age_min':0,'observed_age_min':1})}

    <h2>Rank 29 baseline vs gate shadow</h2>
    <p class="muted">这里的 shadow 版本使用 <code>low_trend_high_noise_w25</code> 的因果 paper 口径：每笔交易只看入场前最近一个已完成 UTC 日的 month-to-date regime 读数；若命中坏环境，则该笔按 <code>25%</code> 曝险记账。<b>注意：</b>这张表不是 orderbook shadow，不包含 L2 深度、spread/impact 或拒单信息。</p>
    {render_table(rank29_shadow_view, percent_cols={'lifetime_total_return_6bps','mean_exposure_weight','shadow_bad_regime_weight'}, digits_cols={'new_trades_appended':0,'gate_hit_trades':0})}

    <h2>Current lane status</h2>
    {render_table(lane_view, percent_cols={'lifetime_total_return_6bps'}, digits_cols={'candidate_rank':0,'new_trades_appended':0})}

    <h2>Open paper positions</h2>
    {render_table(open_df)}

    <h2>Recently appended closed trades</h2>
    {render_table(recent_ledger, percent_cols={'net_ret'}, digits_cols={'candidate_rank':0,'hold_bars':0})}

    <h2>Artifacts</h2>
    <ul class=\"list\">
      <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv\">manual_narrow_paper_status.csv</a></li>
      <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv\">manual_narrow_paper_open_positions.csv</a></li>
      <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_closed_trades.csv\">manual_narrow_paper_closed_trades.csv</a></li>
      <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_desk_reconciliation.csv\">manual_narrow_paper_desk_reconciliation.csv</a></li>
      <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_bot3_reentry_queue.csv\">manual_narrow_paper_bot3_reentry_queue.csv</a></li>
      <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_cron_freshness_audit.csv\">manual_narrow_paper_cron_freshness_audit.csv</a></li>
      <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json\">manual_narrow_paper_last_run_summary.json</a></li>
      <li><a href=\"../../artifacts/manual_narrow_paper_lanes/manual_narrow_paper_state.json\">manual_narrow_paper_state.json</a></li>
    </ul>
  </div>
</body>
</html>
"""
    OUT_PATH.write_text(html, encoding='utf-8')
    print(f"[ok] wrote {OUT_PATH}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
