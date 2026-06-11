#!/usr/bin/env python3
from __future__ import annotations

import json
from html import escape
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ARTIFACTS = ROOT / "reports" / "artifacts" / "chan2022_sr_feature_replication"
SITE = ROOT / "reports" / "site" / "reading" / "chan2022_sr_feature_replication"

SYMBOLS = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD"]
SAMPLES = [
    {"sample_key": "60m_365d", "interval": "60m", "period": "365d", "label": "60m / 365d"},
    {"sample_key": "60m_730d", "interval": "60m", "period": "730d", "label": "60m / 730d"},
]
BASELINE_FEATURES = [
    "ret_1",
    "ret_6",
    "ret_12",
    "vol_12",
    "vol_24",
    "volume_z_24",
    "hl_range_1",
    "close_vs_ema_24",
]
SR_FEATURES = [
    "dist_to_support_20",
    "dist_to_resistance_20",
    "range_pos_20",
    "is_above_resistance_20",
    "is_near_support_20",
    "is_near_resistance_20",
    "dist_to_support_55",
    "dist_to_resistance_55",
    "range_pos_55",
    "is_above_resistance_55",
    "is_near_support_55",
    "is_near_resistance_55",
]
TARGET_COL = "fwd_ret_12"
TOP_K = 2
HORIZON = 12
RIDGE_ALPHA = 10.0
TRAIN_RATIO = 0.7


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def flatten_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df


