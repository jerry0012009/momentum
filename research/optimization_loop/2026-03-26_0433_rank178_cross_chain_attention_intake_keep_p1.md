# Rank 178 / cross-chain attention spread alpha — fresh intake 首判（keep_P1）

- Time: 2026-03-26 04:33 UTC
- Target: `research/quant_digests/2026-03-26_0138_cross-chain-attention-spread-alpha.md`
- Slot before action: `Fresh intake slot`
- Verdict: `keep_P1` → 进入 `Surviving candidate slot`
- Assigned Rank: `178`

## 本轮只回答的一句话
`leader-chain attention shock -> long leader / short rival basket` 这条 cross-chain relative-value 骨架值得保留到 survivor，因为当前 digest 已经给出足够明确、可交易、且 desk 口径一致的最小证据；应保留的是 spread continuation，而不是把论文误读成 rivals 必然绝对下跌。

## 为什么这次首判是 keep_P1，而不是直接 park
1. **alpha 骨架清楚**
   - 不是泛泛“跨链有联动/有替代”，而是明确的交易骨架：
   - 当某条链代表币出现 `attention shock`（短窗收益冲击 + 放量 + 明显领先第二名）后，做 `long leader / short rival basket`。

2. **digest 已给出可执行 proxy，而不是纯学术叙事**
   - Universe 已压到 Binance USDⓈ-M 上可交易的 `ETH / SOL / BNB / AVAX / ARB`。
   - 事件定义、持有窗、对照组都已经写出来，不需要再先做大规模数据工程才能判断有没有前排价值。

3. **最小快检方向一致，且证明 alpha 更像 spread 而不是单腿裸空**
   - 全样本 `long leader / short rivals` 未来 `1h` spread 均值约 `+14.4 bps`，胜率约 `61.0%`。
   - 强 shock 条件下（`lead_z>=2.0, vol_ratio>=1.5, gap>=1.5%`）未来 `1h` spread 均值约 `+87.0 bps`，胜率约 `70.0%`。
   - 但 `short rivals only` 平均并不赚钱，说明应保留的是 **relative-value continuation** 这条骨架，而不是“negative spillover = rivals 会跌”这个误读。

## 为什么这次还不直接升 P2
- 当前证据仍主要来自 digest 内的 public-data quick check，尚未完成更诚实的 desk admission：
  - realistic net-cost / 多腿执行损耗
  - beta / market continuation 剥离
  - 3-leg 可交易压缩版是否仍成立
  - 时间稳定性 / 参数稳定性
- 因此它已经值得保留一次 survivor follow-up，但还没到直接进 `P2` 的地步。

## 对 runtime 的直接影响
- 新对象获得正式 durable identity：`Rank 178`
- `Fresh intake slot` 本轮首判完成
- `Surviving candidate slot` 切换为 `Rank 178 / cross-chain-attention-spread-alpha`
- 后续唯一合法 follow-up 应继续围绕：
  - `leader-chain attention shock -> long leader / short rival basket`
  - 重点验证这是不是扣成本后仍站得住的 spread，而不是被 beta continuation 伪装出来的单腿追强

## 单句结果（供 state / cycle_plan 回写）
`Rank 178 / cross-chain-attention-spread-alpha` 首判为 `keep_P1`：值得保留的是 `leader-chain attention shock -> long leader / short rival basket` 这条 cross-chain relative-value spread continuation 骨架，而不是把论文误读成 rivals 必然绝对下跌。
