# Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade — fresh intake keep_P1

## 本轮执行小点
- target: `research/quant_digests/2026-04-19_0112_cointegration-spreadfade-router-alpha.md`
- action: fresh intake 最小首判，只补双腿 `8/12/16/20bps` friction ladder 与 pair concentration 这一个最小 honesty / execution blocker
- verdict: `keep_P1`
- assigned_rank: `424`

## 结论
`cointegration-first pair admission × strongest residual z-score spread fade` 在当前 `15m strongest-only` portability probe 下，不是单一 pair 幻觉：虽然可交易 pocket 只集中在 `LINK/AVAX`、`LINK/LTC`、`SOL/LTC` 三组 mid-cap pair，但 strongest-router 的 `2h~3h` 持有窗在双腿 `8/12/16/20bps` 梯度下仍保住清楚 after-cost 净边，因此本轮作为新对象分配 `Rank 424` 并保留为 `keep_P1`，进入 survivor 唯一 follow-up 等待更严格 admission / break-risk 复核。

## 证据
### 1) strongest-only router 总体表现
来自 `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_router_15m.csv` 与 `..._summary.json`：
- `n=1528`
- gross mean bps:
  - `ret_4 = +8.13bps`
  - `ret_8 = +15.97bps`
  - `ret_12 = +23.69bps`

### 2) 双腿 friction ladder
按 strongest-only 每笔 round-trip 双腿总成本直接扣减：

- `4 bars (~1h)`
  - `net@8bps = +0.13bps`
  - `net@12bps = -3.87bps`
  - `net@16bps = -7.87bps`
  - `net@20bps = -11.87bps`
  - 说明 1h pocket 太薄，不能作为当前 front verdict 的核心依据。

- `8 bars (~2h)`
  - `net@8bps = +7.97bps`
  - `net@12bps = +3.97bps`
  - `net@16bps = -0.03bps`
  - `net@20bps = -4.03bps`
  - 说明 2h pocket 只在较低摩擦下成立，边际偏薄。

- `12 bars (~3h)`
  - `net@8bps = +15.69bps`
  - `net@12bps = +11.69bps`
  - `net@16bps = +7.69bps`
  - `net@20bps = +3.69bps`
  - 说明当前最像样的口袋明确在 `2h~3h`，尤其是 `3h` time-box 持有窗。

### 3) pair concentration 检查
edge 的确集中，但不是单一 pair 独撑：
- `LINKUSDT/AVAXUSDT`: `n=554` (`36.3%`)
  - `ret_12 gross=+18.38bps`, `net@20= -1.62bps`
- `LINKUSDT/LTCUSDT`: `n=516` (`33.8%`)
  - `ret_12 gross=+17.25bps`, `net@20= +1.25bps`
- `SOLUSDT/LTCUSDT`: `n=458` (`30.0%`)
  - `ret_12 gross=+37.38bps`, `net@20= +17.38bps`

解释：
- 这条线显然还不是广泛分散的 majors stat-arb；
- 但 strongest router 的 after-cost 价值并非完全由某一个 pair 单独虚撑；
- 当前更诚实的系统认知应是：**这是一个 mid-cap pair-cluster 驱动的 P1 候选，而不是已经能直接升 P2 的稳健 pair universe。**

## 为什么不是 background/P0
因为本轮要求回答的唯一 blocker 是「一压现实双腿 friction 后，是否还剩独立 after-cost alpha，且是否只是单一 pair 幻觉」。答案是：
- `1h` 不够；
- `2h` 勉强；
- `3h` strongest-only pocket 仍为正，且三组 pair 都有贡献；
- 因此没有被这一轮 honesty 检查直接打穿到 `background/P0`。

## 为什么还不能直接升 P2
尚未闭合的关键问题仍然存在：
1. 当前 admission 仍是 lightweight proxy，不是正式 Engle-Granger / ADF / rolling re-check；
2. pocket 明显偏 mid-cap pair cluster，break-risk / regime-break 容忍度还没测；
3. `5m child execution` 已经转负，说明不能把 execution 想得太快；
4. 还没回答 BTC 大波动 / funding 时钟 / 事件断裂时的 pair-break 风险。

所以本轮最诚实的层级是 `keep_P1`，而不是 `promote_P2`。

## 对 runtime 的影响
- 新对象分配正式 `Rank 424`
- `Fresh intake slot` 更新为 `Rank 424 / keep_P1`
- `Surviving candidate slot` 锁定为 `Rank 424`，保留唯一一次 follow-up 预算
- `Active P2 slot` 维持 `Rank 423`

## 尾部执行状态（非阻断）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步进程 `fresh-ocean` 最终 `SIGKILL` 失败（无 stdout），按 policy 记为非阻断尾部失败，不影响本轮 verdict/state/log 生效。
- 邮件通知：`send_text_email.py` 已成功发送（subject: `[momentum-bot3-auto] Rank 424 配对残差 fade 保留 P1`）。
