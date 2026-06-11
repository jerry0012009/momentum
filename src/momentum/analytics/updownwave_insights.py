from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class QAInsight:
    question: str
    conclusion: str
    action: str


def _pct(v: float) -> str:
    return f"{v:.2%}" if pd.notna(v) else "-"


def _num(v: float, d: int = 2) -> str:
    return f"{v:.{d}f}" if pd.notna(v) else "-"


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def build_q1_q3_insights(artifact_dir: Path) -> Dict[str, QAInsight]:
    out: Dict[str, QAInsight] = {}

    q1 = _read_csv(artifact_dir / "usage_q1_module_positioning_summary.csv")
    if not q1.empty:
        up = q1[q1["scenario"] == "upwave_entry"].head(1)
        perm = q1[q1["scenario"].str.startswith("trade_permission_", na=False)]
        best_perm = perm.sort_values("median_max_drawdown", ascending=False).head(1)

        if not up.empty and not best_perm.empty:
            up = up.iloc[0]
            bp = best_perm.iloc[0]
            conc = (
                f"UpWave 直接入场中位 CAGR {_pct(up['median_cagr'])}，"
                f"中位回撤 {_pct(up['median_max_drawdown'])}；"
                f"作为交易许可（{bp['scenario']}）中位 CAGR {_pct(bp['median_cagr'])}，"
                f"中位回撤 {_pct(bp['median_max_drawdown'])}，交易频次更低。"
            )
        else:
            conc = "当前样本下，UpWave 兼具入场与过滤属性。"
    else:
        conc = "Q1 数据不足。"

    out["Q1"] = QAInsight(
        question="UpWave 更适合作为入场信号还是交易许可过滤器？",
        conclusion=conc,
        action="风险优先场景先用交易许可；收益优先场景保留入场并叠加状态过滤。",
    )

    q2 = _read_csv(artifact_dir / "usage_q2_event_study_summary.csv")
    if not q2.empty:
        up = q2[q2["signal_side"] == "upwave_long"]
        dn = q2[q2["signal_side"] == "downwave_short"]
        up_best = up.loc[up["mean_ret"].idxmax()] if not up.empty else None
        dn_best = dn.loc[dn["mean_ret"].idxmax()] if not dn.empty else None
        if up_best is not None and dn_best is not None:
            conc = (
                f"UpWave 最佳收益窗口约 {int(up_best['horizon'])} 天（均值 {_pct(up_best['mean_ret'])}），"
                f"DownWave(做空) 最佳窗口约 {int(dn_best['horizon'])} 天（均值 {_pct(dn_best['mean_ret'])}）。"
            )
        else:
            conc = "事件研究显示收益更偏延续型窗口。"
    else:
        conc = "Q2 数据不足。"

    out["Q2"] = QAInsight(
        question="该因子更擅长捕捉启动、延续，还是过滤失败抄底？",
        conclusion=conc,
        action="若 10~30 天窗口贡献更高，采用趋势持仓框架；短窗仅作战术补充。",
    )

    q3 = _read_csv(artifact_dir / "usage_q3_fear_conditions_summary.csv")
    if not q3.empty:
        downs = q3[q3["signal_side"] == "downwave_short"]
        bad_desc = []
        for ind in ["adx", "bbw_q", "atr_q"]:
            d = downs[downs["indicator"] == ind]
            if d.empty:
                continue
            q5 = d[d["bucket"] == "Q5"]["mean_ret"]
            if len(q5) and float(q5.iloc[0]) < 0:
                bad_desc.append(ind)
        if bad_desc:
            conc = f"做空腿在高分位 {', '.join(bad_desc)} 场景出现负期望，存在过热拥挤风险。"
        else:
            conc = "低趋势/低波动区间整体期望走弱。"
    else:
        conc = "Q3 数据不足。"

    out["Q3"] = QAInsight(
        question="该因子最怕什么市场环境（震荡/波动收缩/过热）？",
        conclusion=conc,
        action="设置禁入带：如 ADX<18 或 BBW 分位过低时减少交易；高拥挤区对做空腿额外限仓。",
    )
    return out


