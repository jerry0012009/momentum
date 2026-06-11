# Rank 260 / perp-perp funding diff × net-EV hurdle — fresh intake 首判（keep_P1）

- 时间：2026-03-30 20:28 UTC
- 执行者：bot3 auto 13m loop
- Source digest: `research/quant_digests/2026-03-30_1919_perp-perp-funding-diff-nethurdle-alpha.md`
- Object: `perp-perp funding diff × net-EV hurdle`
- Verdict: `keep_P1`
- Assigned rank: `Rank 260`

## 本轮回答的唯一问题
这条对象是否真的是区别于旧 `richest-venue routing` funding carry 的独立 raw alpha，还是只是把 funding 排名表换成 `net_ev` 包装后的旧题重写？

本轮结论是：**它是独立对象，但当前只够 `keep_P1`，不够直接升 `P2`。**

## 为什么它不是旧 `Rank 235` 的换皮
1. **主语已经变了。**
   `Rank 235` 的核心是“单边去 richest funding venue 收 carry，再用 hysteresis/min-hold 降 churn”；
   这条新对象的核心则是 **同一 underlier 的双 perp 对冲**：`short 高 funding venue + long 低 funding venue`，只在 `funding spread` 同时过 `z-score`、`net_ev`、`quote/depth` 这几道门后才开仓。

2. **收益来源也不同。**
   `Rank 235` 试图回答的是“venue routing 能不能把单边 carry 做厚”；
   新对象回答的是“同币跨 venue funding mispricing 是否大到足以覆盖双腿现实摩擦”。前者更像 richest-print routing，后者更像 market-neutral relative-value pocket。

3. **repo 给出的最小策略骨架已经独立成立。**
   digest 里明确有：
   - `entry`: `abs(funding_spread) >= min_funding_spread` 且 `abs(z) >= entry_z`
   - `exit`: `abs(z) < exit_z`
   - `max_hold`: 最多 `48h`
   - `cost stack`: `fees + slippage + latency + inventory_risk`
   这不是泛泛 funding 观察，而是已经具备最小可审计的 entry / exit / hold / sizing / cost 框架。

## 为什么本轮只能 keep_P1，不能直接升 P2
1. **当前 live sanity check 直接否掉了“always-on 收租机”叙事。**
   digest 里的公开三所快照已经很清楚：
   - BTC 最优 raw spread 仅 `0.6836 bps / 8h`
   - ETH 最优 raw spread 仅 `0.5923 bps / 8h`
   - 但默认成本栈下 breakeven 需要约 `23.5~27.5 bps / 8h`
   这意味着它不能被诚实写成“日常 funding diff 都能收租”的策略。

2. **现阶段证据还停在“结构成立 + 当前 snapshot 不过线”，缺少历史过线率。**
   要不要进 `P2`，至少还得知道：近一段历史里，到底有多少 funding window 真的能过 `net_ev > 0` 这道门；如果过线率极低，它就更像极端拥挤时的事件 pocket，而不是稳定 admission 候选。

3. **它现在更像一个值得保留的窄版 exact object。**
   当前最诚实的写法应是：
   > same-underlier perp-perp funding differential 只有在 `spread 过 z-score 门 + 过净边门 + 过 quote/depth 门` 时才值得开机；平常大部分 funding window 默认应视作 `NO_TRADE`。
   这足以保留为 `P1`，但还不够直接推到 `P2 admission`。

## 改变系统认知的一句话
**Rank 260 / perp-perp funding diff × net-EV hurdle 首判为 `keep_P1`：该对象不是旧 funding routing carry 的换皮，而是“同币双 perp 只在 funding spread 同时覆盖双腿完整成本栈时才开仓”的事件型 relative-value pocket；当前公开 live spread 远不足以支持 always-on 叙事。**

## 下一步（留给 survivor 唯一 follow-up）
只回答一个问题：

> 按 `BTC / ETH / SOL × Binance / Bybit / OKX` 回放近 12 个月 funding windows 后，真正满足 `z-score + net_ev > 0 + quote/depth veto` 的窗口占比到底有多高？

如果 over-hurdle window 只是极低频尾部事件，就应在 survivor 轮后诚实把它定格为“事件 pocket / background-ready”而不是继续往 `P2` 拉。 
