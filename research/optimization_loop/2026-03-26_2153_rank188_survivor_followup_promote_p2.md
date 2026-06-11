# Rank 188 / extreme-only sparse top-k shock reversal skeleton — survivor follow-up promote_P2

- 时间：2026-03-26 21:53 UTC
- 对象：`Rank 188 / extreme-only sparse top-k shock reversal skeleton`
- 轮次角色：bot3 survivor 唯一 cheap decisive follow-up
- 结论：`promote_P2`

## 本轮只回答一个问题
把 repo 原始 `dense 15m + BTC gate` 映射已经判负之后，若只保留 **`extreme-only / sparse rebalance / top-k`** 这条唯一 re-scope，是否足以把 `Rank 188` 从 `P1` 推进到 `P2`。

## 最小 follow-up 做了什么
- 固定沿用前一轮的同一主题与同一 desk 口径：Binance perp `15m` 横截面 shock reversal。
- 不回头重开 repo headline combo；只测 survivor 允许的唯一窄轴：
  1. 只保留 cross-sectional shock reversal 本体；
  2. 只交易最极端的 `top-k` shock；
  3. 改成 **稀疏 rebalance**，不再逐 bar 重排；
  4. BTC gate 仍只当 crash veto，不当 alpha 本体。
- 复用本地 `365d` perp cache，截取最近约 `120d`；可对齐样本为 `11` 个主流 perp（`ETH/BNB/SOL/XRP/DOGE/ADA/AVAX/LINK/LTC/DOT/SUI`）+ `BTC` gate。`TRX/TAO` 当前本地 cache 不齐，因此这轮如实不纳入 cheap probe。

## 结果收口
相对前一轮被否掉的 dense 版本（`gross -0.296 ~ -0.409 bps/bar`，`turnover 6.28x ~ 11.04x/day`），这轮 survivor follow-up 给出了一条会改变系统认知的新信息：

- **`top-k=2`、`16-bar sparse rebalance`、BTC gate 版本转成 `gross +0.053 bps/bar`，Sharpe 约 `+1.57`，turnover 约 `1.54x/day`**；
- **`top-k=4`、`16-bar sparse rebalance` 结果几乎同向：`gross +0.054 bps/bar`，Sharpe 约 `+1.73`，turnover 同样约 `1.54x/day`**；
- 较快的 `8-bar` sparse 版本仍回到负值（约 `-0.08 bps/bar`），说明这条线的生存关键确实不是“更多触发”，而是 **足够稀疏的 turnover compression**。

按前轮统一成本口径（`2 bps/side`）粗算，`16-bar` 稀疏版的成本拖累约 `0.032 bps/bar`，因此净值空间虽然不大，但**已经不是 dense 版本那种明显死在高换手上的负 edge**。也就是说：

> `Rank 188` 的唯一 survivor 问题已经被回答成“是，turnover 压缩后存在诚实可交易 pocket”，所以它不该继续停在 `P1`，而应进入 `P2 admission`。

## 为什么这轮是 promote_P2，而不是继续 keep_P1 / 直接 park
- 这轮不是又补了一次同义重复，而是把 survivor 唯一允许的问题真正回答了：**dense 负值是否只是 turnover 杀死策略**。
- 现在答案已经变成：**是，至少在主流 perp 横截面 + 极端 top-k + 16-bar 稀疏调仓下，gross 已翻正且 turnover 明显压下来了。**
- 这足以证明 `extreme-only sparse top-k shock reversal skeleton` 不只是抽象概念，而是值得进入 admission 的对象。
- 但这还**不够直接升 P3**，因为当前还没系统回答：
  - 成本后净 edge 是否足够厚；
  - 跨资产稳定性是否只靠少数币；
  - 时间稳定性 / 参数稳定性是否过脆；
  - honesty / execution realism 在真实费率和更完整 universe 下是否仍站得住。

## 系统影响
- `Rank 188` 用完 survivor 唯一 follow-up 配额，不再停留在 `Surviving candidate slot`。
- `Rank 188` 进入 `Active P2 slot`，下一步应按 admission 维度收口，而不是回头重开原 repo headline 或继续开放式 `keep_P1`。
- 当前可保留的正式对象仍然只有一个：**`Rank 188 / extreme-only sparse top-k shock reversal skeleton`**。
