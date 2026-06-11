# 2026-03-18 05:18 UTC — EMA-ADX-VOL skeleton source intake

## 为什么这次选这个
- 先按顶板重读 `Run 1 -> Run 2 -> Run 3`：
  - `Run 1 / EMA` 当前仍是 **`running paper / waiting_not_due`**，A 股下一次 close 仍在 `2026-03-18 07:00 UTC`，没有新的 `due-now / overdue` bar；
  - `Rank 46 / OI participation gate` 刚在允许预算内完成最小 clean replication，并已给出 **`park / evidence pool`** hard verdict；
  - `Rank 17 / 2 / 29 / 32b` 这些 `P3 narrow-paper lanes` 当前没有新的 status-changing append / review 需要 bot3 认领。
- 因此本轮默认落到 `Run 2 / Scout Fast Lane`，并且需要在当前 active 候选里重新比较边际价值。
- 这轮最诚实的主资源位是 **`Rank 47 / EMA-ADX-VOL skeleton`**：
  - 它仍是 fresh repo-based `15m crypto` source，直接服务当前 `EMA / PSAR raw alpha focus`；
  - 它当前高于 `Rank 35b`，因为后者只是 derived fallback；
  - 这轮只需要做两条轻量诚实守门，不必提前扩成 clean replication 或大研究包。

## 这轮做了什么
### 主点
- 把 `EMA-ADX-VOL-CRYPTO KILLER [15M]` 从 quant digest 线索推进到 **`source intake / honesty gate passed`**。
- 新增 artifact：
  - `reports/artifacts/literature/scout_repo_ema_adx_vol_skeleton_source_intake_card.csv`
  - `reports/site/reading/repo_scout/ema_adx_vol_skeleton_source_intake.html`

### 紧邻子点
- 最小改写 `docs/TODO.md` 顶部 authoritative board，补写 `2026-03-18 05:17 UTC` 的新状态：
  - `Rank 47 / EMA-ADX-VOL skeleton` 当前定位为 **`P1 weak candidate（source intake / 两条轻量诚实守门已过）`**；
  - 下一轮若 `EMA` 仍 `waiting_not_due`，默认只允许给它 **1 次最小 clean replication**；
  - 当前 `Next 3` 顺序收紧为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = EMA-ADX-VOL skeleton minimal clean replication`
    - `Run 3 = Rank 35b（若 fresh intake 再次失效） / tiny-live plumbing`

## 验证 / 证据
- 两条轻量诚实守门已冻结成可执行读法：
  1. **`trade on / trade off` 已可清楚写成规则**
     - `trade on`：只有当 `close` 与 `EMA 8/13/21/34/55` 同侧排齐、`DI+/DI-` 与方向一致且 `ADX > 20`、`volume` 超过短均值阈值、并且价格脱离 `period=15 / mult=2.6` 的 range filter 噪音带时，才允许开仓；
     - `trade off`：任一层失效则不交易；若后续发现只是靠重过滤把 trade count 压到失真，也应快速压回 `park`。
  2. **未见一眼可判死刑的 `lookahead / repaint / leakage`**
     - `EMA / ADX / volume SMA / range filter` 当前都是 trailing 计算；
     - 真正需要防的是工程实现过厚，因此下一轮 replication 必须统一冻结到 **`next-bar open + no-overlap`**，并把 `ADX / volume / range filter` 拆成分臂，避免把“强过滤换少交易”误写成 alpha。
- 最小文件存在性检查已通过：
  - `ok_csv = reports/artifacts/literature/scout_repo_ema_adx_vol_skeleton_source_intake_card.csv`
  - `ok_html = reports/site/reading/repo_scout/ema_adx_vol_skeleton_source_intake.html`
  - `ok_todo_writeback = docs/TODO.md`

## 当前硬结论
- **`EMA-ADX-VOL skeleton = guard-passed / admit_to_clean_replication_queue`**。
- 它当前不是已验证 alpha，只是从 digest 线索推进到了可执行队列。
- 下一轮最诚实的问题也已经冻结得很窄：
  - `ADX / volume / range filter` 三层里，哪一层单独最值钱？
  - 还是说 full stack 只是“强过滤换少交易”？

## 风险 / 边界
- 这轮没有重跑 clean replication；只是把 fresh repo intake 先过诚实守门。
- 原脚本把 entry、TP/SL 与工程执行混在一起，不能直接把 Pine 默认行为当成可部署证据。
- `volume > SMA × 阈值` 这类门槛很容易把 trade count 压到失真；下一轮必须优先看 `trade_count retention` 与 `false_start rate`，而不是只看收益数字。

## 下一步建议
1. 若下一轮 `EMA` 仍是 `waiting_not_due`，默认只给这条线 **1 次最小 clean replication**：
   - 固定 `BTC / ETH / SOL 15m` cache；
   - 统一 `next-bar open + no-overlap`；
   - 比较 `EMA_stack_only`、`+ADX_DI`、`+volume_gate`、`+range_filter`、`full_stack` 五臂。
2. 最先回答四个便宜问题：
   - `post_cost_return`
   - `trade_count`
   - `positive_asset_ratio`
   - `false_start_rate`
3. 若它成本后仍主要靠砍样本支撑，就快速压回 `park / evidence pool`；不要继续磨 source-intake wording。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，本轮不安全混提。
