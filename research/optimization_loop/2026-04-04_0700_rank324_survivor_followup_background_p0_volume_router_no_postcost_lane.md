# Rank 324 — survivor follow-up — background/P0 on volume-router dual-book

- 时间：2026-04-04 07:00 UTC
- 对象：`Rank 324 / vol-z router × TSMOM / XS reversal dual-book`
- 轮次角色：bot3 自动执行
- 结论：`background/P0`

## 为什么这一步改变系统认知
`Rank 324` 的 first verdict 证明了它是一个讲得清楚的 **dual-book raw alpha 壳**，但 survivor 那唯一一次 follow-up 要回答的不是“故事顺不顺”，而是：在 `15m` 优先、`4 / 8 / 12 bps` 成本阶梯下，是否真存在至少一条诚实的 `vol-z` 路由 short-cycle lane。基于当前项目里唯一现成、可直接复用的 `120d / 15m` 三币 cache（`BTC/ETH/SOL`），本轮最小 clean-room 的答案是：**没有。**

更糟的是，问题不只是“router 没有带来增益”，而是 **router 本体、continuation-only、reversal-only 三条口径在成本后都没有留下可推广 pocket**。因此这条对象不该升 `P2`，也不值得继续占 survivor 资源；本轮应诚实收口为 `background/P0`。

## 本轮 clean-room 口径
脚本：`scripts/build_rank324_volume_router_survivor_followup.py`

样本与边界：
- 数据：`reports/artifacts/scout_tau_band_breakout_15m/cache/{BTC,ETH,SOL}USDT__120d__15m.csv`
- 频率：`15m`
- 资产：只有 `BTC / ETH / SOL` 三币；这不是全市场结论，但足够回答“是否已出现最小可推进 lane”
- 执行诚实性：信号在 bar `t` 计算，持仓统一 `shift(1)` 到 bar `t+1` 才生效；成本按 turnover 收单边 `4 / 8 / 12 bps`

规则翻译：
1. **Continuation book**：`mom_ret = close.pct_change(16 或 32)`，高量时按 `sign(mom_ret)` 顺势；
2. **XS reversal book**：`xs_ret = close.pct_change(16 或 32)` 后做三币横截面排序，低量时做 loser-long / winner-short；
3. **Router**：`vol_z = (rolling_mean(log(volume), 8) - rolling_mean(log(volume), 96)) / rolling_std(log(volume), 96)`；
   - `vol_z >= +0.5 / +1.0` 才允许 continuation
   - `vol_z <= -0.5 / -1.0` 才允许 reversal
   - 中间区间不交易
4. 每本书都做逐时点 gross 归一，避免把两本书叠成虚高杠杆。

## 关键结果
总表：`reports/artifacts/rank324_volume_router_followup/overall_summary.csv`

### 1) Router 没有留下成本后 pocket
最好的 router 版本也没过关：
- `router_hard_16_16_z10 @ 4bps`：
  - `positive_assets = 0/3`
  - `mean_total_return = -17.08%`
  - `mean_net_ret_bps = -0.158 bps/bar`
- 更宽松或更活跃的 router 只会更差：
  - `router_hard_16_16_z05 @ 4bps`：`mean_total_return = -39.11%`
  - `router_hard_16_32_z05 @ 4bps`：`mean_total_return = -33.82%`
  - `router_hard_32_16_z05 @ 4bps`：`mean_total_return = -42.27%`
- 到 `8 / 12 bps` 后全部进一步恶化，所有 router 版本都仍然是 `0/3` 正资产。

翻成人话：**volume z-score 并没有把 continuation / reversal 路由成一个能活下来的 short-cycle desk lane；它只是把两本原本就不强的书以更高 turnover 的方式拼在一起。**

### 2) 问题不只是 router，单书也没站住
- `continuation_only` 最好的口径是 `router_hard_16_16_z10 @ 4bps`：
  - `positive_assets = 1/3`
  - `mean_total_return = -2.18%`
  - `mean_net_ret_bps = -0.015 bps/bar`
- `reversal_only` 最好的口径是 `router_hard_16_16_z10 @ 4bps`：
  - `positive_assets = 0/3`
  - `mean_total_return = -15.26%`
  - `mean_net_ret_bps = -0.143 bps/bar`

也就是说，本轮不是“router 方向对了，只是混合方式还需再调”；更诚实的读法是：**在当前可用 short-cycle 样本里，continuation 和 low-volume XS reversal 这两本书本身都没有拿出足够强的 post-cost 基底。**

### 3) 高活跃 router 反而带来更差的换手
例如：
- `router_hard_16_16_z05`：`mean_trade_events ≈ 2387.7`，`mean_turnover ≈ 0.134`
- `router_hard_16_16_z10`：`mean_trade_events ≈ 1002.7`，`mean_turnover ≈ 0.059`

即使把阈值收紧到 `z10` 去降低切换次数，router 仍没有转正；阈值放宽只会把负收益和成本一起放大。

## 出口判断
按照 policy，这个 survivor 本轮必须收口，不能再拖第二次 follow-up。出口判断如下：

- **不是 `promote_P2`**：因为没有找到一条在 `15m` 与 `4 / 8 / 12 bps` 下仍保留成本后 pocket 的 router lane；
- **也不是新的 `keep_P1`**：survivor 预算只有这一次，本轮必须给出口；
- **因此应写成 `background/P0`**：保留它“volume 当 router 而非 confirmation”的结构启发，但不再把这条 repo 壳当成当前前排对象。

## 对 runtime 的直接影响
- `Surviving candidate slot`：`Rank 324` 用完唯一一次 decisive follow-up，本轮释放为 `none`
- `Background pool`：记录 `Rank 324` 已诚实收口，不得自动 reopen
- `Active P2 slot`：继续保持 `none`

## Result sentence
`Rank 324` 的 survivor follow-up 已完成：在当前唯一可复用的 `120d/15m` 三币 clean-room 中，`vol-z` 路由的 `TSMOM / XS reversal` 双书在 `4 / 8 / 12 bps` 下未找到任何成本后可推进 lane，且 router、continuation-only、reversal-only 三条口径都未形成最小 post-cost pocket；因此本轮正式收口为 `background/P0`，并释放 survivor 槽位。
