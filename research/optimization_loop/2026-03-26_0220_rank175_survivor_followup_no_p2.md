# Rank 175 / fomc-event-clock-veto-size-down-overlay — survivor follow-up 结论（不升 P2，退出前排）

- 时间：2026-03-26 02:20 UTC
- 对象：`Rank 175 / fomc-event-clock-veto-size-down-overlay`
- 结论：**survivor follow-up 完成；不升 P2，退出前排，转入 background pool**

## 这轮只回答一个问题
把这条 `scheduled FOMC release -> shared risk overlay / veto + size-down + re-arm` 接到现有 short-cycle 策略后，是否已经有足够证据证明：它能在**不明显伤害基线收益**的前提下，**稳定改善回撤、成交质量或尾部损失**，从而值得升入 `P2`？

回答：**没有。当前证据仍然只稳定证明“FOMC 事件窗确实存在且会放大波动/成交”，还没有证明“接入 overlay 后会形成稳定、可部署、跨策略可复用的净改善”。因此这轮必须诚实结束为不升 `P2`。**

## 这轮看到的证据
本轮复核的核心材料仍是 `2026-03-26_0106_fomc-event-clock-veto-size-down-overlay.md` 及其本地 probe：
- `summary.csv`
- `summary_15m.csv`
- `meta.json`

其中能稳定成立的只有两类事实：
1. **事件窗客观存在。** 最近 18 次 scheduled FOMC statement 上，BTC/ETH 在事件后 `1h` 与 `15m` 的绝对收益和成交额，普遍高于事件前窗口。
2. **冲击主要是 shared execution / volatility shock。** 这更像一个“公开时钟下的执行与风险管理问题”，不是独立方向 alpha。

可量化地说：
- `1h` 口径：BTC/ETH 的 `mean_post_quote_vol / mean_pre_quote_vol` 约 **3.34x / 3.14x**；
- `15m` 口径：BTC/ETH 的 `median_vol_ratio` 约 **3.09x / 3.29x**；
- 这足以支持“FOMC 前后不要按平时的 fill / sizing 假设交易”。

## 为什么这轮不能升 P2
### 1) 缺的不是事件存在性，而是 overlay A/B 的净改善证据
当前没有看到任何一版真正回答下面问题的 `with gate vs without gate` 结果：
- 哪类现有策略接了 gate？
- 改善的是净值回撤、尾部损失、还是成交质量？
- 这种改善是否抵消了少做交易带来的基线收益损失？

没有这一步，就还不能说它是 `P2 admission` 候选，只能说它是一个**值得记住的 event-risk 常识骨架**。

### 2) 证据还没有跨“服务对象”闭环
这条线声称可服务 breakout / momentum、MR、maker/taker execution 三类栈，但当前证据并没有展示：
- 对 trend breakout：减少了多少坏追单/坏 slippage；
- 对 mean reversion：减少了多少事件窗内被提前打掉的错误逆势单；
- 对 maker：quote widening / inventory cap 是否真实改善 adverse selection。

也就是说，**它有共享 overlay 的故事，但还没有共享 overlay 的落地收益账本**。

### 3) 这一步是 survivor 的唯一一次 follow-up，按 policy 应该收口而不是拖长
根据 policy，survivor 只允许一次 decisive follow-up。本轮 follow-up 后，系统认知没有升级到“可部署净改善已成立”，因此不能为了“方向上看起来合理”继续把它拖在前排。

## 更诚实的最终定位
**Rank 175 值得保留的，不是任何 FOMC 后方向交易或独立 alpha；而是一个“scheduled macro release 会系统性破坏短周期常态执行假设”的共享 event-risk overlay 骨架。**

这足以写进 background pool 的研究骨架，但**还不足以作为当前前排 `P2` 候选继续 admission**。

## 本轮改变的系统认知
**Rank 175 的唯一 survivor follow-up 已经完成：现有证据仍只证明 `FOMC event window exists`，未证明 `overlay integration delivers stable net improvement without materially harming baseline alpha`，因此不升 `P2`，并退出前排转入 background pool。**

## Runtime 落点
- `Surviving candidate slot`：清空
- `Active P2 slot`：保持 `none`
- `Background pool`：新增记录 `Rank 175`，保留其 `scheduled-event shared risk overlay` 研究骨架，禁止自动回前排