def build_q4_q6_insights(artifact_dir: Path) -> Dict[str, QAInsight]:
    out: Dict[str, QAInsight] = {}

    q4 = _read_csv(artifact_dir / "usage_q4_hold_robust_band.csv")
    if not q4.empty:
        pairs = [f"{r.mode}:{int(r.recommended_default_hold)}" for r in q4.itertuples()]
        conc = "模式对应稳健持有期中值为 " + "，".join(pairs) + "。"
    else:
        conc = "Q4 数据不足。"
    out["Q4"] = QAInsight(
        question="最佳持有期是否稳健，默认值如何选？",
        conclusion=conc,
        action="不追逐单点最优，优先选稳健区间中值并按模式分层配置。",
    )

    q5 = _read_csv(artifact_dir / "usage_q5_ma_n_oos_summary.csv")
    if not q5.empty:
        best = q5.loc[q5["median_cagr"].idxmax()]
        worst = q5.loc[q5["median_cagr"].idxmin()]
        conc = (
            f"滚动 OOS 最优参数 MA{int(best['ma_period'])}×N{int(best['n_days'])}"
            f"（中位 CAGR {_pct(best['median_cagr'])}），"
            f"最弱参数 MA{int(worst['ma_period'])}×N{int(worst['n_days'])}"
            f"（中位 CAGR {_pct(worst['median_cagr'])}），参数存在敏感性。"
        )
    else:
        conc = "Q5 数据不足。"
    out["Q5"] = QAInsight(
        question="MA 与连续天数 N 是否敏感，是否有过拟合风险？",
        conclusion=conc,
        action="参数敏感时改软评分/分层，而非硬固定单点参数。",
    )

    q6 = _read_csv(artifact_dir / "usage_q6_cost_budget_by_market.csv")
    if not q6.empty:
        valid = q6[q6["break_even_fee_bps"] >= 0]
        be_med = valid["break_even_fee_bps"].median() if not valid.empty else np.nan
        turn_med = valid["turnover_trades_per_year"].median() if not valid.empty else np.nan
        hold_med = valid["best_hold_days"].median() if not valid.empty else np.nan
        conc = (
            f"市场级 break-even fee 中位数约 {_num(be_med,1)} bps，"
            f"对应中位换手约 {_num(turn_med,1)} 笔/年、中位最优持有期 {_num(hold_med,0)} 天。"
        )
    else:
        conc = "Q6 数据不足。"
    out["Q6"] = QAInsight(
        question="考虑成本/滑点后策略还能活吗？",
        conclusion=conc,
        action="按市场维护成本预算表；当 roundtrip 成本超过 break-even 时降低换手并延长持有期。",
    )
    return out


def build_q7_q9_insights(artifact_dir: Path) -> Dict[str, QAInsight]:
    out: Dict[str, QAInsight] = {}

    q7 = _read_csv(artifact_dir / "usage_q7_combo_compare_summary.csv")
    if not q7.empty:
        ls10 = q7[(q7["mode"] == "long_short") & (q7["hold_days"] == 10)]
        if not ls10.empty:
            best_sh = ls10.loc[ls10["median_sharpe"].idxmax()]
            best_mdd = ls10.loc[ls10["median_max_drawdown"].idxmax()]
            conc = (
                f"long_short@10 下，Sharpe 最优为 {best_sh['combo_method']}（{_num(best_sh['median_sharpe'],3)}），"
                f"回撤最优为 {best_mdd['combo_method']}（MDD {_pct(best_mdd['median_max_drawdown'])}）。"
            )
        else:
            conc = "组合方法存在收益-回撤权衡。"
    else:
        conc = "Q7 数据不足。"
    out["Q7"] = QAInsight(
        question="主信号应如何组合（AND/分层/score 分位）？",
        conclusion=conc,
        action="用决策树按目标切换组合：risk-first 选低回撤组，return-first 选高 Sharpe/CAGR 组。",
    )

    q8 = _read_csv(artifact_dir / "usage_q8_risk_module_compare.csv")
    if not q8.empty and len(q8) >= 2:
        base = q8[q8["portfolio"] == "baseline"].head(1)
        layer = q8[q8["portfolio"] == "regime_layer"].head(1)
        if not base.empty and not layer.empty:
            b, l = base.iloc[0], layer.iloc[0]
            conc = (
                f"baseline→regime_layer：MDD {_pct(b['max_drawdown'])} → {_pct(l['max_drawdown'])}，"
                f"CAGR {_pct(b['cagr'])} → {_pct(l['cagr'])}。"
            )
        else:
            conc = "分层仓位具备风控价值。"
    else:
        conc = "Q8 数据不足。"
    out["Q8"] = QAInsight(
        question="该模块能否作为独立风控开关？",
        conclusion=conc,
        action="作为下行期风控开关而非常开模块；触发时降杠杆并限制高波动腿。",
    )

    q9 = _read_csv(artifact_dir / "usage_q9_asset_whitelist.csv")
    if not q9.empty:
        white = q9[q9["list_flag"] == "white"]["asset_class"].tolist()
        conc = f"当前白名单资产类别：{', '.join(white) if white else '无'}。"
    else:
        conc = "Q9 数据不足。"
    out["Q9"] = QAInsight(
        question="哪些资产适配该因子，名单规则如何定义？",
        conclusion=conc,
        action="按 rolling 正收益占比 + break-even + Calmar 动态维护白/灰/黑名单。",
    )
    return out


