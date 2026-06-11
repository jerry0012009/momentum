# Rank 213 survivor follow-up promote P2

- Time: 2026-03-28 07:29 UTC
- Target: `Rank 213 / large-cap XS momentum × short-leg jump veto`
- Action: 唯一一次 decisive survivor follow-up；把 universe 放宽到更接近论文 failure mode 的 `30` 个 liquid USDT perp，并并排比较 `plain XS momentum`、`short-leg jump veto`、`single-name short cap`、`strategy-level inverse-vol`
- Verdict: `promote_P2`

## What changed
这次 follow-up 已经把唯一 blocker 真正回答清楚了：**在更宽的 liquid alt-perp universe 里，plain XS momentum 并不是本体直接坏死；真正把它从“能跑”拖回“不能用”的，确实是 short leg 被高 jump 名单集中打穿。** 一旦把 short 侧从“机械 bottom-3”改成带 `jump veto` 的版本，left tail 与成本后结果都出现了实质级别改善，这就不再只是 `keep_P1` 的故事，而是足以进入 `P2 admission` 的对象。

## Evidence used for the close
直接新跑了一版 widening follow-up artifact：`reports/artifacts/optimization_loop/rank213_survivor_followup_20260328/summary.json` 与 `timeseries.csv`。

口径：
- 数据：Binance USDⓈ-M Futures 公共 `15m` K 线
- 样本：`2026-02-09 10:15 UTC ~ 2026-03-28 07:00 UTC`，共 `4500` 根 bar / `550` 次非重叠换仓
- universe：当前仍在交易、且在样本起点前已上线的 `30` 个高成交 `USDT` perpetual
- signal：过去 `96` 根 `15m`（约 `24h`）收益做横截面排名，未来 `8` 根 `15m`（约 `2h`）持有
- 组合骨架：`top-3 long / bottom-3 short` market-neutral；并行比较 `jump veto`、`short cap 25%`、`strategy-level inverse-vol`

关键结果：
- `plain`：
  - gross mean：`+6.50 bps/rebalance`
  - net mean @ `4 bps`：`+2.26 bps`
  - net cumulative @ `4 bps`：`-17.82%`
  - 5% left-tail：`-459.29 bps`
  - 平均最大单名 short 损失：`84.21 bps`
- `short-leg jump veto`：
  - gross mean：`+14.19 bps/rebalance`
  - net mean @ `4 bps`：`+9.85 bps`
  - net cumulative @ `4 bps`：`+37.77%`
  - 5% left-tail：`-400.49 bps`
  - 平均最大单名 short 损失：`39.58 bps`
  - `avg_vetoed_short_names_per_rebalance = 1.218`
  - `pct_rebalances_with_any_veto = 71.64%`
- `single-name short cap (25%)`：
  - net mean @ `4 bps`：`+5.04 bps`
  - net cumulative @ `4 bps`：`+0.32%`
- `strategy-level inverse-vol`：
  - net mean @ `4 bps`：`+6.47 bps`
  - net cumulative @ `4 bps`：`+2.45%`

最重要的结构性诊断：
- plain 的 `avg_top_short_contributor_share = 0.677`，说明亏损时 short 侧经常接近被单名主导；
- jump-veto 版本把 `avg_largest_short_loss` 从 `84.21 bps` 直接压到 `39.58 bps`，`p95` 也从 `323.68 bps` 降到 `128.65 bps`；
- short 侧过去 `24h` 最大 `15m` 上冲 bar 的均值，从 plain 的 `6.05%` 降到 veto 版本的 `1.98%`。

这组数放在一起，含义已经够明确：**更宽 alt-perp pocket 里的 decisive blocker 不是“XS momentum 本体根本不存在”，而是 short leg single-name jump concentration；而且在我们这版最小 transfer 里，`jump veto` 明显比单纯 `short cap` 或 strategy-level `inverse-vol` 更接近对症。**

## Why this is promote_P2
`P2` 需要的是“已经看到值得继续做 admission 的生存证据”，而不是已经全维度毕业。当前 follow-up 已经满足前者：
1. blocker 被直接回答：在更宽 universe 中，`short-leg jump veto` 不只是名义减亏，而是把 net mean 与 net cumulative 都推到了显著优于 plain 的水平；
2. 提升不是 generic overlay 随便都行：`short cap` 与 `inverse-vol` 也有改善，但力度明显不如 `jump veto`，说明 paper 指向的 failure mode 具备针对性；
3. 对象下一步已经很清楚：它现在值得进入正式 `P2 admission`，去补 `cross-asset stability / time stability / parameter stability / execution realism`，而不是继续停在 `P1` 讲概念。

## Why this is not P3 yet
还不能直接升 `P3`，因为当前证据仍只是一次 survivor widening check：
- universe 是按当前 liquid perpetual 做的静态截面，不是长期稳定的 live admission universe；
- 还没做更完整的 friction / venue / horizon / parameter stability 组；
- 还没把 veto 规则写成 admission-ready 的可部署 spec（例如阈值、refill 规则、资产准入、动态 liquidity guard）。

所以这一步最诚实的位置是：**从 `P1 survivor` 升到 `Active P2`，而不是直接宣布可 paper launch。**

## Runtime implication
- `Rank 213` 的 survivor follow-up 预算已用完，并且结果是正向升级；因此它不再占用 survivor 槽位。
- 当前 `Active P2 slot` 应切换为 `Rank 213 / large-cap XS momentum × short-leg jump veto`。
- 下一轮若继续做它，应该进入标准 `P2 admission`：优先补 `parameter stability + execution realism`，而不是再做开放式 fresh-intake 风格探索。

## Result sentence
`Rank 213 / large-cap XS momentum × short-leg jump veto` 的唯一 survivor follow-up 已回答核心 blocker：在更宽的 `30` 币 liquid alt-perp universe 里，plain XS momentum 的主要失败模式确实是 short-leg single-name jump concentration，而 `jump veto` 相比 `short cap` 与 `inverse-vol` 给出了最明显的成本后改善，因此这条对象应从 `P1 survivor` 正式升到 `P2 admission`。
