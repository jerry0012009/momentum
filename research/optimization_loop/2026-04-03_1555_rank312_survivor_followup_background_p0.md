# Rank 312 — adaptive regime switch × trend/MR dual sleeve — survivor follow-up closed to background/P0

- 时间：2026-04-03 15:55 UTC
- 轮次：bot3 13 分钟自动执行
- 对象：`Rank 312 / adaptive regime switch × trend sleeve / mean-reversion sleeve`
- 本轮动作：survivor 唯一一次 follow-up（按 state 要求收口 `regime-switched` vs `trend-only` vs `MR-only` 的最小 ablation verdict）
- 结论：**不升 `P2`，直接退回 `background/P0`**

## 本轮实际检查了什么
1. 重读对象 digest：`research/quant_digests/2026-04-03_1020_adaptive-regime-switch-trend-mr-alpha.md`
2. 重读 first verdict：`research/optimization_loop/2026-04-03_1542_rank312_adaptive_regime_first_verdict_keep_p1.md`
3. 在项目内检索 `Rank 312 / adaptive regime / regime-switched / trend-only / MR-only` 的后续实验、clean-room 结果、ablation artifact

## 检查结果
本轮没有找到任何新的 reader-facing 或 runtime 级证据，能把这条对象从“完整策略壳”推进到“router 对 short-cycle post-cost 真的有新增系统认知”。

项目内当前能确认的仍只有：
- repo 源码确实写出了完整对象：`ATR/ADX regime router + trend sleeve + range sleeve + ATR trailing + cost/risk shell`；
- repo README/源码给的是 **90 天 hourly Hyperliquid** 口径；
- digest 明确把下一步 decisive blocker 写成：在统一 `BTC/ETH/SOL 15m`、统一成本口径下，做 `regime-switched` vs `trend-only` vs `MR-only` 的最小 honest ablation。

但本轮检索后，未发现：
- 统一 `BTC/ETH/SOL 15m` 的 clean-room 对照结果；
- `regime-switched` 相对 `trend-only` / `MR-only` 至少一边仍保留更稳定净后 pocket 的证据；
- 收益不是由单一 sleeve 或单一标的支撑的 attribution 证据。

## 为什么本轮不能升 P2
按照本轮 state 写死的 success criterion，survivor follow-up 必须回答：

> `regime-switched` 相对单腿基线，是否至少一边仍保留更稳定的净后 pocket，且收益不被单一 sleeve / 单一标的完全支撑。

现在能确认的只有“这是一条完整壳”，还不能确认“router 在 short-cycle post-cost 上真的创造了新增系统认知”。

换句话说：
- **对象成立为策略壳**，所以 first verdict 给 `keep_P1` 没问题；
- **但 survivor 轮要验证的是 router 的新增价值**，这一点目前仍停留在“应该怎么测”，没有进入“已经测出什么”。

因此继续把它留在 survivor 或直接升 `P2`，都会把“尚未产生的新证据”误写成“已经存在的 admission 证据”。这不合法。

## 会改变系统认知的一句话结果
`Rank 312` 已证明自己是完整的 `regime-switched dual-alpha` 策略壳，但在 survivor 唯一一次 follow-up 里，仍拿不出统一 `BTC/ETH/SOL 15m`、统一成本口径下的 `regime-switched vs trend-only vs MR-only` 最小 ablation 证据；因此当前不能把 router 的价值写成已成立，结论是 **survivor 收口后退回 `background/P0`**。

## 对后续系统的含义
这不是否认对象有研究价值，而是把它从“当前前排候选”诚实降回“背景候选”：
- 若未来出现真正的 clean-room ablation 结果，可再作为新证据重新 intake；
- 在那之前，不应继续占用 survivor / P2 前排资源。
