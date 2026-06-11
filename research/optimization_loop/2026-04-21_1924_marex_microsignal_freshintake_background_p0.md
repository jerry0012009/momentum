# bot3 optimization loop — marex micro_signal fresh intake -> background/P0

- 时间：2026-04-21 19:24 UTC
- 执行对象：`research/quant_digests/2026-04-21_1842_marex-microsignal-maker-skew-alpha.md`
- 执行动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮只回答的 decisive blocker
`micro_signal fair-value shift × maker-first quote skew` 能否在当前可见的 `BTC/ETH/SOL` 盘口短漂移里，作为独立 `1m/3m child-execution alpha` 保住最小 after-cost pocket，而不是只剩几秒级 mid drift？

## 读取到的最小证据
来自 digest 已落库的 live probe artifact：
- `reports/artifacts/quant_digests/2026-04-21_marex_micro_signal_probe.py`
- `reports/artifacts/quant_digests/marex_micro_signal_live_summary_2026-04-21.csv`

核心口径：
- Binance USDⓈ-M `BTCUSDT / ETHUSDT / SOLUSDT`
- `top20 depth`、约 `1Hz`、总计约 `90s`
- 简化可迁移信号：`micro_signal_bps = clip(microprice_edge_bps + 2 * imbalance_l3, ±6)`
- 评估未来 `5s / 15s / 30s` signed mid return

## 关键读数
### BTCUSDT
- `|signal|>=1bp, pos`: `n=42`
  - signed fwd `5s/15s/30s ≈ +0.22 / +0.21 / +1.29 bps`
- `|signal|>=1bp, neg`: `n=7`
  - signed fwd `5s/15s/30s ≈ +0.77 / +0.72 / +3.51 bps`
- `corr(signal, next15s) ≈ 0.263`

### ETHUSDT
- `|signal|>=1bp, pos`: `n=15`
  - signed fwd `5s/15s/30s ≈ +0.21 / +0.04 / +1.53 bps`
- `|signal|>=1bp, neg`: `n=25`
  - signed fwd `5s/15s/30s ≈ +0.05 / +0.89 / +2.73 bps`
- `corr(signal, next15s) ≈ 0.175`

### SOLUSDT
- `|signal|>=1bp, pos`: `n=5`
  - signed fwd `5s/15s/30s ≈ +0.94 / +0.00 / +3.30 bps`
- `neg` 侧无样本
- `corr(signal, next15s) ≈ 0.162`

## 为什么这一步直接收口为 background/P0
1. **当前可见边际仍停留在“秒级 mid drift 存在”**，不是可独立承接的 after-cost alpha。最强可见 pocket 也只是 `30s` 方向性漂移大约 `1~3bps` 量级；这还没有覆盖 maker/taker 费率、排队落空、撤单重挂、adverse selection、以及 quote skew 带来的未成交概率损失。
2. **样本厚度不够回答“不是单次 live snapshot 噪声”**。整轮 probe 只有约 `90s`，而 `SOL >=1bp` 甚至只剩 `5` 个正侧样本、`0` 个负侧样本；这不足以支撑 `keep_P1`。
3. **repo 真正主张的 alpha 还依赖 OFI / trade-flow / VPIN / fast-vol 等事件级输入**，本轮 artifact 只复刻了 `microprice_edge + imbalance_l3` 的最小 proxy；在没有 websocket 级事件流与 maker-first friction ladder 之前，当前 reader-facing truth 仍只能是“有短漂移迹象”，还不是“保住了可复制 after-cost pocket”。
4. **按本轮 success criterion，不满足 keep_P1 条件**：没有任何一个标的在统一成本后被证明仍保留可复制短时 after-cost pocket，且现有证据本身也还停留在单次短 live snapshot。

## 系统认知更新
`marex micro_signal fair-value shift × maker-first quote skew` 当前只证明了 Binance perp top-book 上存在薄的秒级方向漂移迹象，但还没有证明它在统一成本、成交/排队 realism 下能独立保住可复制的 `1m/3m` after-cost pocket；因此本轮 fresh intake 直接收口 `background/P0`，不保留 survivor。

## 影响到的 runtime truth
- `Fresh intake slot` 本轮对象收口为 `background/P0`
- `cycle_plan` 第 1 项完成，状态改为 `done`
- `Background pool` 追加本轮 parked 结论与日志记录

## 尾部交付状态
- homepage index publish：尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，但命令在本轮 exec timeout 后被 `SIGKILL`；按 policy 视为非阻断尾部失败，不回滚 verdict / state / log。
- email summary：已发送到配置收件人。
