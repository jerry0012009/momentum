# Rank 273 — survivor follow-up 收口：修正 `96 vs 672` / `288 vs 2016` lookback 后，edge 仍主要集中在单一 `ARB/CRV` shock-compression pocket，不足以升 `P2`，回 `background/P0`

- 时间：2026-03-31 22:30 UTC
- 对象：`Rank 273 / whitelist peer-divergence × half-life-gated spread fade`
- 执行类型：唯一 survivor follow-up（front-slot legal action）
- 来源：
  - `research/quant_digests/2026-03-31_2048_whitelist-peer-divergence-halflife-spread-fade.md`
  - `reports/artifacts/quant_digests/privateer_peer_pair_scan_15m_20260331.csv`
  - `reports/artifacts/quant_digests/privateer_arb_crv_signal_followthrough_15m_20260331.csv`
  - 本轮新增 `Binance USDⓈ-M 5m clean-room replication`（`2016` bar lookback，对应 `15m 672`）

## 结论
`Rank 273` 的唯一 survivor follow-up 已完成。修正 repo 的错误 lookback 口径后，这条 peer-bucket spread-fade 线仍能留下可读的 relative-value 结构，但 **可迁移的 after-cost pocket 仍主要集中在极少数 pair，且最像样的幸存者仍是单一 `ARB/CRV`，形态更接近低频 shock-compression，而不是足以支撑 admission 的多 pair、可扩展 `P2` alpha lane**。因此本轮最诚实 verdict 是：**用尽 survivor follow-up 后直接回 `background/P0`，不升 `P2`**。

## 这轮具体回答了什么
本轮只回答 state 里规定的那个问题：
- 在固定 peer buckets 下，修正 `96 vs 672`（以及对应 `5m` lookback）后，bucket 内 pair search、去重后 signal episodes、`first compression` vs `full reversion` 与 after-cost pocket 是否仍成立。

答案是：**成立的是“少数 pair 上的 thin shock-compression pocket”，不成立的是“足以让 Rank 273 进入 `P2` admission 的可迁移多-pair lane”。**

## 15m：`672-bar` clean-room 结果没有把对象推过 admission 门槛
现有 15m artifact 已足够说明修正 lookback 后并没有出现一组稳定、可扩展的 pair basket：

- 在 `672-bar` 口径下，当前满足 `corr >= 0.95` 且 `6 <= half_life <= 15` 的 pair 主要只有：
  - `ARB/CRV`
  - `ARB/LINK`
  - `LINK/CRV`
- 但当前 live z-score 都不高：
  - `LINK/CRV` 约 `0.98`
  - `ARB/CRV` 约 `0.66`
  - `ARB/LINK` 约 `0.52`
- rolling `672-bar` 窗口里，真正留下像样原始信号窗口的，仍主要是 `ARB/CRV`：
  - `ARB/CRV` gated windows = `298 / 829`（`35.9%`）
  - raw signal windows (`|z| >= 2.5`) = `34`
  - 去重后独立 episode = `5`
- `ARB/LINK` 虽也经常过 gate（`220 / 829`），但原始信号窗口只有 `3`
- `LINK/CRV` 当前 half-life 合格，但 raw signal windows = `0`

翻成人话：**修正到更像“1 周”的 15m lookback 后，确实不是完全没有东西，但幸存结构远称不上一个能稳定扩成 bucket 内多 pair 的 alpha lane。**

## 15m followthrough：更像 `first compression`，不是稳定 `full reversion`
现有 `ARB/CRV` followthrough artifact 显示：
- 5 个去重后的 signal episode 中，绝大多数能在未来 10 bars 内压回一截 spread；
- 但只有少数能在 15 bars 内真正回到 `|z| <= 0.5` 或翻过零轴。

这说明 15m 口径下最诚实的出场理解仍是：
- **可以把它读成 `shock -> first compression` pocket**；
- **不能把它读成稳定、广泛成立的 full-mean-reversion desk lane**。

## 本轮新增 5m clean-room replication：结论没有变强，反而更支持“单一幸存者 + 薄 pocket”
为避免只停在 15m，本轮按 state 指定补了对应 `5m` lookback：
- 频率：`5m`
- lookback：`2016` bars（对应 `15m 672` 的约 1 周长度）
- universe：与 digest 同一批 Binance perp proxy symbol
- gate：`corr >= 0.95` 且 `6 <= half_life <= 15`
- raw signal：`|z| >= 2.5`

