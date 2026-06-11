# 2026-03-17 19:16 UTC · rank2 replay preflight snapshot

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / Rank 2 replay preflight`
- 触发原因：
  - 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`
  - `Scout Seat` 本轮没有拿到更高边际价值的新 `paper / repo based 5m / 15m crypto` intake
  - 上一轮 `small_live evidence freshness board` 已明确指出：`Rank 2 receipt-chain audit` 是 tiny-live 侧最旧证据；若继续认领 Run 3，不该再空补同义卡，而应优先减少一次真实 replay 前的硬不确定性

## 开始前检查
- repo 状态：工作区仍有与本轮无关的既有脏文件 / 未跟踪文件；本轮只做 selective 写入，不混提
- 当前 seat 读法：
  - `Paper Seat`：`EMA = running paper pilot / waiting_not_due`
  - `Live Seat`：默认空席
  - `Scout Seat`：本地 shortlist 暂无明显高边际 value 的 fresh intake
- 当前 `Rank 2` 的唯一会改状态动作仍是：`1 次 whitelist-bound test/no-fill replay`；但当前环境里没有现成、安全、可确认的 venue replay 接口可直接落真实 receipt chain

## active Scout 候选边际价值比较（简）
- `Rank 17 / Rank 29`：都更接近 `P3 continuity / manual runner 托管`，今天继续认领只会消耗 continuity 预算，不会更快改变 desk judgment
- fresh intake：已按本地 shortlist 反复筛过，当前没有明显优于现有状态的新 `paper / repo based 5m / 15m crypto` 主点
- 因此按规则落到 `Run 3`；但这轮不再继续写 `receipt packet / starter row / status wording` 近义页，而是选择一个**真的会改变 replay 准备度判断**的最小检查：
  - 直接用 Binance 公共规则把 `ETH / SOL / BTC` 三条 whitelist leg 的 `tickSize / stepSize / minQty / minNotional` 压成当日 preflight 快照
  - 同时用 `50 USDT / test-no-fill` 样例计算 rounding 后的 `rounded_qty / rounded_notional / qty_rounding_loss_bps`

## 本轮主点 + 紧邻子点
- **主点**：新增 `small_live_rank2_replay_preflight_snapshot_v1.csv`
- **紧邻子点**：把同一 hard verdict 同步到 `alpha_closure_board` 网页

## 本轮做了什么
### 1) 新增 deployable artifact
新增：
- `reports/artifacts/alpha_closure_board/small_live_rank2_replay_preflight_snapshot_v1.csv`

字段包括：
- `mark_price_usdt`
- `tick_size / step_size / min_qty / min_notional_usdt`
- `sample_notional_usdt`
- `intended_qty / rounded_qty_down / rounded_notional_usdt`
- `qty_rounding_loss_bps`
- `min_notional_check`
- `replay_priority_verdict`
- `hard_read`

数据来源：
- Binance 公共 `exchangeInfo`
- Binance 公共 `ticker/price`

### 2) 本轮 hard verdict
当前没有证据支持把 ETH -> SOL -> BTC 改序；三条腿都能过 50 USDT test/no-fill 预检，ETH 继续是最干净首腿。

更细一点地看：
- `ETHUSDT`：`stepSize=0.0001`，`50 USDT` 样例下 rounding 损耗约 `5.2480 bps`，`rounded_notional≈49.973760 USDT`，通过 `minNotional`
- `SOLUSDT`：`stepSize=0.01`，`50 USDT` 样例下 rounding 损耗约 `12.1271 bps`，`rounded_notional≈49.939770 USDT`，通过 `minNotional`
- `BTCUSDT`：`stepSize=0.00001`，`50 USDT` 样例下 rounding 损耗约 `52.4780 bps`，`rounded_notional≈49.737737 USDT`，仍通过 `minNotional`，但作为首腿不如 `ETH / SOL` 干净

### 3) reader-facing 同步
- 已把 `Rank 2 replay venue preflight snapshot（v1）` 插入：
  - `reports/site/factors/alpha_closure_board/report.html`

网页公开口径：
- 这不是“已经 replay 成功”的伪装
- 这是一次真实减少 replay 前不确定性的 preflight snapshot
- 它回答的是：`ETH -> SOL -> BTC` 这个顺序在今天的 venue 规则下是否仍诚实可用

## 为什么这轮不是又一张同义小卡
- 之前 tiny-live 链里已经有：`ticket / runsheet / closeout matrix / freshness board`
- 真正还没被压成当日硬证据的，是 **venue precision / min_notional 到今天是否仍支持当前 replay 顺序**
- 这一步不会冒充真实 receipt chain，但它确实减少了 operator 在真 replay 前最容易 silently 出错的一层前置不确定性

## 验证 / 证据
已验证：
- 公共接口请求成功返回：
  - `https://api.binance.com/api/v3/exchangeInfo?...`
  - `https://api.binance.com/api/v3/ticker/price?...`
- 新 CSV 已写出并含 `ETH / SOL / BTC` 三条记录
- 网页已出现 `Rank 2 replay venue preflight snapshot（v1）`

## 交付物
### deployable artifact
- `reports/artifacts/alpha_closure_board/small_live_rank2_replay_preflight_snapshot_v1.csv`

### reader-facing 落点
- `reports/site/factors/alpha_closure_board/report.html`

## 风险 / 边界
- 本轮**没有**伪装成已完成真实 `test/no-fill replay`
- 本轮**没有**把 `Rank 2` 升格成 `shadow_parity` 或 `tiny-live ready`
- 本轮只回答：当真要做那唯一一次 whitelist-bound replay 时，当前 `ETH -> SOL -> BTC` 顺序在 venue 规则层面是否还站得住

## Git
- 未提交
- 原因：repo 内仍有与本轮无关的既有脏文件 / 未跟踪文件，避免混提
