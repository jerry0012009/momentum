# Rank pending fresh intake：IC-ranked coint basket spread fade first verdict = background / P0

- 时间：2026-04-08 17:33 UTC
- 对象：`research/quant_digests/2026-04-08_1646_ic-ranked-coint-basket-spread-fade-alpha.md`
- 槽位：Fresh intake
- 动作：fresh intake first verdict
- 结论：`background / P0`

## 为什么这轮直接收口
这条线有完整工程壳：`IC shortlist -> coint gate -> zscore entry/exit -> margin cap -> stop -> portfolio kill-switch`，所以它**不是空洞课程项目**，也确实说明 repo 作者在认真做可交易化包装。

但按 bot3 本轮要求，问题不是“壳是不是完整”，而是它是否已经压成一个**不会被现有 plain pairs / coint spread MR 家族吸收的独立 raw alpha 主语**。这里更诚实的答案是否定的。

## 改变系统认知的证据
1. **alpha 本体仍是老的 coint spread fade**  
   digest 自己给出的策略拆解，核心仍是：协整配对、rolling beta spread、`|z|>=2` 入场、回到 `|z|<=0.5` 平仓。新增部分主要集中在 shortlist / risk shell / kill-switch，而不是一个新的价格形成机制。

2. **repo 的“值钱部分”主要是 admission + execution shell，不是新的 queue-facing alpha 主语**  
   `IC shortlist + coint admission` 确实比裸相关性筛 pair 更像 desk 做法，但它更像“如何挑 pair、如何包风控”，不是和现有 plain-pairs / dual-test / engle-granger 家族并列的新 raw alpha 物种。

3. **public portability probe 没证明这层 shortlist/gate 已带来足够独立的 after-cost edge**  
   本地最小迁移记录显示：
   - 15m：`ETH/SOL` 毛 `+13.16 bps/笔`，`AAVE/UNI` 毛 `+14.69 bps/笔`
   - 但按四腿 taker roundtrip `16 bps` 扣后，分别只剩 `-2.84 / -1.31 bps/笔`
   - 5m 更差，`ETH/SOL` 只剩约 `-6.99 bps/笔`

   也就是说，本轮能确认的是：这类 pair 在 15m 仍可能有**毛 alpha**；但还**不能确认** `IC shortlist + coint gate` 这一层足以把它从“plain pairs baseline 加一层工程治理”提升成独立前排主题。

4. **当前素材池里已经有更直接的 pairs baseline 与 coint-family 主语**  
   现有 digest 里已经明确存在：
   - `2026-03-26_1505_plain-pairs-longshort-vs-longonly.md`：plain-vanilla pairs baseline
   - `2026-04-01_2105_dualtest-coint-zscore-pairs-alpha.md`
   - `2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`

   相比之下，这条 Cornell repo 目前更像**“pairs shell / admission implementation reference”**，而不是新的 queue-facing raw alpha。

## 诚实 verdict
- 不升 `keep_P1`
- 不分配新 Rank
- fresh intake first verdict 直接收口为：`background / P0`

## 一句话 result
这份 Cornell CFEM repo 证明了 `IC shortlist + coint admission + kill-switch` 能把 plain pairs 包成完整交易壳，但目前新增价值主要停留在 pair-admission / execution shell，未证明其 after-cost edge 足以脱离现有 plain pairs / coint spread MR 家族，故本轮 fresh intake 收口为 `background / P0`。
