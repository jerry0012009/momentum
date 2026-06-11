# 2026-03-16 18:38 UTC｜Rank 4b clean replication：rolling-beta 窄重开通过，先给 `one_more_light_check`

## 为什么这次选这个
- 先按 `TRADING DESK BOARD` 检查：`EMA` 已是 `waiting_not_due`，所以本轮不能在 Paper Seat 空转，默认切到 `Scout Seat`。
- 当前 active Scout 候选里，`Rank 2 combo_all` 已被 board 明确降成「只做最小 paper wiring，不再继续 admission 文档打磨」；相比之下，`Rank 4b crypto stat-arb reframe` 还缺一个真正可审计的 **clean replication v2**，边际价值更高。
- 上一轮 `2026-03-16_1822_rank4b-reframe-sanity-scan.md` 只是 ad hoc sanity scan，不够作为正式 scout artifact；因此本轮主点固定为：把 `Rank 4b` 落成 **可复跑、可上网页的 clean replication v2**。

## 做了什么改动
1. 新增脚本：`scripts/build_crypto_pairs_stat_arb_rank4b_report.py`
   - 固定窄 reframe spec：
     - `rolling-beta z-score spread`
     - `ROLL_WINDOW = 192`
     - `entry_z = 2.5`
     - `exit_z = 0.0`
     - `max_hold = 32`
     - 不额外叠加 regime / vol gate（先看 model calibration 自己够不够）
   - 保留原 `Rank 4` 的同一数据范围：`BTC/ETH`、`ETH/SOL`、`BTC/SOL` 三组 `15m` crypto pairs。
   - 信号继续严格按 `prior-bar zscore -> next-bar open` 执行，避免 lookahead / repaint。

2. 生成新的 scout artifacts：
   - `reports/artifacts/scout_crypto_pairs_stat_arb_15m_rank4b/clean_room_spec_v2.csv`
   - `reports/artifacts/scout_crypto_pairs_stat_arb_15m_rank4b/pair_summary.csv`
   - `reports/artifacts/scout_crypto_pairs_stat_arb_15m_rank4b/trades.csv`
   - `reports/artifacts/scout_crypto_pairs_stat_arb_15m_rank4b/trial_meta.csv`
   - `reports/artifacts/scout_crypto_pairs_stat_arb_15m_rank4b/rank4_vs_rank4b_compare.csv`

3. 生成新的网页可见落点：
   - `reports/site/factors/scout_crypto_pairs_stat_arb_15m_rank4b/report.html`

## 验证 / 证据
已运行：
```bash
python3 scripts/build_crypto_pairs_stat_arb_rank4b_report.py
```

关键结果（`pair_summary.csv`）：
- `ETH/SOL`：`trade_count = 20`，`cumulative_net_return ≈ +2.28%` → `one_more_light_check`
- `BTC/SOL`：`trade_count = 15`，`cumulative_net_return ≈ +0.74%` → `one_more_light_check`
- `BTC/ETH`：`trade_count = 21`，`cumulative_net_return ≈ -6.99%` → `clean_replication_complete_but_negative`

与原 `Rank 4 frozen-beta` 对照后的更硬结论：
- 原版是 **三组全负**；
- 这次 `Rank 4b` 在统一窄 spec 下把 `ETH/SOL`、`BTC/SOL` 都抬回了**轻微正 pocket**；
- 但 `BTC/ETH` 仍明显为负，所以当前最诚实 verdict 只能是：
  - **`one_more_light_check`**
  - 还**不是** `paper candidate`
  - 更不是 `tiny-live` 候选

## 风险 / 边界
- 这轮只完成了 **clean replication v2**，还没有跑完整 `Light Stability Pack`。
- 当前正 pocket 仍然偏薄：
  - `ETH/SOL` 虽然为正，但也只约 `+2.28%`；
  - `BTC/SOL` 更薄，约 `+0.74%`；
  - 不能把这种 first-pass pocket 误读成稳健 alpha。
- 因为 repo 当前存在大量与本轮无关的脏文件，本轮不安全提交；避免把别人的在制品混进来。

## 硬结论（本轮 desk 口径）
- `Rank 4` 原 verdict 仍然是 `park`，**没有被推翻**。
- 但 `Rank 4b` 这个合法窄重开，已经从“原地全负”推进到：
  - **值得补下一刀轻量稳定性**
  - 当前最诚实位置：`one_more_light_check`
- 因此如果后续继续认领 `Rank 4b`，默认下一步应优先：
  1. 时间稳定性
  2. 成本 / 交易数稳定性
  3. 跨 pair 稳定性
- 只要这几刀里任一明显翻弱，就应更诚实地把 `Rank 4b` 压回 `park`，不要再硬撑成 `paper candidate`。

## 下一步建议
- 若下一轮仍在 `Scout Seat`，优先把 `Rank 4b` 补成最小 `Light Stability Pack`，不要回去继续写 `Rank 2` 的 near-duplicate closeout 文档。
- 默认先做：
  - `time stability`
  - 或 `cost / trade-count stability`
- 若这两刀都没把 `Rank 4b` 判死，再决定是否值得补 `cross-pair stability` 并争取进入更明确的 scout pool verdict。

## Commit hash
- 未提交。
- 原因：`git status` 显示 repo 内外存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合做安全 selective commit。
