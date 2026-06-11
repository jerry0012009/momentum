# 2026-03-17 19:24 UTC · rank2 replay rounding budget ladder

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / Rank 2 replay preflight 邻接检查`
- 触发原因：
  - 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`
  - `Scout Seat` 这轮没有新的合格 `paper / repo based 5m / 15m crypto` fresh intake
  - 上一轮已经把 `Rank 2` 的 venue precision / minNotional 压成 `replay preflight snapshot`；若继续留在 `Run 3`，最值得补的紧邻一格不是 receipt wording，而是把 **qty rounding 损耗预算** 也说清

## 开始前检查
- repo 工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 当前 seat 读法：
  - `Paper Seat`：`EMA = running paper pilot / waiting_not_due`
  - `Live Seat`：默认空席
  - `Scout Seat`：本地 shortlist 已临时耗尽，当前诚实回退到 `Run 3`
- 当前唯一相关上游 artifact：
  - `reports/artifacts/alpha_closure_board/small_live_rank2_replay_preflight_snapshot_v1.csv`

## 本轮主点 + 紧邻子点
- **主点**：新增 `small_live_rank2_replay_rounding_budget_ladder_v1.csv`
- **紧邻子点**：同步一个 reader-facing 页面 `rank2_replay_rounding_budget_ladder.html`，并把 hard verdict 摘要挂回 `alpha_closure_board/report.html`

## 本轮做了什么
### 1) 把 preflight 再压一格：从“能下”改成“够不够干净”
上一轮的 preflight 只回答了：
- `ETH / SOL / BTC` 在 Binance 当前公开规则下能不能过 `minNotional / precision`

这一轮新增回答：
- 如果 operator 还关心 **qty rounding 损耗预算**，那每条 whitelist leg 至少该用多大的 test/no-fill 样例 notional？

具体做法：
- 复用上一轮已经冻结好的 `mark_price_usdt + step_size + 50U 样例 rounding 结果`
- 计算每条腿 `1 step` 对应的名义金额（`step_size * mark_price`）
- 反推出把 rounding 损耗压到 `<= 5 / 10 / 25 / 50 bps` 时所需的最小样例 notional

### 2) 当前 hard verdict
更诚实的结论不是“上一轮顺序完全不变”，而是：
- **如果只是问 venue 规则 pass/fail**：`ETH / SOL / BTC` 仍都能过最小预检
- **如果把 50U replay 样例的 rounding 损耗预算收紧到 `<=25bps`**：当前应临时读成 **`SOL -> ETH -> BTC`**
  - `SOL`：50U 实际 rounding 损耗约 `4.1760 bps`，已过 `<=25bps`
  - `ETH`：50U 实际 rounding 损耗约 `35.8174 bps`，要把预算压到 `<=25bps`，样例名义金额应提高到约 `100U`
  - `BTC`：50U 实际 rounding 损耗约 `127.7649 bps`；若真要做 BTC replay，至少应提高到约 `150U`（`<=50bps`）/ `300U`（`<=25bps`）

### 3) 这轮真正减少了什么 blocker
- 它没有伪装成已完成真实 replay
- 也没有偷偷重开 `Live Seat`
- 它减少的是 **operator 最容易误读的一层前置不确定性**：
  - `50U 能下` 不等于 `50U 也足够干净`
  - 若继续把 `ETH` 当首腿，至少该先知道：在更严格的 rounding 预算下，应该先提 notional，而不是继续沿用旧样例金额

## 交付物
### deployable artifact
- `reports/artifacts/alpha_closure_board/small_live_rank2_replay_rounding_budget_ladder_v1.csv`

### reader-facing 落点
- `reports/site/factors/alpha_closure_board/rank2_replay_rounding_budget_ladder.html`
- `reports/site/factors/alpha_closure_board/report.html`

### 最小 authoritative write-back
- `docs/TODO.md` 顶部 `Next 3 bot3 runs` 最新补充：写回这次 `50U != rounding-clean` 的 hard verdict

## 验证 / 证据
已验证：
- 新 CSV 已生成，含 `ETH / SOL / BTC` 三条记录与 `5/10/25/50bps` budget 梯子
- 新网页已生成，可直接 reader-facing 查看
- `alpha_closure_board/report.html` 已挂出摘要卡片
- `docs/TODO.md` 顶板已追加最新补充

## 风险 / 边界
- 本轮没有触发真实 venue route / ack / cancel
- 本轮没有把 `Rank 2` 升格成 `shadow parity passed` 或 `tiny-live ready`
- 这次结论只改变 **replay 样例金额 / rounding 预算** 的操作读法，不改变当前 `Live Seat = 暂空`

## Git
- 未提交
- 原因：repo 内仍有与本轮无关的既有脏文件 / 未跟踪文件，避免混提