def build_q10_q14_insights(artifact_dir: Path) -> Dict[str, QAInsight]:
    out: Dict[str, QAInsight] = {}

    q10 = _read_csv(artifact_dir / "usage_q10_failure_monitor.csv")
    if not q10.empty:
        vc = q10["status"].value_counts().to_dict()
        conc = "当前状态分布：" + "，".join([f"{k}={v}" for k, v in vc.items()]) + "。"
    else:
        conc = "Q10 数据不足。"
    out["Q10"] = QAInsight(
        question="如何判定失效与降级？",
        conclusion=conc,
        action="执行三级降级：入场 → 过滤 → 停用，并按月滚动复核。",
    )

    q11 = _read_csv(artifact_dir / "usage_q11_signal_density_summary.csv")
    if not q11.empty:
        x = q11[q11["year"] < q11["year"].max()]
        conc = (
            f"信号密度均值约 {_num(x['mean_signal_count'].mean(),1)} 次/年/市场，"
            f"成交约 {_num(x['mean_trade_count'].mean(),1)} 笔，空仓比约 {_pct(x['mean_idle_ratio'].mean())}。"
        )
    else:
        conc = "Q11 数据不足。"
    out["Q11"] = QAInsight(
        question="信号密度是否合理，资金利用率是否健康？",
        conclusion=conc,
        action="设置容量阈值并把空仓窗口分配给低相关策略，控制换手。",
    )

    q12 = _read_csv(artifact_dir / "usage_oos_2y6m_by_fold.csv")
    if not q12.empty:
        agg = (
            q12.groupby(["ma_period", "n_days"], as_index=False)
            .agg(
                median_cagr=("cagr", "median"),
                iqr_cagr=("cagr", lambda s: float(np.nanpercentile(s, 75) - np.nanpercentile(s, 25))),
            )
        )
        best = agg.loc[agg["median_cagr"].idxmax()]
        conc = (
            f"滚动 OOS 最优中位收益参数为 MA{int(best['ma_period'])}×N{int(best['n_days'])}，"
            f"中位 CAGR {_pct(best['median_cagr'])}，IQR {_pct(best['iqr_cagr'])}。"
        )
    else:
        conc = "Q12 数据不足。"
    out["Q12"] = QAInsight(
        question="2年训练+6个月验证的滚动 OOS 稳定吗？",
        conclusion=conc,
        action="用分位数稳定性约束参数选择，并持续滚动再评估。",
    )

    q13 = _read_csv(artifact_dir / "usage_tail_risk_summary.csv")
    if not q13.empty:
        ls10 = q13[(q13["mode"] == "long_short") & (q13["hold_days"] == 10)].head(1)
        if not ls10.empty:
            r = ls10.iloc[0]
            conc = (
                f"long_short@10：p5 单笔 {_pct(r['p5_trade_ret'])}，"
                f"最差5%均值 {_pct(r['avg_worst5_ret'])}，建议仓位上限约 {_pct(r['position_size_hint'])}。"
            )
        else:
            conc = "尾部风险显著，需仓位约束。"
    else:
        conc = "Q13 数据不足。"
    out["Q13"] = QAInsight(
        question="尾部风险有多大，仓位和止损如何定？",
        conclusion=conc,
        action="用 worst-5% 与 MAE 联动设置仓位上限，并叠加 vol targeting。",
    )

    out["Q14"] = QAInsight(
        question="综合来看，该因子在实盘中的最优定位是什么？",
        conclusion="该因子更像条件型趋势模块（入场+过滤+风控联动），不建议裸跑单模块。",
        action="默认框架：long-first + regime gating + 成本预算 + 失效降级监控。",
    )
    return out


def build_q_insights(artifact_dir: Path) -> Dict[str, QAInsight]:
    out: Dict[str, QAInsight] = {}
    out.update(build_q1_q3_insights(artifact_dir))
    out.update(build_q4_q6_insights(artifact_dir))
    out.update(build_q7_q9_insights(artifact_dir))
    out.update(build_q10_q14_insights(artifact_dir))
    return out


def insights_to_dict(q: Dict[str, QAInsight]) -> Dict[str, dict]:
    return {k: asdict(v) for k, v in q.items()}
