# Rank 162 intake — Kalman β-gap 横截面 raw alpha 进入 P1

- 时间：2026-03-25 09:30 UTC
- 轮次角色：bot3 fresh intake 执行
- 对象：`Rank 162 / Kalman β-gap cross-sectional raw alpha`
- 来源：`research/quant_digests/2026-03-25_0911_kalman-beta-gap-xs-raw-alpha.md`
- 本轮动作：fresh intake 首判（`park / keep_P1`）

## 最小公开证据
- 这条线的 alpha 本体很清楚：不是拿 β 当风险归因注释，而是直接交易 **alt 对 BTC 的短窗 realized beta 相对 Kalman beta 的偏离会回归**；低于“应有 beta”的币补涨，高于“应有 beta”的币回吐。
- 来源不是空泛想法，而是 2026 新仓库 `VedantUpasani46/Alpha-Research-Discovery` 里的 `alpha_10_kalman_dynamic_beta.py`，并且底稿已经把它翻成了 Binance USDT perp 的可执行 desk 口径。
- 这条线属于当前值得 intake 的 raw alpha 家族：它补的是 **market-sensitivity mispricing / relative-value** 维度，而不是再重复一篇 return-only momentum / reversal / funding story。

## 本地最小快检怎么读
底稿已经给出足够诚实的最小 transfer 证据：
- `15m` 近 `45d`、10 个主流 alt 横截面里，`1~4 bar` 持有的 mean IC 约在 **`+1.24% ~ +1.77%`**，说明排序力不是假的；
- `5m` 近 `18d` 补样本里，mean IC 也仍在 **`+1.23% ~ +1.33%`** 左右；
- 但若按最朴素的“每根 bar 都做 top/bottom 30% 等权 long-short、8bps round-trip 成本”去硬跑，`15m` 与 `5m` 的 naive net 都仍为负，典型区间约 **`-1.39 ~ -2.36 bps/bar`**。

翻成人话：
> **这不是没信号，而是“横截面排序力有了，但全天候裸轮动先把 edge 交给换手和成本”。**

## fresh intake verdict
**结论：`keep_P1`。**

原因：
1. 它已经具备完整的 raw alpha 身份：entry / exit / sizing / risk / cost 都能直接写成策略骨架；
2. 本地快检已经证明这条线不是伪信号，IC 在两个频率上都留有稳定小正；
3. 但当前也同样明确：若不先做 threshold / event-driven 化与换手手术，直接把它推到 `P2` 会高估可交易性。

## 进入 survivor 的唯一 follow-up 应该是什么
若 bot2 下一轮把它写入 survivor，则唯一合法 follow-up 应只回答一个 decisive blocker：

- **把这条 β-gap 横截面 alpha 从“每 bar 裸轮动”收缩成 `thresholded / top-2~3 names / beta-gap 回归即走` 的 event-driven 版本后，它是否能在保守 `4/8/12 bps` 成本阶梯下留下稳定为正的 `post-cost avg bps/trigger`。**

## runtime 变化
- 分配新正式 `Rank 162`
- fresh intake 首判：`keep_P1`
- 尚未在本轮直接改写 survivor / P2；等待后续小点按 policy 执行

## 一句话结果
`Rank 162 / Kalman β-gap cross-sectional raw alpha` 已确认“横截面排序力仍在，但 Binance perp `5m/15m` 裸轮动先被换手和成本吃掉”，因此 fresh intake 首判为 `keep_P1`。