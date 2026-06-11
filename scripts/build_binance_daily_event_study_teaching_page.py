#!/usr/bin/env python3
"""Build a plain-Chinese teaching page for Binance daily event study v0."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.html_render import (  # noqa: E402
    PAGE_CSS_DARK,
    fmt_int,
    fmt_pct,
    render_metric_cards,
    render_note,
    render_page,
    render_section,
    render_table,
    write_page,
)

ART = ROOT / "jerry" / "wlfi" / "FR_Monitor" / "reports" / "artifacts" / "binance_daily_event_study_v0"
OUT = ROOT / "reports" / "site" / "paper" / "binance_daily_event_study_v0.html"


def pct(v: float, digits: int = 2) -> str:
    return fmt_pct(v, digits=digits)


def fmt_year(v) -> str:
    return str(int(v)) if pd.notna(v) else "—"


def code(x: str) -> str:
    return f"<code>{escape(x)}</code>"


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def h3(text: str) -> str:
    return f"<h3>{escape(text)}</h3>"


def mini_bar_table(df: pd.DataFrame, label_col: str, value_col: str, title: str, note: str = "") -> str:
    if df.empty:
        return ""
    vals = df[value_col].astype(float)
    max_abs = max(abs(vals.min()), abs(vals.max()), 1e-9)
    rows = []
    for _, r in df.iterrows():
        label = escape(str(r[label_col]))
        val = float(r[value_col])
        width = min(100, abs(val) / max_abs * 100)
        color = "#ef4444" if val < 0 else "#22c55e"
        rows.append(
            f"<tr><td style='width:260px'>{label}</td>"
            f"<td class='num'>{pct(val)}</td>"
            f"<td><div class='bar-track'><div class='bar' style='width:{width:.1f}%;background:{color}'></div></div></td></tr>"
        )
    return f"<h3>{escape(title)}</h3>{p(note) if note else ''}<table><tbody>{''.join(rows)}</tbody></table>"


def load() -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    manifest = json.loads((ART / "manifest_v0.json").read_text(encoding="utf-8"))
    atomic = pd.read_csv(ART / "summary_by_tag_v0.csv")
    combo = pd.read_csv(ART / "combo_summary_v0.csv")
    yearly = pd.read_csv(ART / "yearly_summary_v0.csv")
    events = pd.read_csv(ART / "events_v0.csv", usecols=["event_date", "symbol", "tags", "year"])
    return manifest, atomic, combo, yearly, events


def pretty_atomic(atomic: pd.DataFrame) -> pd.DataFrame:
    name_map = {
        "top_gainer_1d": "涨幅榜 Top20",
        "top_loser_1d": "跌幅榜 Bottom20",
        "funding_extreme_positive": "高正资金费率 Top20",
        "funding_extreme_negative": "高负/低资金费率 Bottom20",
    }
    d = atomic.copy()
    d["事件类型"] = d["tag"].map(name_map).fillna(d["tag"])
    d["样本数"] = d["events"]
    d["涉及币数"] = d["symbols"]
    d["1天后价格"] = d["price_1d_mean"]
    d["5天后价格"] = d["price_5d_mean"]
    d["10天后价格"] = d["price_10d_mean"]
    d["5天做多含资金费"] = d["long_total_5d_mean"]
    d["5天做空含资金费"] = d["short_total_5d_mean"]
    d["做空胜率5天"] = d["short_total_5d_win_rate"]
    return d[["事件类型", "样本数", "涉及币数", "1天后价格", "5天后价格", "10天后价格", "5天做多含资金费", "5天做空含资金费", "做空胜率5天"]]


def pretty_combo(combo: pd.DataFrame) -> pd.DataFrame:
    name_map = {
        "funding_extreme_negative": "低/负 funding",
        "funding_extreme_positive": "高正 funding",
        "top_gainer_1d": "涨幅榜",
        "top_loser_1d": "跌幅榜",
    }
    d = combo.copy()
    def rename_tags(s: str) -> str:
        return " + ".join(name_map.get(x, x) for x in str(s).split("+"))
    d["组合事件"] = d["tags"].map(rename_tags)
    d["样本数"] = d["events"]
    d["5天后价格"] = d["price_5d_mean"]
    d["10天后价格"] = d["price_10d_mean"]
    d["5天上涨概率"] = d["price_5d_win_rate"]
    d["5天做多含资金费"] = d["long_total_5d_mean"]
    d["5天做空含资金费"] = d["short_total_5d_mean"]
    d["5天多头MAE中位数"] = d["mae_long_5d_median"]
    d["5天多头MFE中位数"] = d["mfe_long_5d_median"]
    return d.sort_values("5天后价格")[["组合事件", "样本数", "5天后价格", "10天后价格", "5天上涨概率", "5天做多含资金费", "5天做空含资金费", "5天多头MAE中位数", "5天多头MFE中位数"]]


def pretty_yearly(yearly: pd.DataFrame) -> pd.DataFrame:
    d = yearly.copy()
    d["年份"] = d["year"]
    d["样本数"] = d["events"]
    d["5天后价格"] = d["price_5d_mean"]
    d["5天上涨概率"] = d["price_5d_win_rate"]
    d["5天做多含资金费"] = d["long_total_5d_mean"]
    d["5天做空含资金费"] = d["short_total_5d_mean"]
    d["5天多头MAE中位数"] = d["mae_long_5d_median"]
    return d[["年份", "样本数", "5天后价格", "5天上涨概率", "5天做多含资金费", "5天做空含资金费", "5天多头MAE中位数"]]


def build_body(manifest: dict, atomic: pd.DataFrame, combo: pd.DataFrame, yearly: pd.DataFrame, events: pd.DataFrame) -> str:
    cards = [
        {"label": "这页的最终结论", "value": "先别追涨", "subtitle": "日线榜单事件后，整体更像 5-10 天回落", "kind": "warn"},
        {"label": "事件样本", "value": fmt_int(manifest["event_rows"]), "subtitle": f"{manifest['event_date_min']} → {manifest['event_date_max']}"},
        {"label": "覆盖币种", "value": fmt_int(manifest["event_symbols"]), "subtitle": "Binance USDT-M 历史日线 + funding"},
        {"label": "涨幅榜5天后均值", "value": pct(float(atomic.loc[atomic.tag == 'top_gainer_1d', 'price_5d_mean'].iloc[0])), "subtitle": "不是 continuation，而是偏回落", "kind": "bad"},
        {"label": "高正funding后做空5天", "value": pct(float(atomic.loc[atomic.tag == 'funding_extreme_positive', 'short_total_5d_mean'].iloc[0])), "subtitle": "价格回落 + 收 funding 的粗粒度结果", "kind": "good"},
        {"label": "2023/2024警告", "value": "会反过来", "subtitle": "牛市/强beta年份事件后反而偏上涨", "kind": "warn"},
    ]

    body = ""
    body += render_metric_cards(cards)

    body += render_section("0. 先讲人话：这次到底在问什么？", "".join([
        render_note("我们不是在做一个已经可以实盘的策略，而是在做“事件研究”：历史上某类事情发生后，后面价格通常怎么走？先找规律，再谈交易。", kind="warn"),
        p("你现在关心的是：213、32b、154 这些线 alpha 都很薄，下一步到底该往哪里推进。我们先选了一个最小、可验证的 Step 1：用 Binance 历史日线 K 线 + 资金费率，研究“榜单币/拥挤币事件”发生后，未来 1/3/5/10 天的表现。"),
        p("简单说：如果一个币今天涨幅榜靠前，或者 funding 特别高/特别低，它之后是继续冲，还是回落？这个问题如果都没吃透，就不应该急着做 live radar。"),
    ]))

    body += render_section("1. 数据从哪里来？有没有未来函数？", "".join([
        p(f"输入数据是已有的历史面板：{code(str(manifest['input_panel']))}。它来自 Binance public archive 的 USDⓈ-M futures 日线 K 线和 fundingRate。"),
        ul([
            "K 线：每天 open/high/low/close、成交额等。",
            "Funding：每天发生过的资金费率结算记录，聚合出当天最后一笔、当天合计、当天结算次数。",
            "Universe：每个历史日期只用当时已经知道的数据，按过去 30 天成交额选 Top100。不是用今天最活跃的币倒回去看历史。",
            "Listing age：要求上市至少 30 天，避免刚上线没历史的极端噪声。",
        ]),
        render_note("关键防未来函数点：每天的 universe 都是按“历史当天”的 trailing 30d quote volume 选出来的，不用今天的排名；收益标签只看事件日之后 t+1...t+h。", kind="good"),
    ]))

    body += render_section("2. 我们定义了哪些“事件”？", "".join([
        p("每天先选出历史当日流动性 Top100 的币，然后在这 100 个币里打标签。一个币一天可能同时有多个标签，比如既是涨幅榜，又是高 funding。"),
        render_table(pd.DataFrame([
            {"事件": "涨幅榜 Top20", "代码标签": "top_gainer_1d", "人话解释": "今天涨得最猛的一批币。我们想看：追涨有没有优势？"},
            {"事件": "跌幅榜 Bottom20", "代码标签": "top_loser_1d", "人话解释": "今天跌得最惨的一批币。我们想看：会不会反弹，还是继续跌？"},
            {"事件": "高正资金费率 Top20", "代码标签": "funding_extreme_positive", "人话解释": "多头很拥挤，正 funding 意味着多头付钱给空头。"},
            {"事件": "高负/低资金费率 Bottom20", "代码标签": "funding_extreme_negative", "人话解释": "空头拥挤，或者多头可以收 funding。"},
        ])),
        p("注意：Binance funding 有 1h/2h/4h/8h 不同结算间隔，所以不能直接比较 fundingRate 原始值。我这里用了小时归一的估算：" + code("funding_per_hour_est = carry_raw / funding_interval_est_hours") + "。"),
    ]))

    body += render_section("3. 每个事件后，我们看了什么结果？", "".join([
        p("每条事件是一行样本。比如：2025-某天，某币进入涨幅榜 Top20，同时 funding 很高。然后我们看它后面 1/3/5/10 天怎么走。"),
        render_table(pd.DataFrame([
            {"指标": "price_5d_mean", "意思": "事件后 5 天的纯价格收益均值。正数=涨，负数=跌。"},
            {"指标": "long_total_5d_mean", "意思": "假设做多 5 天：价格收益 - 期间付/收的 funding。"},
            {"指标": "short_total_5d_mean", "意思": "假设做空 5 天：-价格收益 + 期间收/付的 funding。"},
            {"指标": "win rate", "意思": "收益大于 0 的比例。比如做空胜率 55%，不是暴利，只是略偏。"},
            {"指标": "MAE/MFE", "意思": "持有期间最不利/最有利的路径。这里是日收盘路径，真实日内风险会更大。"},
        ])),
        render_note("正 funding 的含义：多头付钱给空头。所以高正 funding 的币，如果价格又回落，做空会同时吃到价格回落和 funding 收入。", kind="good"),
    ]))

    atomic_pretty = pretty_atomic(atomic)
    combo_pretty = pretty_combo(combo)
    yearly_pretty = pretty_yearly(yearly)

    body += render_section("4. 单事件结果：最重要的一张表", "".join([
        p("这张表先不要看复杂组合，只看单个标签。最核心的是 5 天后价格和 5 天做多/做空含 funding。"),
        render_table(
            atomic_pretty,
            col_formats={
                "样本数": fmt_int, "涉及币数": fmt_int,
                "1天后价格": fmt_pct, "5天后价格": fmt_pct, "10天后价格": fmt_pct,
                "5天做多含资金费": fmt_pct, "5天做空含资金费": fmt_pct, "做空胜率5天": fmt_pct,
            },
            col_positive_good=["1天后价格", "5天后价格", "10天后价格", "5天做多含资金费", "5天做空含资金费"],
        ),
        mini_bar_table(atomic_pretty, "事件类型", "5天后价格", "直观看：四类事件 5 天后价格均值", "绿色代表事件后上涨，红色代表事件后下跌。这里四类都是红的。"),
        render_note("第一结论：涨幅榜并没有继续涨。涨幅榜 Top20 事件后 5 天平均 -0.54%，10 天平均 -0.91%。这不是追涨信号。", kind="bad"),
    ]))

    body += render_section("5. 组合事件：榜单 + funding 叠加后，有没有更清楚？", "".join([
        p("组合事件的意义是：单纯涨幅榜可能太粗，我们想看“涨幅榜 + 高 funding”这种更贴近控盘/拥挤的状态。"),
        render_table(
            combo_pretty,
            col_formats={
                "样本数": fmt_int,
                "5天后价格": fmt_pct, "10天后价格": fmt_pct, "5天上涨概率": fmt_pct,
                "5天做多含资金费": fmt_pct, "5天做空含资金费": fmt_pct,
                "5天多头MAE中位数": fmt_pct, "5天多头MFE中位数": fmt_pct,
            },
            col_positive_good=["5天后价格", "10天后价格", "5天做多含资金费", "5天做空含资金费", "5天多头MFE中位数"],
        ),
        ul([
            "涨幅榜 + 高正 funding：5 天后价格平均 -0.46%，做空含 funding 约 +0.59%。这更像拥挤后回落，不像继续冲。",
            "跌幅榜 + 高正 funding：5 天后价格几乎不跌，说明这种组合不适合简单追空，可能有 squeeze/承接。",
            "低/负 funding + 涨幅榜：价格也回落，但做多能收 funding，所以方向不干净。",
        ]),
        render_note("这一步没有得到“发现神奇厚 alpha”的结果，但得到了很有价值的排除项：不要把榜单币等同于可追涨机会。", kind="warn"),
    ]))

    body += render_section("6. 年度拆开看：为什么不能直接上 live？", "".join([
        p("如果一个规律只在某几年有效，另几年反过来，那就不是无脑 alpha，而是 regime-dependent。这里年度拆分非常关键。"),
        render_table(
            yearly_pretty,
            col_formats={
                "年份": fmt_year, "样本数": fmt_int,
                "5天后价格": fmt_pct, "5天上涨概率": fmt_pct,
                "5天做多含资金费": fmt_pct, "5天做空含资金费": fmt_pct,
                "5天多头MAE中位数": fmt_pct,
            },
            col_positive_good=["5天后价格", "5天做多含资金费", "5天做空含资金费"],
        ),
        mini_bar_table(yearly_pretty, "年份", "5天后价格", "按年份看 5 天后价格均值", "2023/2024 是正的，说明强 beta 年份里事件后可能继续涨。"),
        render_note("最大警告：2021/2022/2025/2026 偏回落，但 2023/2024 偏继续涨。所以这个发现不能直接变成 live 策略，必须加市场 regime 或二级确认。", kind="bad"),
    ]))

    body += render_section("7. 这次研究告诉我们什么？", "".join([
        h3("结论 A：先不要走“泛因子 IC 挖矿”"),
        p("大规模 IC/IR 当然能做，但它很容易重新掉进 213/154 那种“看起来有一点点、交易后很薄”的坑。现在更应该围绕事件做深，而不是横向铺开一堆弱因子。"),
        h3("结论 B：FR monitor 方向仍然有价值，但不是直接 DEX-CEX 历史套利"),
        p("这次用的是 Binance 单所历史数据，还不能证明 DEX-CEX funding/basis 套利。但它证明了 funding extreme 是重要的拥挤状态变量，值得作为 radar 条件之一。"),
        h3("结论 C：控盘币/榜单币方向值得继续，但入口不是“看到涨就追”"),
        p("更可能的机会是：榜单币进入异常状态 → funding/成交额/新高/连续上涨确认拥挤 → 然后等失速信号。也就是事件候选 + 二级确认，而不是事件当天无脑上。"),
    ]))

    body += render_section("8. 我建议我们下一步怎么做？", "".join([
        render_note("我的建议：先把这页吃透。如果你认可 v0 结论，Step 1.1 就做条件化事件研究，而不是直接开发交易。", kind="good"),
        render_table(pd.DataFrame([
            {"下一步": "事件分桶", "具体做法": "按上市年龄、涨幅大小、funding Top5/Top10/Top20 分开看", "目的": "找到是不是只有某类新币/极端事件有 edge"},
            {"下一步": "形态过滤", "具体做法": "是否接近20日新高、是否连续3日上涨、是否放量、事件后第1天是否失速", "目的": "把“热闹事件”变成“可交易候选”"},
            {"下一步": "局部小时线/分钟线", "具体做法": "只抽 200-500 个典型事件下载 1h/1m K线", "目的": "看真实入场、止损、MAE，不被日线均值骗"},
        ])),
        p("我倾向于下一步专攻：" + code("top_gainer / high funding / event reversal") + "。这条线最贴近你说的币安人生、pippin、siren 这类榜单/控盘币机会。"),
    ]))

    body += render_section("9. 产物索引", "".join([
        render_table(pd.DataFrame([
            {"文件": "events_v0.csv", "用途": "每条事件的原始样本，可继续分桶/抽样。"},
            {"文件": "summary_by_tag_v0.csv", "用途": "单事件标签汇总。"},
            {"文件": "combo_summary_v0.csv", "用途": "组合事件汇总。"},
            {"文件": "yearly_summary_v0.csv", "用途": "年度稳定性检查。"},
            {"文件": "STEP1_FINDINGS_V0.md", "用途": "第一轮文字结论。"},
            {"文件": "scripts/build_binance_daily_event_study.py", "用途": "生成事件样本的脚本。"},
        ])),
        p("页面生成时间：" + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")),
    ]))
    return body


def main() -> None:
    manifest, atomic, combo, yearly, events = load()
    body = build_body(manifest, atomic, combo, yearly, events)
    extra_css = PAGE_CSS_DARK + """
    .bar-track { height: 12px; background: #0f172a; border-radius: 999px; overflow: hidden; border: 1px solid #1f2937; }
    .bar { height: 100%; border-radius: 999px; opacity: .9; }
    .hero { background: radial-gradient(circle at top left, #1e3a8a55, transparent 35%), linear-gradient(135deg, #0f172a 0%, #111827 100%); }
    """
    html = render_page(
        "Step 1 事件研究：榜单币和 Funding 到底告诉了我们什么？",
        body,
        subtitle="用 Binance 历史日线 K 线 + 资金费率，把“涨跌榜/控盘币/拥挤 funding”先讲明白，再决定下一步。",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        css=extra_css,
    )
    write_page(OUT, html)
    print(f"[ok] wrote {OUT}")


if __name__ == "__main__":
    main()
