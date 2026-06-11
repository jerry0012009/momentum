# 2026-03-16 15:08 UTC｜Scout Seat：Rank 4 crypto pairs stat-arb 完成最小 clean replication，并给出 `park` 硬结论

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- `Run 1 / Paper Seat`：`EMA` 当前处于真实 `waiting_not_due`，没有新的 `due-now / overdue` refresh。
- 因此本轮切到 `Run 2 / Scout Fast Lane`。
- 最近两轮已经把 `Rank 2` 收口成窄范围 `paper candidate`、把 `Rank 3` 补齐 Light Stability Pack 后压回 `park`；当前 `Next 3 bot3 runs` 剩下最自然的允许动作，就是把 `Rank 4 crypto pairs trading / stat-arb` 从 `source intake` 推到**最小 clean replication**，然后诚实给出 `paper candidate / one more light check / park` 三选一。

本轮只认领：
- **主点**：完成 `Rank 4` 的 `source intake -> clean replication`，检查最小 `trade on / trade off` 规则能否用现有历史样本诚实跑通。
- **紧邻子点**：把 verdict 同步到 reader-facing 页面与 `TODO` 顶部交易台指挥板，避免 desk 继续把它当作“仍待跑”的默认候选。

## 开始前检查
- `git status --short`：工作区存在大量与本轮无关的历史脏文件 / 未跟踪文件；本轮坚持 selective 改动，不混提。
- 最近 runs：
  - `2026-03-16_1355_scout-rank2-paper-candidate-admission-memo.md`
  - `2026-03-16_1423_scout-rank3-tradecount-time-stability.md`
  - `2026-03-16_1434_scout-rank3-parameter-stability-park.md`
- 当前席位：`Paper=EMA waiting_not_due`，`Live=暂空`，`Scout=默认主资源`。

## 本轮做了什么
1. 新增 `scripts/build_crypto_pairs_stat_arb_first_verdict.py`
   - 复用现有缓存：`reports/artifacts/scout_tau_band_breakout_15m/cache/*.csv`
   - 用 `BTC-USD / ETH-USD / SOL-USD` 三个币种组成三组高相关 pairs：
     - `BTC/ETH`
     - `ETH/SOL`
     - `BTC/SOL`
   - 冻结第一版 clean-room 规则：
     - 用样本前 `60%` 训练窗口冻结 `beta`
     - 用 frozen-beta 的 `spread z-score` 生成信号
     - `trade on`：前一根 bar 的 `z-score >= +2` 做 `short spread`；`<= -2` 做 `long spread`
     - `trade off`：前一根 bar 均值回归到 `±0.25` 内，或持有满 `32` bars
     - 执行价统一用**下一根 bar 的 open**，避免 lookahead
     - 成本统一按双腿 roundtrip `24bps` 记入
   - 生成 artifacts：
     - `reports/artifacts/scout_crypto_pairs_stat_arb_15m/clean_room_spec_v1.csv`
     - `reports/artifacts/scout_crypto_pairs_stat_arb_15m/pair_summary.csv`
     - `reports/artifacts/scout_crypto_pairs_stat_arb_15m/trades.csv`
     - `reports/artifacts/scout_crypto_pairs_stat_arb_15m/trial_meta.csv`
   - 生成 factor 页面：
     - `reports/site/factors/scout_crypto_pairs_stat_arb_15m/report.html`

2. 修改 `scripts/build_trendline_alpha_scout_report.py`
   - 新增 Rank 4 本地 clean replication 卡片；
   - 将 shortlist 中 Rank 4 的当前 desk role 改成“已完成最小 clean replication；若主要 pairs 整体偏负，则更诚实读法应是 `park / evidence pool`”；
   - 让 reader-facing scout 页面可以直接看到本轮结论，而不是只藏在日志里。

3. 最小同步更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
   - 把 `Rank 4 crypto pairs stat-arb` 从 `source intake / clean replication` 更新为 **`park`**；
   - 在 `Scout Seat` 候选阶段表中补上本轮 clean replication 的关键负结果；
   - 把 `Next 3 bot3 runs` 的默认顺序收紧为：`Rank 2 paper-candidate narrow scope -> tiny-live plumbing -> 其他维护 / 等 bot2 新点名`，避免 desk 继续误把 Rank 4 当作“下一轮默认要跑的未完成候选”。

## 最小验证
执行并通过：
1. `python3 -m py_compile scripts/build_crypto_pairs_stat_arb_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_crypto_pairs_stat_arb_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `grep` 校验网页落点：
   - `reports/site/factors/scout_crypto_pairs_stat_arb_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`

说明：本轮严格复用已有 15m crypto cache，没有重跑重型下载，也没有等待新 bar。

## 关键结果 / hard verdict
### Clean replication 是否跑通
- **跑通了**：规则、样本边界、执行口径、成本口径都已冻结成可复核的最小版本；
- `lookahead_guard = pass`
- `repaint_guard = pass`
- `source_intake_verdict = pass`
- `clean_replication_verdict = pass`

### 但 hard verdict 是什么
- **hard verdict：`park`**

### 证据
三组 pairs 的 frozen-beta `z-score spread` first pass 结果：
- `BTC/ETH`：
  - `trade_count = 83`
  - `win_rate ≈ 30.12%`
  - `cumulative_net_return ≈ -12.42%`
- `BTC/SOL`：
  - `trade_count = 117`
  - `win_rate ≈ 23.93%`
  - `cumulative_net_return ≈ -22.91%`
- `ETH/SOL`：
  - `trade_count = 127`
  - `win_rate ≈ 31.50%`
  - `cumulative_net_return ≈ -27.77%`

一句话结论：
- `Rank 4` 的**最小 clean replication 已经完成**，但它不是“差一点就能进下一步”的状态，而是 clean replication 本身已经在主要 pairs 上一起偏负；
- 因此当前更诚实的交易台读法应是 **`park / evidence pool`**，而不是继续默认投入 `Light Stability Pack` 资源，更不是偷升格成 `paper candidate pool`。

## 可部署 / reader-facing 落点
- 新 factor 页面：
  - `reports/site/factors/scout_crypto_pairs_stat_arb_15m/report.html`
- 更新 scout 汇总页：
  - `reports/site/reading/trendline_alpha_scout/report.html`
- 更新交易台顶板来源：
  - `docs/TODO.md`
- 发布后会同步到：
  - `reports/site/plans/momentum_todo.html`
  - `https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 本轮不是 formal cointegration 论文忠实复现；没有跑 Johansen / rolling beta / 更复杂的 pair-selection。
- 这不代表“pairs trading 方向永远无效”，只代表：**当前 desk 定义下的最小 frozen-beta z-score spread clean replication，不够硬，不值得继续占默认 Scout 主资源。**
- 如果后续 bot2 明确要求重开，最合理的重开方式应是：
  1. 换更贴近论文 / repo 的 calibration 细节；或
  2. 换 pair scope（而不是在这组三个 pairs 上继续磨 wording）。

## 下一步建议
1. `Scout Seat` 当前默认不再继续给 `Rank 4` 分配主资源；
2. 若 `Rank 2 combo_all` 没有新的最小诚实检查要补，下一轮默认直接转去 `tiny-live plumbing / parity / dry-run`；
3. 若 bot2 之后想再开新 scout 候选，应优先点名新的 `paper / repo based 5m/15m crypto` 候选，而不是回到已 park 的 Rank 1/3/4。

## Commit hash（基线）
- `76cea75`

## 如果未提交，原因
当前 worktree 有大量与本轮无关的脏文件与未跟踪文件；为避免混提，本轮只做 selective 构建、网页刷新、日志与邮件交付，不提交。
