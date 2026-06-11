# 2026-03-23 01:51 UTC — Rank 142 / hammer-engulf retest quality gate source intake（fresh reserve admitted as active compare）

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / fresh intake reserve`
- 范围控制：仅 **1 个主点（fresh intake reserve）** + **1 个紧邻子点（对旧 P1 池做边际价值比较）**。

## 0. 先判 interrupt
先检查顶板要求的 interrupt：
- `EMA / PSAR raw alpha focus` 的 autopilot status 文件存在，`updated_at_utc = 2026-03-23T01:45:02Z`
- `Rank 139` 仍被定义为 `independent hosted pilot runner`，但本轮未发现新的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 证据写回顶板
- `tiny-live / live-shadow plumbing` 也未见新的 blocking anomaly 落点

因此本轮 **不抢 interrupt**，继续按 `Next 3` 默认顺序执行。

## 1. 为什么这轮不回头磨 Rank 125 / 112 / 111
按当前顶板：
- `Rank 125 = P1 / keep_P1 / budget used`
- `Rank 112 = P1 / weak candidate / evidence_pool / budget used`
- `Rank 111 = P1 / evidence_pool / budget used`

结合最近留痕：
- `Rank 125` 最近已经补过 `cost_trade_stability` 与 `explicit three-arm family board`，当前读法已稳定在 `keep_P1 / canonical family reference`；再补近义检查，大概率只会重复“可读但不够强”。
- `Rank 112` 的主要问题不是还差一刀，而是 `kept:veto = 120:2` 太失衡；下一刀如果不重写 family 定义，就很难真改变 verdict。
- `Rank 111` 虽 split 更平衡，但最近结论也已稳定在 `有点区分度、仍不够稳`。

结论：在 `125 / 112 / 111 / fresh intake reserve` 四选一里，**fresh reserve 的边际信息增量更高**。

## 2. 本轮认领的 fresh intake reserve
本轮选用：
- 原始证据：`research/quant_digests/2026-03-23_0031_caizongxun-hammer-engulf-retest-asymmetric-gate.md`
- 新编号：**`Rank 142 / hammer-engulf retest quality gate`**

选它而不是另外两条最新 reserve（`Donchian strength short admission`、`better-entry rearm`）的原因：
1. **更贴当前 desk 的双主线**：
   - 能直接服务 `Fibonacci confirmation / retest_hold`
   - 也能作为 `EMA / PSAR` 的确认层，而不是硬去救 raw alpha
2. **非对称性清楚且可执行**：
   - `long` 侧有正 pocket：`base avg_pnl_r=+0.0319 -> pattern +0.0925`
   - `short` 侧基本没改善：说明它天然不是 shared gate，而是更窄的 long-side quality filter
3. **比另两条更不容易误升级成 shared truth**：
   - `Donchian strength` 很容易把人再次带回 breakout-short only 世界
   - `better-entry rearm` 更像 loss-control thinning，不足以当 fresh reserve 主点

## 3. Rank 142 的最小 intake verdict
### reader-facing 定义
**`Rank 142 / hammer-engulf retest quality gate`**
- 定位：`15m` 趋势中回踩确认后的 **long-side quality gate**
- 明确不做：`breakout-short` shared hard gate
- 当前层级：**`P1 / fresh intake / active compare admitted`**

### 本轮最小读法
- 它不是独立 alpha，也不是 shared follow-up 真理；
- 它最有希望的角色，是给 `Fib / EMA long retest` 做一个便宜确认层；
- 因为 `short` 侧未改善，下一刀若继续，必须坚持 **long-only / asymmetric**，不能偷渡成三线共享规则。

## 4. 轻量 scorecard（intake 版）
> 本轮不是 clean replication，只能给出 intake scorecard，供下轮 deciding cut 用。

- `usefulness`: **medium** — 能直接回答一个 desk 里反复出现的问题：哪些确认层只该给 long-retet 用，不该共享到 breakout-short。
- `time_stability`: **unknown** — 目前只有 `120d / 15m / proxy first-hit`。
- `cross_asset_stability`: **weak-medium** — BTC long 改善不明显，ETH/SOL 贡献更大。
- `cost_trade_stability`: **unknown** — 还没补 `6/10/15bps per side` 的正式成本层。
- `deployability`: **medium-low** — 适合做 confirmation layer，不适合直接上 paper。
- `hard-fail flags`:
  - `not_shared`
  - `short_side_negative`
  - `pattern_samples_sparse`
- `recommended_action = keep_P1`
- `why_now`: 旧的 `125/112/111` 已接近边际递减，这条能给 Scout 重新注入一个更贴近当前双主线的非共享确认候选。
- `main_weakness`: 仍只是 proxy pattern gate；样本稀疏，且 BTC long 改善不稳。

## 5. 对后续 run 的最小授权边界
若后续按顶板继续推进 `Run 2 / Run 3`，`Rank 142` 只允许吃 **1 次便宜诚实检查**：
1. `base_retest`
2. `base_retest + long_pattern_gate`
3. `base_retest + short_engulf_only`

统一口径应补：
- `15m signal + 5m execution 对照`
- `6 / 10 / 15 bps per side`
- `trade retention`
- `post-cost avg_pnl_r`

若 long-only 版本在成本后仍维持正 pocket，才有资格继续留在 active Scout；否则直接 `park`。

## 6. 本轮对 TODO 顶板的最小写回
本轮只做最小局部修改：
- 给 fresh reserve 正式分配 `Rank 142`
- 把它写进 `Active Scout 排序`
- 在 `Next 3 bot3 runs` 的比较集合中，用 `Rank 142` 替换模糊的 fresh reserve 指代
- 补 1 条最近关键 evidence

不改更大结构，不重写历史解释。
