# 2026-04-01 01:44 UTC — Rank 276 fresh intake：BTC 15m Donchian overshoot fade × 10bps breach threshold → keep_P1

- target: `research/quant_digests/2026-04-01_0113_donchian-overshoot-fade-threshold-alpha.md`
- action: 作为新的 fresh intake，只回答这条 `BTC 15m Donchian overshoot fade × 10bps breach threshold` 单币 overextension mean-reversion 在 repo 已给出的 `entry / exit / cost` 骨架与最小 public-data transfer path 下，是否已经形成值得保留的 raw alpha skeleton
- success_criterion: 必须给出明确 first verdict：`keep_P1 / P2 / P0`
- verdict: `keep_P1`（分配正式 `Rank 276`）

## 这一步实际回答的问题
只回答一个问题：

> 这条 BTC 单币 `15m` Donchian overshoot fade，在 repo 已给出明确 `entry / exit / cost` 规则、且最小 transfer path 仍停留在公开 kline 级数据时，是否已经足够诚实地保留到前排做 1 次 decisive follow-up？

## 本轮采用的最小证据
1. 已重读 digest：
   - `research/quant_digests/2026-04-01_0113_donchian-overshoot-fade-threshold-alpha.md`
2. 本轮只接受 digest 已经落下来的几条硬信息：
   - alpha 本体不是 breakout continuation，而是 **BTC `15m` 在穿出过去 `200` 根 Donchian 区间后做反手的 overextension fade / mean reversion**。
   - baseline（高波动 admission + 区间外侧直接反手）样本外仍为正：`OOS net PnL 9260.84 USD`，`OOS Sharpe 1.5113`，`36` 笔。
   - 在 baseline 上加 `10 bps breach threshold` 后，样本外进一步改善：`OOS net PnL 9872.83 USD`，`OOS Sharpe 1.6722`，`35` 笔，`win rate 62.86%`。
   - 再继续加更“精致”的双边 vol band 过滤后，样本外直接转负：`OOS net PnL -9406.37 USD`，`OOS Sharpe -2.2350`。
   - repo 内部失败对照也较清楚：`lead-lag` 基本不显著，`BTC-ETH pairs` 样本外被 `5 bps` 成本打穿；当前 repo 真正 surviving 的是 BTC 单币 overextension fade。
   - 策略骨架已经完整：
     - `entry`: `close < lower_band*(1-0.001)` 做多；`close > upper_band*(1+0.001)` 做空
     - `admission`: `rolling_vol(50) > in-sample 60th percentile`
     - `exit`: 反向极端信号或最多持有 `40` 根 `15m` bar
     - `cost`: repo 明确按每次仓位变化 `5 bps` 计费

## 为什么这一步不是 P0
这条线不能直接打回背景，因为它已经满足一个合格 fresh intake 至少该有的三件事：

1. **raw alpha 本体清楚**  
   这里不是把某个“高波动 breakout”标签误读成 alpha。真正活下来的，是 **极端偏离区间后的 snap-back / fade**，而不是 continuation。alpha 本体、admission、threshold 三层结构在 digest 里已经分得很清楚。

2. **策略骨架已经完整且可公开迁移**  
   `entry / exit / max hold / cost` 都已有具体规则；而且需要的数据只是 BTC `15m` 公开 klines 就能先做 faithful reproduction。它不是那种只剩故事、还没有 executable rule 的题。

3. **当前证据已经包含最起码的 after-cost 指向**  
   虽然这些结果仍来自 coursework repo，而不是我们自有复现 artifact，但它至少不是“样本内漂亮、样本外没提成本”的软判断。repo 已明确写了 `5 bps` 成本，且当前 surviving 版本在样本外仍是正的；这足以支持它进入前排做 1 次便宜但 decisive 的 follow-up。

## 为什么这一步也还不能直接升 P2
它现在还不够直接进 `P2 admission`，理由也很明确：

1. **当前 after-cost 证据仍只来自单一 coursework repo**  
   现在我们有的是 digest 对 repo 源码与表格的审读结论，不是 runtime 里已经落好的独立 reproduction artifact。还缺一次最小、自有、source-faithful 复现，来确认 `5 bps` 以上它不是 coursework 偶然物。

2. **transfer path 目前只证明“可复现”，还没证明“可迁移得足够诚实”**  
   digest 已说明 `15m` faithful reproduction 用公开数据能做，但向 desk 的 `5m / spot-vs-perp / maker-taker realism` 迁移还没做。它还没跨过“repo 幸存者”到“我们 runtime 下也成立”的那一步。

3. **目前还没回答唯一最关键的 follow-up 问题**  
   现在最该补的不是继续讲故事，而是直接检验：在 source-faithful `15m` 复现里，把成本从 `3 / 5 / 8 / 10 bps` 拉开后，这条线是否仍保留至少一个诚实的 after-cost pocket；如果 `5 bps` 以上就塌，那它不该走进 `P2`。

## 本轮 verdict
`BTC 15m Donchian overshoot fade × 10bps breach threshold` 已经形成一条足够清楚、可独立书写、且具备最小公开数据 transfer path 的单币 mean-reversion raw alpha skeleton；当前 digest 还给出了明确的样本外 `5 bps` 成本后正结果，因此它不该直接回 `background/P0`。但现阶段 runtime 里还没有我们自己的 source-faithful reproduction artifact，暂时不足以跳过 survivor 直接进入 `P2 admission`。

因此本轮给出：**`keep_P1`，并分配正式 `Rank 276`。**

## 对 runtime 的直接影响
- `Fresh intake slot`：更新为 `Rank 276 / BTC 15m Donchian overshoot fade × 10bps breach threshold`
- `Surviving candidate slot`：锁定为 `Rank 276`，保留唯一一次 follow-up 预算
- 不进入 `Active P2`
- 不回 `Background/P0`

## 下一步允许的唯一 survivor follow-up（供 bot2 排班时参考）
只允许做 **1 次最小 decisive follow-up**，并且必须直接回答下面这件事：

> 用公开 BTC `15m` 数据对 source 规则做一次 faithful reproduction，并显式拉开 `3 / 5 / 8 / 10 bps` 成本壳后，这条 `Donchian overshoot fade × 10bps threshold` 是否仍保留至少一个可诚实书写的 after-cost pocket？

如果这次 follow-up 发现 edge 只在 coursework 表格里成立、在最小自有 reproduction 下 `5 bps` 以上就明显塌掉，默认应结束 survivor 预算并回 `background/P0`；只有当 source-faithful reproduction 也显示 `5 bps` 左右仍站得住，才值得讨论是否升 `P2`。
