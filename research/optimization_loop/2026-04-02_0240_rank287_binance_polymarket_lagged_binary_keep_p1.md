# Rank 287 — Binance impulse × Polymarket 15m lagged binary mispricing 首判：keep_P1

- 时间：2026-04-02 02:40 UTC
- 对象：`research/quant_digests/2026-04-02_0117_binance-polymarket-lagged-binary-mispricing-alpha.md`
- 层级动作：`fresh intake -> keep_P1`
- 正式 Rank：`287`
- 结论一句话：这条 `Binance fast impulse -> Polymarket slow probability catch-up` 已经具备可独立审计的 cross-market raw alpha skeleton，因此值得保留为 `P1 survivor`；但当前证据仍主要来自 repo/source audit 与 live endpoint snapshot，尚未完成最小 clean-room lagged baseline，暂不直升 `P2`。

## 为什么这轮给 keep_P1，而不是直接回 background/P0
这条对象已经不只是题材叙事：

1. **错价本体清楚**：不是泛泛“RL 预测市场交易”，而是同资产 `Binance futures` 的快腿冲击先于 `Polymarket 15m binary` 的 quoted probability 调整；交易对象、错价定义、entry/exit 的方向都可直接写清。
2. **执行时钟硬**：15m crypto binary 自带 hard expiry，`time remaining`、near-expiry veto、timeout 都天然明确，比很多“慢腿可能什么时候回归”更可审计。
3. **公开取数路径已经打通**：digest 已经给出 Gamma API / CLOB websocket / Binance futures REST/stream 的公开数据路径，并验证 live snapshot 可拿；说明它不是只能停留在 repo PPT 里的黑箱故事。
4. **最小 transfer path 存在**：即使先不复刻 PPO，也能先用 `Binance features -> p_fair_up` 的 non-RL baseline 去测 `p_fair_up - p_mid_up` 的 edge decile / spread ratio / time-to-expiry 分桶，这是一条诚实的 first follow-up 路径。

## 为什么这轮还不能直升 P2
现在还缺的不是“再读一遍 repo”，而是最关键的 clean-room 生死线：

1. **尚未证明 post-cost pocket 真厚**：当前最醒目的数字来自 repo 自报的 paper results；而 binary venue 的 spread、fee、stale quote、near-expiry legging 风险都可能很快吃掉 edge。
2. **尚未做 lagged honest baseline**：还没看到独立的 one-sample-lag / one-tick-lag fair-value baseline 去证明慢腿确实系统性落后，而不是把 Binance 本身方向性 continuation 误读成 cross-market edge。
3. **容量与现实成交问题未回答**：15m binary 市场容量有限，且 repo 自身也承认 live 会有明显 performance degradation；在没做 clean-room edge/spread/latency 检查前，不够诚实直接进 `P2`。

## 本轮首判
- verdict: `keep_P1`
- rank: `287`
- 进入理由：已有可审计 raw alpha skeleton + 明确最小 follow-up 路径
- 不升 P2 的原因：还缺独立、滞后、扣成本的 clean-room baseline 证据

## 唯一 survivor follow-up 应该测什么
下一次若给这条对象 survivor 预算，唯一高杠杆问题应是：

**在公开可拿的 BTC/ETH/SOL/XRP 15m Polymarket crypto binary + Binance futures 数据上，做 one-lag honest fair-value baseline 后，`edge = p_fair_up - p_mid_up` 在 spread + fee + near-expiry veto 之后是否仍留下可执行净 pocket？**

如果答案是否定的，就应直接收口回 `background/P0`；如果答案肯定且 pocket 不是只活在极窄样本/单资产点状窗口，才值得进 `P2`。

## 对 runtime 的影响
- `Fresh intake slot`：本轮完成，正式记为 `Rank 287 keep_P1`
- `Surviving candidate slot`：应切换为 `Rank 287`，并保留 1 次 follow-up 预算
- 当前没有 `Active P2`