def download_bars(ticker: str, period: str, interval: str) -> pd.DataFrame:
    raw = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise ValueError(f"No data for {ticker} {period} {interval}")
    raw = flatten_yf_columns(raw)
    bars = raw.reset_index().rename(
        columns={
            "Datetime": "timestamp",
            "Date": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    keep = [c for c in ["timestamp", "open", "high", "low", "close", "volume"] if c in bars.columns]
    return bars[keep].dropna(subset=["open", "high", "low", "close"]).sort_values("timestamp").reset_index(drop=True)


def load_sample(sample: dict) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for symbol in SYMBOLS:
        df = download_bars(symbol, sample["period"], sample["interval"])
        df["symbol"] = symbol
        parts.append(df)
        print(f"downloaded {symbol} sample={sample['sample_key']} rows={len(df)}", flush=True)
    out = pd.concat(parts, ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    return out


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    g = df.copy().sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    out_parts: list[pd.DataFrame] = []
    for symbol, part in g.groupby("symbol", sort=False):
        p = part.copy()
        p["ret_1"] = p["close"].pct_change(1)
        p["ret_6"] = p["close"].pct_change(6)
        p["ret_12"] = p["close"].pct_change(12)
        p["vol_12"] = p["ret_1"].rolling(12).std()
        p["vol_24"] = p["ret_1"].rolling(24).std()
        p["volume_ma_24"] = p["volume"].rolling(24).mean()
        p["volume_std_24"] = p["volume"].rolling(24).std()
        p["volume_z_24"] = (p["volume"] - p["volume_ma_24"]) / p["volume_std_24"].replace(0, np.nan)
        p["hl_range_1"] = (p["high"] - p["low"]) / p["close"].replace(0, np.nan)
        ema24 = _ema(p["close"], 24)
        p["close_vs_ema_24"] = p["close"] / ema24 - 1.0

        for win in [20, 55]:
            support = p["low"].shift(1).rolling(win).min()
            resistance = p["high"].shift(1).rolling(win).max()
            width = (resistance - support).replace(0, np.nan)
            p[f"support_{win}"] = support
            p[f"resistance_{win}"] = resistance
            p[f"dist_to_support_{win}"] = p["close"] / support - 1.0
            p[f"dist_to_resistance_{win}"] = resistance / p["close"] - 1.0
            p[f"range_pos_{win}"] = (p["close"] - support) / width
            p[f"is_above_resistance_{win}"] = (p["close"] > resistance).astype(float)
            p[f"is_near_support_{win}"] = (((p["close"] - support).abs() / p["close"].replace(0, np.nan)) <= 0.003).astype(float)
            p[f"is_near_resistance_{win}"] = (((resistance - p["close"]).abs() / p["close"].replace(0, np.nan)) <= 0.003).astype(float)

        p[TARGET_COL] = p["close"].shift(-HORIZON) / p["close"] - 1.0
        p["target_up"] = (p[TARGET_COL] > 0).astype(float)
        p["row_idx_symbol"] = np.arange(len(p))
        split_idx = int(len(p) * TRAIN_RATIO)
        p["is_train"] = p["row_idx_symbol"] < split_idx
        out_parts.append(p)
    out = pd.concat(out_parts, ignore_index=True)
    use_cols = BASELINE_FEATURES + SR_FEATURES + [TARGET_COL, "target_up", "is_train"]
    out = out.dropna(subset=use_cols).reset_index(drop=True)
    return out


def fit_ridge_predict(train_df: pd.DataFrame, test_df: pd.DataFrame, features: list[str], alpha: float) -> tuple[np.ndarray, pd.DataFrame]:
    x_train = train_df[features].to_numpy(dtype=float)
    x_test = test_df[features].to_numpy(dtype=float)
    y_train = train_df[TARGET_COL].to_numpy(dtype=float)

    mu = x_train.mean(axis=0)
    sigma = x_train.std(axis=0)
    sigma[sigma == 0] = 1.0
    x_train_z = (x_train - mu) / sigma
    x_test_z = (x_test - mu) / sigma

    x_train_aug = np.c_[np.ones(len(x_train_z)), x_train_z]
    x_test_aug = np.c_[np.ones(len(x_test_z)), x_test_z]
    reg = np.eye(x_train_aug.shape[1]) * alpha
    reg[0, 0] = 0.0
    beta = np.linalg.solve(x_train_aug.T @ x_train_aug + reg, x_train_aug.T @ y_train)
    preds = x_test_aug @ beta

    coef_df = pd.DataFrame({
        "feature": ["intercept"] + features,
        "coef": beta,
    })
    return preds, coef_df


def _safe_corr(a: pd.Series, b: pd.Series) -> float:
    if len(a) < 3:
        return float("nan")
    if a.std(ddof=0) == 0 or b.std(ddof=0) == 0:
        return float("nan")
    return float(a.corr(b))


def top_bucket_stats(df: pd.DataFrame, score_col: str) -> dict[str, float]:
    if df.empty:
        return {"top_bucket_mean": np.nan, "bottom_bucket_mean": np.nan, "spread": np.nan}
    q_hi = df[score_col].quantile(0.8)
    q_lo = df[score_col].quantile(0.2)
    top = df[df[score_col] >= q_hi][TARGET_COL]
    bottom = df[df[score_col] <= q_lo][TARGET_COL]
    return {
        "top_bucket_mean": float(top.mean()) if len(top) else np.nan,
        "bottom_bucket_mean": float(bottom.mean()) if len(bottom) else np.nan,
        "spread": float(top.mean() - bottom.mean()) if len(top) and len(bottom) else np.nan,
    }


def rank_backtest(df: pd.DataFrame, score_col: str, label: str) -> tuple[pd.DataFrame, dict[str, float]]:
    rows: list[dict] = []
    if df.empty:
        return pd.DataFrame(), {"portfolio_total_return": np.nan, "avg_period_return": np.nan, "positive_period_ratio": np.nan, "periods": 0}
    g = df.sort_values(["timestamp", "symbol"]).copy()
    timestamps = list(pd.unique(g["timestamp"]))
    timestamps = timestamps[::HORIZON]
    for ts in timestamps:
        slab = g[g["timestamp"] == ts].copy()
        if slab.empty:
            continue
        slab = slab.sort_values(score_col, ascending=False).head(TOP_K)
        rows.append(
            {
                "timestamp": ts,
                "variant": label,
                "selected_symbols": ", ".join(slab["symbol"].tolist()),
                "period_return": float(slab[TARGET_COL].mean()),
                "avg_score": float(slab[score_col].mean()),
            }
        )
    periods = pd.DataFrame(rows)
    if periods.empty:
        return periods, {"portfolio_total_return": np.nan, "avg_period_return": np.nan, "positive_period_ratio": np.nan, "periods": 0}
    stats = {
        "portfolio_total_return": float((1.0 + periods["period_return"]).prod() - 1.0),
        "avg_period_return": float(periods["period_return"].mean()),
        "positive_period_ratio": float((periods["period_return"] > 0).mean()),
        "periods": int(len(periods)),
    }
    return periods, stats


def evaluate_variant(sample_key: str, df: pd.DataFrame, features: list[str], label: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_df = df[df["is_train"]].copy()
    test_df = df[~df["is_train"]].copy()
    preds, coefs = fit_ridge_predict(train_df, test_df, features, alpha=RIDGE_ALPHA)
    test_df = test_df.copy()
    test_df["score"] = preds
    test_df["variant"] = label
    test_df["sample_key"] = sample_key

    top_stats = top_bucket_stats(test_df, "score")
    period_df, bt_stats = rank_backtest(test_df, "score", label)

    symbol_summary = (
        test_df.groupby("symbol", dropna=False)
        .agg(
            ic=("score", lambda s: _safe_corr(pd.Series(s), test_df.loc[s.index, TARGET_COL])),
            mean_fwd_ret=(TARGET_COL, "mean"),
            top20_mean=(TARGET_COL, lambda s: float(s[test_df.loc[s.index, 'score'] >= test_df.loc[s.index, 'score'].quantile(0.8)].mean()) if len(s) else np.nan),
        )
        .reset_index()
    )

    summary = pd.DataFrame(
        [
            {
                "sample_key": sample_key,
                "variant": label,
                "train_rows": int(len(train_df)),
                "test_rows": int(len(test_df)),
                "test_ic": _safe_corr(test_df["score"], test_df[TARGET_COL]),
                "directional_accuracy": float(((test_df["score"] > 0) == (test_df[TARGET_COL] > 0)).mean()),
                "top_bucket_mean": top_stats["top_bucket_mean"],
                "bottom_bucket_mean": top_stats["bottom_bucket_mean"],
                "top_bottom_spread": top_stats["spread"],
                "portfolio_total_return": bt_stats["portfolio_total_return"],
                "avg_period_return": bt_stats["avg_period_return"],
                "positive_period_ratio": bt_stats["positive_period_ratio"],
                "periods": bt_stats["periods"],
            }
        ]
    )
    return summary, test_df, symbol_summary, coefs


def plot_metric_bars(summary: pd.DataFrame, out_path: Path) -> None:
    metrics = ["test_ic", "top_bottom_spread", "portfolio_total_return", "positive_period_ratio"]
    labels = ["IC", "Top-Bottom", "Portfolio Return", "Positive Ratio"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    axes = axes.flatten()
    for ax, metric, lab in zip(axes, metrics, labels):
        pivot = summary.pivot(index="sample_key", columns="variant", values=metric)
        pivot.plot(kind="bar", ax=ax)
        ax.set_title(lab)
        ax.axhline(0, color="#94a3b8", linewidth=1)
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_top_coefs(coefs: pd.DataFrame, out_path: Path) -> None:
    c = coefs[coefs["feature"] != "intercept"].copy()
    c["abs_coef"] = c["coef"].abs()
    top = c.sort_values("abs_coef", ascending=False).head(12).sort_values("coef")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top["feature"], top["coef"], color=np.where(top["coef"] >= 0, "#16a34a", "#dc2626"))
    ax.set_title("Enhanced model · top coefficients (|coef|)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def render_table(df: pd.DataFrame, max_rows: int = 120) -> str:
    if df is None or df.empty:
        return '<p class="muted">(empty)</p>'
    view = df.head(max_rows).copy()
    for c in view.columns:
        if pd.api.types.is_float_dtype(view[c]):
            view[c] = view[c].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return view.to_html(index=False, classes="tbl", border=0)


def main() -> None:
    ensure_dir(ARTIFACTS)
    ensure_dir(SITE)

    all_summary: list[pd.DataFrame] = []
    all_symbol: list[pd.DataFrame] = []
    all_periods: list[pd.DataFrame] = []
    enhanced_coefs_last = pd.DataFrame()
    sample_meta_rows: list[dict] = []

    for sample in SAMPLES:
        bars = load_sample(sample)
        feat = build_features(bars)
        sample_meta_rows.append(
            {
                "sample_key": sample["sample_key"],
                "interval": sample["interval"],
                "period": sample["period"],
                "rows": int(len(bars)),
                "feature_rows": int(len(feat)),
                "symbols": int(feat["symbol"].nunique()),
            }
        )
        for label, features in [("baseline_price_only", BASELINE_FEATURES), ("enhanced_plus_sr", BASELINE_FEATURES + SR_FEATURES)]:
            summary, scored, symbol_summary, coefs = evaluate_variant(sample["sample_key"], feat, features, label)
            periods, _ = rank_backtest(scored, "score", label)
            if not periods.empty:
                periods["sample_key"] = sample["sample_key"]
            symbol_summary["sample_key"] = sample["sample_key"]
            symbol_summary["variant"] = label
            coefs["sample_key"] = sample["sample_key"]
            coefs["variant"] = label
            all_summary.append(summary)
            all_symbol.append(symbol_summary)
            all_periods.append(periods)
            if label == "enhanced_plus_sr" and sample["sample_key"] == "60m_730d":
                enhanced_coefs_last = coefs.copy()
            print(f"evaluated sample={sample['sample_key']} variant={label}", flush=True)

    sample_meta = pd.DataFrame(sample_meta_rows)
    summary_df = pd.concat(all_summary, ignore_index=True) if all_summary else pd.DataFrame()
    symbol_df = pd.concat(all_symbol, ignore_index=True) if all_symbol else pd.DataFrame()
    periods_df = pd.concat(all_periods, ignore_index=True) if all_periods else pd.DataFrame()
    delta = summary_df.pivot(index="sample_key", columns="variant", values=["test_ic", "top_bottom_spread", "portfolio_total_return", "positive_period_ratio"]) if not summary_df.empty else pd.DataFrame()
    if not delta.empty:
        delta.columns = [f"{a}__{b}" for a, b in delta.columns]
        delta = delta.reset_index()
        delta["ic_delta_enh_minus_base"] = delta["test_ic__enhanced_plus_sr"] - delta["test_ic__baseline_price_only"]
        delta["spread_delta_enh_minus_base"] = delta["top_bottom_spread__enhanced_plus_sr"] - delta["top_bottom_spread__baseline_price_only"]
        delta["portfolio_delta_enh_minus_base"] = delta["portfolio_total_return__enhanced_plus_sr"] - delta["portfolio_total_return__baseline_price_only"]
        delta["positive_ratio_delta_enh_minus_base"] = delta["positive_period_ratio__enhanced_plus_sr"] - delta["positive_period_ratio__baseline_price_only"]
    plot_metric_bars(summary_df, ARTIFACTS / "metric_bars.png")
    if not enhanced_coefs_last.empty:
        plot_top_coefs(enhanced_coefs_last, ARTIFACTS / "enhanced_top_coefs.png")

    sample_meta.to_csv(ARTIFACTS / "sample_meta.csv", index=False)
    summary_df.to_csv(ARTIFACTS / "summary.csv", index=False)
    symbol_df.to_csv(ARTIFACTS / "symbol_summary.csv", index=False)
    periods_df.to_csv(ARTIFACTS / "period_backtest.csv", index=False)
    delta.to_csv(ARTIFACTS / "delta_vs_baseline.csv", index=False)
    enhanced_coefs_last.to_csv(ARTIFACTS / "enhanced_coefficients_60m_730d.csv", index=False)
    (ARTIFACTS / "summary.json").write_text(
        json.dumps(
            {
                "samples": SAMPLES,
                "baseline_features": BASELINE_FEATURES,
                "sr_features": SR_FEATURES,
                "target": TARGET_COL,
                "horizon_bars": HORIZON,
                "top_k": TOP_K,
                "ridge_alpha": RIDGE_ALPHA,
                "train_ratio": TRAIN_RATIO,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    headline_rows = []
    if not delta.empty:
        for _, row in delta.iterrows():
            headline_rows.append(
                f"<li><b>{escape(str(row['sample_key']))}</b>：enhanced 相比 baseline，<code>IC</code> 提升 {row['ic_delta_enh_minus_base']:.4f}，<code>top-bottom spread</code> 提升 {row['spread_delta_enh_minus_base']:.4f}；但最小 top-{TOP_K} 组合回测的 <code>portfolio_total_return</code> 反而下降 {row['portfolio_delta_enh_minus_base']:.4f}。</li>"
            )
    headline_html = ''.join(headline_rows) if headline_rows else '<li>当前无 headline。</li>'

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <title>Chan 2022 · S/R Feature Replication Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1320px; margin: 0 auto; }}
    .card {{ background:white; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; margin-bottom:18px; box-shadow:0 1px 2px rgba(0,0,0,0.04); }}
    .muted {{ color:#475569; }}
    .tbl {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    .tbl th,.tbl td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eff6ff; color:#1d4ed8; font-size:12px; margin-right:6px; }}
    img {{ max-width:100%; border:1px solid #e2e8f0; border-radius:12px; background:white; }}
    code {{ background:#f1f5f9; padding:1px 4px; border-radius:6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
<div class='wrap'>
  <div class='card'>
    <h1>Chan 2022 · S/R Feature Replication Report</h1>
    <p class='muted'>这是第一版 clean-room replication。目标不是复刻原论文全部智能模型，而是先回答：<b>把 Support / Resistance 结构特征加进一个干净的 price-only baseline 后，是否能带来稳定增量价值？</b></p>
    <p class='muted'><span class='pill'>baseline</span> 纯价格/波动/成交量特征 <span class='pill'>enhanced</span> baseline + clean-room S/R 特征 <span class='pill'>data</span> 8 crypto / 60m / 365d + 730d</p>
  </div>

  <div class='card'>
    <h2>为什么这个 baseline 合理？</h2>
    <ul>
      <li>它<strong>故意不用</strong>旧的 pyindicator 事件信号，避免把“旧主线太弱”这个问题又带回实验里。</li>
      <li>它只用普适的 price-only 特征做对照，因此更适合回答 Chan 2022 的原问题：<b>S/R 特征到底有没有增量信息</b>。</li>
      <li>增强版只额外加入 clean-room S/R 特征：<code>dist_to_support</code>、<code>dist_to_resistance</code>、<code>range_pos</code>、<code>is_above_resistance</code>、<code>is_near_support/resistance</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>Replication design</h2>
    <ol>
      <li>对每个 symbol 按时间切分 70% train / 30% test。</li>
      <li>用 ridge regression 预测未来 12 根 K 线收益 <code>fwd_ret_12</code>。</li>
      <li>在测试集上比较：
        <ul>
          <li><code>test_ic</code>：预测分数与未来收益的相关性</li>
          <li><code>top_bottom_spread</code>：高分桶与低分桶的未来收益差</li>
          <li>最小 rank-based backtest：每 12 根 K 线重排一次，只做得分最高的 2 个币</li>
        </ul>
      </li>
    </ol>
  </div>

  <div class='card'>
    <h2>Headline conclusion</h2>
    <ul>{headline_html}</ul>
    <p class='muted'>这说明第一版 clean-room 复现更像是在支持 Chan 2022 的“<b>S/R 特征有增量信息</b>”这一层，而不是马上支持“<b>当前这个最小组合构造已经能稳定赚到更多钱</b>”。</p>
  </div>

  <div class='card'>
    <h2>Sample meta</h2>
    {render_table(sample_meta, max_rows=10)}
  </div>

  <div class='card'>
    <h2>Summary</h2>
    {render_table(summary_df, max_rows=20)}
  </div>

  <div class='card'>
    <h2>Enhanced vs baseline delta</h2>
    <p class='muted'>正值表示 enhanced（加入 S/R 特征）优于纯 price-only baseline。</p>
    {render_table(delta, max_rows=10)}
  </div>

  <div class='card'>
    <h2>Metric bars</h2>
    <img src='../../artifacts/chan2022_sr_feature_replication/metric_bars.png' alt='metric bars' />
  </div>

  <div class='card'>
    <h2>Enhanced model · top coefficients (60m / 730d)</h2>
    <img src='../../artifacts/chan2022_sr_feature_replication/enhanced_top_coefs.png' alt='top coefficients' />
  </div>

  <div class='card'>
    <h2>Symbol summary</h2>
    {render_table(symbol_df, max_rows=40)}
  </div>

  <div class='card'>
    <h2>How to read the result</h2>
    <ul>
      <li>如果 enhanced 在两个样本里都让 <code>test_ic</code>、<code>top_bottom_spread</code>、<code>portfolio_total_return</code> 变好，说明 S/R 特征确实有增量价值。</li>
      <li>如果 enhanced 只让某一个指标好看，但别的指标变差，就说明第一版特征设计还不够稳。</li>
      <li>这页只是第一版 clean-room replication，不等于已经完全复刻原文全部智能模型。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>Artifacts</h2>
    <ul>
      <li><a href='../../artifacts/chan2022_sr_feature_replication/sample_meta.csv'>sample_meta.csv</a></li>
      <li><a href='../../artifacts/chan2022_sr_feature_replication/summary.csv'>summary.csv</a></li>
      <li><a href='../../artifacts/chan2022_sr_feature_replication/delta_vs_baseline.csv'>delta_vs_baseline.csv</a></li>
      <li><a href='../../artifacts/chan2022_sr_feature_replication/symbol_summary.csv'>symbol_summary.csv</a></li>
      <li><a href='../../artifacts/chan2022_sr_feature_replication/period_backtest.csv'>period_backtest.csv</a></li>
      <li><a href='../../artifacts/chan2022_sr_feature_replication/enhanced_coefficients_60m_730d.csv'>enhanced_coefficients_60m_730d.csv</a></li>
      <li><a href='../../artifacts/chan2022_sr_feature_replication/summary.json'>summary.json</a></li>
    </ul>
  </div>
</div>
</body>
</html>
"""
    (SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"Wrote report to {SITE / 'report.html'}", flush=True)


if __name__ == "__main__":
    main()
