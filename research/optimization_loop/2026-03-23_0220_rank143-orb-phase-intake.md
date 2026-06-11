# 2026-03-23 02:20 UTC — Rank 143 / ORB phase retest state-machine + score gate source intake（fresh reserve admitted as active compare）

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / fresh intake reserve`
- 范围控制：仅 **1 个主点（fresh intake reserve）** + **1 个紧邻子点（对旧 P1 池做边际价值比较）**。

## 0. 先判 interrupt
先检查顶板要求的 interrupt：
- `Paper / 正在自动运行` 仍只有 `EMA / PSAR raw alpha focus`、`Rank 2 / 17 / 29 / 32b`、`Rank 139`、`Rank 122` 这些 autonomous runners；顶板本轮未写入新的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 证据
- `tiny-live / live-shadow plumbing` 也未见新的 blocking anomaly 落点

因此本轮 **不抢 interrupt**，继续按 `Next 3` 默认顺序执行。

## 1. 为什么这轮不回头磨 Rank 125 / 112 / 111
按当前顶板：
- `Rank 125 = P1 / keep_P1 / budget used`
- `Rank 112 = P1 / weak candidate / evidence_pool / budget used`
- `Rank 111 = P1 / evidence_pool / budget used`

结合最近留痕：
- `Rank 125` 的 clean replication、成本/交易数稳定性、aligned scorecard 都已经给过，当前结论稳定在 `keep_P1 / budget used`
- `Rank 112` 的主要问题仍是 `kept:veto` 极度失衡；若不重写 family，再补一刀边际极低
- `Rank 111` 虽 split 更平衡，但显式三臂与替代 strict arm 都已写出：**有点区分度，但仍不够稳**

结论：在 `125 / 112 / 111 / fresh intake reserve` 四选一里，**fresh reserve 仍是这轮最有杠杆的主点**。

## 2. 本轮认领的 fresh intake reserve
本轮选用：
- 原始证据：`research/quant_digests/2026-03-23_0205_orb-phase-retest-score-not-hard-gate.md`
- 新编号：**`Rank 143 / ORB phase retest state-machine + score gate`**

选它而不是继续回头磨旧 P1、也暂不选 `Donchian strength short admission` / `better-entry rearm` 的原因：
1. **直接回答当前最卡的角色问题**  
   - 它回答的不是“再补一个小过滤器”，而是：`Fib retest_hold` 到底该不该继续被写成独立 hard gate。  
   - 这比重复验证 `Rank 125 / 112 / 111` 的旧结论，更可能改变 desk 的表达与后续 clean replication 设计。
2. **能同时服务三条主线，但角色边界更诚实**  
   - `Fib retest_hold`：最直接，应该从“独立硬门”降回 `phase-quality layer`
   - `breakout-short`：可以借 `timeout / abort / bounce` 骨架修 follow-up，但不等于 shared yes/no gate
   - `EMA / PSAR`：提醒确认层更像 `score + state machine`，而不是继续幻想 raw trigger 自净
3. **比另外两条 reserve 更接近当前 desk 缺口**  
   - `Donchian strength` 更像 breakout-short 专项 admission score，shared 性不足  
   - `better-entry rearm` 更像 long-only loss-control thinning，救不了 raw alpha，也不适合作 fresh primary

## 3. Rank 143 的最小 intake verdict
### reader-facing 定义
**`Rank 143 / ORB phase retest state-machine + score gate`**
- 定位：`retest` 不再被当独立 hard gate，而是作为 **`breakout → retest → bounce + timeout/abort + score`** 的 phase-quality skeleton
- 第一落点：优先服务 `Fib retest_hold`
- 可借骨架：`breakout-short follow-up` 与 `EMA / PSAR confirmation`
- 当前层级：**`P1 / fresh intake / active compare admitted`**

### 本轮最小读法
- 它不是独立 alpha，不是 ORB session 策略照搬，也不是新的 shared hard filter；
- 它真正值得保留的是：
  1. `Phase 1`: breakout 已成立  
  2. `Phase 2`: retest 必须在有限等待窗内发生  
  3. `Phase 3`: 必须 bounce / reclaim 才放行  
  4. 若先越 invalidation boundary 或超时，直接 abort / timeout  
  5. 最后只加一个 cheap score，而不是继续堆硬门
- 因此它当前最诚实的身份是：**shared process skeleton 候选**，不是 shared trigger truth。

## 4. 轻量 scorecard（intake 版）
> 本轮不是 clean replication，只给 intake scorecard，供下轮 deciding cut 用。

- `usefulness`: **high** — 它直接改变当前 desk 对 `retest_hold` 的写法：从独立硬门，改回 phase-quality skeleton
- `time_stability`: **unknown** — 目前还是 repo intake，未做 desk clean-room OOS
- `cross_asset_stability`: **unknown** — 当前尚无 BTC/ETH/SOL 的正式 phase-state replication
- `cost_trade_stability`: **unknown** — 尚未补 `6/10/15bps` 成本层
- `deployability`: **medium** — 作为执行/确认 skeleton 很可部署；但离 paper 还差一轮诚实最小 replication
- `hard-fail flags`:
  - `repo_not_crypto_native`
  - `session_shell_not_transferable`
  - `score_double_count_risk`
  - `not_a_shared_hard_gate`
- `recommended_action = keep_P1`
- `why_now`: 旧 P1 的边际递减已经很明确；这条 fresh reserve 能最便宜地重写“确认层该扮演什么角色”
- `main_weakness`: 目前只有 repo 侧结构证据，没有 desk 自己的 `15m signal + 5m confirmation` clean replication

## 5. 对后续 run 的最小授权边界
若后续按顶板继续推进 `Run 2 / Run 3`，`Rank 143` 只允许吃 **1 次最小 clean replication**：
1. `A = 当前二元 retest_hold`
2. `B = phase state machine（breakout -> retest -> bounce + timeout/abort，不加 score）`
3. `C = phase state machine + score>=60`
4. `D = phase state machine + score>=70`

统一口径：
- `BTC / ETH / SOL`
- `15m signal + 5m confirmation`
- `next-bar open + no-overlap`
- `trade_count_retention`
- `continue / fail / timeout share`
- `post-cost expectancy`
- `12-bar / 24-bar invalidation ratio`

若 B/C/D 只是把 trade_count 大砍、timeout 大增，却没有更诚实的成本后改善，就直接 `park`；若能把“碰线就算 hold”的假确认压下去，才保留为 `keep_P1` 甚至考虑 `promote_P2`。

## 6. 本轮对 TODO 顶板的最小写回
本轮只做最小局部修改：
- 给 fresh reserve 正式分配 `Rank 143`
- 把它写进 `Active Scout 排序`
- 在 `Next 3 bot3 runs` 的比较集合里，用 `Rank 143` 替换模糊的 fresh reserve 指代
- 补 1 条最近关键 evidence

不改更大结构，不重写历史解释。
