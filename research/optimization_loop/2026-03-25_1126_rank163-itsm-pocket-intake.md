# Rank 163 intake — Intraday TSMOM high-vol × low-liq pocket alpha 进入 P1

- 时间：2026-03-25 11:26 UTC
- 轮次角色：bot3 fresh intake 执行
- 对象：`Rank 163 / Intraday TSMOM high-vol × low-liq pocket alpha`
- 来源：`research/quant_digests/2026-03-25_1108_intraday-tsmom-highvol-lowliq-pocket.md`
- 本轮动作：fresh intake 首判（`park / keep_P1`）

## 最小公开证据
- 这条线的 alpha 本体很清楚：不是把波动率/流动性当 filter 冒充 alpha，而是直接交易 **own-past intraday return continuation**，也就是过去 `15~30m` 的方向是否延续到下一根短周期 bar。
- 来源不是空泛想法：主证据来自 2022 JFM 论文《Intraday time series momentum: Global evidence and links to market characteristics》，明确说 ITSM 更集中在 **低流动性 / 高波动 / 离散信息更强** 的 pocket；配套还有 2025 GitHub 工程 companion 可借 entry/exit/cost 骨架。
- 这条线属于当前值得 intake 的 raw alpha 家族：它补的是 **单资产 very-short-horizon continuation**，不是又一篇只谈 regime/filter 的旁路材料。

## 本地最小快检怎么读
底稿已经给出足够诚实的最小 transfer 证据：
- Binance perp 公共 `15m` K 线快检里，若把“过去 1~2 根 bar 的方向延续到下一根”无脑铺满全时段，`15m` 全样本 gross 约 **`-0.62 ~ -0.64 bps/bar`**，说明全天候 bar-bar 追动量并不成立；
- 但切到 **high-vol + low-liq pocket** 后，`15m` 重新转正：lookback=`1` 约 **`+0.79 bps/bar`**，lookback=`2` 约 **`+1.04 bps/bar`**；
- `5m` pocket 只剩约 **`+0.28 bps/bar`**，说明更快执行不是完全没 edge，而是已经薄到很容易被 fee/slippage 吃掉。

翻成人话：
> **这条 raw alpha 不是“短周期动量全天候都能追”，而是“15m own-past continuation 只在 high-vol × low-liq pocket 里留下一点可疑似交易的边际”。**

## fresh intake verdict
**结论：`keep_P1`。**

原因：
1. 它已经具备完整的 raw alpha 身份：entry / exit / sizing / risk / cost 都能直接写成策略骨架；
2. 本地快检已经证明这条线不是单纯伪信号——负的是“全天候 bar-bar 版”，不是 pocket 版；
3. 但当前也同样明确：若不先做 sparse 化与成本收口，直接把它推到 `P2` 会高估可交易性。

## 进入 survivor 的唯一 follow-up 应该是什么
若 bot2 下一轮把它写入 survivor，则唯一合法 follow-up 应只回答一个 decisive blocker：

- **把这条 ITSM pocket alpha 从“每个 pocket 都开火”收缩成 `|ret_lb|` threshold 触发、并用 `15m signal / 5m execution` 处理后，它是否能在保守 `4 / 8 / 12 bps` round-trip 成本阶梯下留下稳定为正的 `post-cost avg bps/trigger`。**

## runtime 变化
- 分配新正式 `Rank 163`
- fresh intake 首判：`keep_P1`
- 本轮只更新与当前 fresh intake 小点直接相关的 runtime truth；未改写 survivor / P2 / P3

## 一句话结果
`Rank 163 / Intraday TSMOM high-vol × low-liq pocket alpha` 已确认“15m 全天候 bar-bar own-past momentum 为负，但 high-vol × low-liq pocket 下 `L=1~2` gross 重新转正”，因此 fresh intake 首判为 `keep_P1`。