### 5m 当前与 rolling 结果
最像样的 pair 依然集中在老那几个名字上，但 admission 结构没有扩展开：

1. `LINK/CRV`
   - current corr ≈ `0.966`
   - current half-life ≈ `9.80`
   - current z ≈ `0.97`
   - gated windows = `259 / 585`
   - raw signal windows = `0`

2. `ARB/CRV`
   - current corr ≈ `0.965`
   - current half-life ≈ `9.70`
   - current z ≈ `0.55`
   - gated windows = `258 / 585`
   - raw signal windows = `12`
   - 去重后独立 episodes = `2`

3. `UNI/CRV`
   - current half-life 已偏长（≈ `19.56`）
   - 虽有 `11` 个 raw signal windows，但不满足当前 gate，不能诚实算作主 admission 候选

也就是说：**把频率压到 5m、把 lookback 修正到对应的一周后，真正同时满足 gate 且又出现像样极端偏离的，仍主要只有 `ARB/CRV` 一组。**

### 5m `ARB/CRV` followthrough
本轮 5m clean-room 对 `ARB/CRV` 的两个去重后 episodes 看了未来 15 bars（75 分钟）：

- Episode 1：
  - entry z ≈ `-2.57`
  - 15 bars 内最佳 `abs(z)` 改善 ≈ `1.13`
  - 但 **未** 在 15 bars 内回到 `|z| <= 0.5` 或翻符号
- Episode 2：
  - entry z ≈ `-2.73`
  - 15 bars 内最佳 `abs(z)` 改善 ≈ `1.04`
  - 同样 **未** 在 15 bars 内回到 `|z| <= 0.5` 或翻符号

这和 15m 结论是一致的：
**5m 也更像先吃一段 compression，而不是稳定 full reversion。**

## 为什么这还不够升 `P2`
`P2` admission 需要的不是“存在一个还算有趣的 pair pocket”，而是更接近：
- 不依赖单一偶然 pair；
- 在 bucket 内至少有可迁移、可扩展的多 pair 结构；
- exit / hold / cost 口径能支撑更完整的 admission 讨论。

现在修正 lookback 后得到的更诚实画面是：
1. `96 vs 672` 的口径错误确实会显著改变 pair discovery；
2. 修正后并没有把对象强化成“bucket 内普遍成立”的 lane；
3. 15m 和 5m 都把核心幸存者收敛到 **单一 `ARB/CRV`**；
4. `LINK/CRV` 更多只是 gate 幸存，但缺乏极端偏离触发；
5. 真正看得见的 pocket 更接近 **低频 shock-compression**，还没证明经过真实成本后能作为独立 `P2` lane 存活。

因此，继续把它拖成开放式 `P2` 会违反当前 policy 对 survivor 的收口要求。

## 本轮改变系统认知的一句话
`Rank 273`：修正 `96 vs 672` / `288 vs 2016` lookback 后，peer-bucket spread fade 的幸存 edge 仍主要集中在单一 `ARB/CRV` 的 shock-compression pocket，缺乏足以支撑 bucket 内多 pair admission 的 after-cost 迁移证据，因此 survivor follow-up 用尽后应直接回 `background/P0`，不升 `P2`。

## runtime 写回要点
- `Surviving candidate slot` 清空（唯一 follow-up 已消耗）
- `Background pool.latest_parked` 更新为 `Rank 273`
- `cycle_plan[1]` 写成 `done`
- `cycle_plan[1].result` 写明：修正 lookback 后 edge 仍主要是单一 `ARB/CRV` thin pocket，故回 `background/P0`

## 备注
这不代表这条线“完全没价值”。更准确的说法是：
- 它像一个 **可记录的 relative-value pocket**，
- 但在当前证据下还不足以成为值得进入 `P2 admission` 的前排候选。

若未来用户明确要求 reopen，更像是以“单一 peer shock-compression micro-lane”重开，而不是继续拿“bucket 内可扩展 pairs lane”这个更大的叙事往前推。