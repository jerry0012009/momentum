# Rank 228 / directional-change overshoot + abnormal-regime veto — fresh intake 首轮判分：keep_P1

- 时间：2026-03-28 19:00 UTC
- 对象：`research/quant_digests/2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`
- 新分配 Rank：`Rank 228`
- 本轮动作：fresh intake 首判
- 结论：**keep_P1**（进入 `Surviving candidate slot`，保留唯一一次 follow-up）

## 为什么这条 intake 够格保留到 P1

这条线通过首判，不是因为 paper headline 收益高，而是因为它已经像一条**独立、可执行、事件驱动**的 raw alpha 骨架，而不只是 breakout 包装：

1. **交易对象清楚**：不是 generic breakout，而是 `DC 上行确认 -> 吃 overshoot continuation -> 反向 DC / abnormal regime 退出`。
2. **事件时钟有独立价值**：它改变的不是某个 threshold，而是先换 sampling clock，再谈 continuation；这和 desk 里已有 fixed-bar 动量素材不是同一层东西。
3. **退出 / veto 机制完整**：`α·θ` 级别的反向确认和 `RDC -> HMM abnormal regime veto` 让它天然比“固定持有 N 根 bar”更接近可交易规则。
4. **cheap follow-up 路径明确**：可以直接在 `BTCUSDT / ETHUSDT` 的公开 `1m` 数据上做最小 bar-proxy DC 事件流，先回答这是不是 crypto 上也存在的独立 raw alpha，而不用先陷入重数据工程。

## 为什么现在还不能直接升 P2

当前证据还只够 `keep_P1`，不够 `P2`，原因也很明确：

1. **原始证据来自 FX，不是 crypto 原生样本**；
2. **论文 headline 明确是 long-only + 忽略 transaction cost**，还没有回答 crypto 上扣掉 `4~6 bps` 后是否仍有边；
3. **HMM veto 看起来有用，但仍可能只是 FX 样本里的 regime overfit**；
4. **目前还没有 BTC/ETH 的最小 clean replication**，因此不能直接把它当成 admission-ready 候选。

## 与已有旧对象的边界

它和旧的 `Rank 111 / abnormal-return event clock`、以及文中提到的 `DC first-hit follow-up gate` 不是同一对象：

- `Rank 111` 更像事件窗口/过滤层；
- `DC first-hit follow-up gate` 更像 breakout verdict / confirm 层；
- **`Rank 228` 留下的是完整 raw alpha：event-trigger overshoot capture + abnormal-regime veto。**

所以这次给 `keep_P1` 是诚实的：它值得占用一次 survivor 预算，但还没到可以越级升 `P2` 的程度。

## 唯一一次 follow-up 应该回答什么

下一次如果继续推进，唯一值得做的不是再补 paper wording，而是直接回答：

> 在 `BTCUSDT / ETHUSDT` 的 public `1m` bar-proxy DC 事件流上，`DC-confirmed overshoot continuation` 在加入 `α·θ` 反向确认退出后，是否能留下至少一个扣掉 `4~6 bps` 后仍不塌的 pocket；`abnormal regime veto` 是否真能降低 tail loss，而不是只是在样本内美化 equity curve。

若这一步答不出成本后 pocket，就应按预算写成 `keep_P1 后转 background`；若能留下明确 pocket，再升 `P2`。

## 本轮 writeback

- `Rank 228 / directional-change overshoot + abnormal-regime veto`：**keep_P1**
- 槽位迁移：`Fresh intake slot -> Surviving candidate slot`
- 下一手合法动作：唯一一次 `BTC/ETH 1m bar-proxy DC event-flow` follow-up

## 一句话结果

`directional-change overshoot + abnormal-regime veto` 已通过 fresh intake 首判并获得 `Rank 228`：它保留的是一条值得做一次 `BTC/ETH 1m` bar-proxy DC 事件流验证的 event-driven raw alpha，而不是普通 breakout filter；但当前证据仍停在 FX、long-only、无成本口径，所以本轮只到 `keep_P1`，不直接升 `P2`。
