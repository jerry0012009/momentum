# Rank intake log — fixed-threshold high-frequency pair spread MR
- Time: 2026-03-26 09:35 UTC
- Operator: bot3 auto loop
- Cycle item: `research/quant_digests/2026-03-26_0803_fixed-threshold-hf-pairs-spread-mr.md`
- Verdict: `park`

## Changed system cognition
`fixed-threshold high-frequency pair spread MR` 首判收口为 `park`：当前正值更像固定 universe + 长 timeout 支撑的局部 pairs pocket，尚未证明“fixed threshold 优于 dynamic threshold”这条对象本体在完整 4-leg cost、funding 与 method 对照下可独立成立，因此不进入 survivor。

## Why this changes the system view
1. 这条 intake 的可取之处不是泛泛的 pairs/cointegration，而是一个更具体的命题：`15m/5m` 高频层上 fixed threshold 是否比 dynamic threshold 更诚实、更能留下净边。
2. 现有本地 proxy 的确看到若干 post-cost 正值 pocket：
   - `15m` / `1.44σ`：15 笔，`net_total_bps ≈ +207.4`
   - `5m` / `1.65σ`：15 笔，`net_total_bps ≈ +262.9`
   - `5m` / `2.0σ`：13 笔，`net_total_bps ≈ +318.6`
3. 但这些 pocket 还不足以证明 intake 对象本体成立：
   - 论文证据目前仍是摘要级，不是全文 replication；
   - 本地只做了 `distance` proxy，尚未补 `cointegration / hybrid`；
   - 最关键的 `fixed vs dynamic threshold` 同口径 head-to-head 还没做；
   - `median hold` 基本贴着 `24h timeout`，说明收益更像“高频触发 + 长时间收敛”的特定结构，不是已经站稳的高频 MR 骨架；
   - 仍缺 `4-leg fee/slippage + funding` 的完整 honesty gate。
4. 在当前 survivor 仍被 `Rank 183` 占用的前提下，这条对象若没有更硬的一跳证据，不值得抢前排名额。

## Scope discipline
- 本轮只做最小首判，不扩写 full replication。
- 未触发 `keep_P1 / promote_P2 / promote_P3`，因此本轮无需分配新 `Rank`。
