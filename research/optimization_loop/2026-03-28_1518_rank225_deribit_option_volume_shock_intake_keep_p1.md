# Rank 225 / Deribit option volume shock × OTM directional gate：fresh intake keep_P1

- 时间：2026-03-28 15:18 UTC
- 对象：`research/quant_digests/2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`
- 轮次类型：bot3 auto optimization
- 结论：`keep_P1`
- Rank：`225`

## 这轮做了什么
按当前 `cycle_plan` 执行这条 fresh intake，回答它是否真能形成 `Deribit BTC option volume shock` 驱动的短周期 raw alpha，而不是只是一篇把 options flow 拿来解释 IV 的文献摘要。

## 本轮判断
结论是 **`keep_P1`**，但还不够直接升 `P2`。

原因分三层：
1. **这不是纯解释型 options-IV 论文。** 该对象已经把论文里最适合 desk 化的部分拆清楚：`volume shock` 是主 alpha，`OTM/DOTM short-dated call-vs-put directional pressure` 更像 direction gate / veto，而不是拿 aggregate NBP 直接冒充方向键。
2. **它已经具备可独立复现的最小策略骨架。** 目标市场（Deribit BTC options）、执行腿（BTC perp）、最小信号定义（`volshock_z / dir_z / volinfo_z`）、默认频率（`15m` / `5m`）、持有期（1 小时）和成本注意点都已写清；而且 Deribit 官方公开 API 允许 recent/live 逐笔抓取，不依赖私有 feed 才能起步。
3. **但当前证据仍停留在“论文成立 + 公共数据可抓”的 intake 层，不是 desk 口径下已验证的 after-cost edge。** 这轮还没有拿到 `recent/live` 的同口径实验，去正面回答：
   - `volume shock only` 是否在当前市场还留有净位移；
   - `+ dir_z` 与 `+ volinfo veto` 是否相对裸 `volume shock` 有独立净增益；
   - `15m` 是否真的优于更噪的 `5m`；
   - 在 perp fee + conservative slippage 后，净 alpha 是否仍足够厚。

所以它已经值得保留为前排候选，但证据还没到 `P2 admission` 那一层。

## 会改变系统认知的话
`Rank 225 / Deribit option volume shock × OTM directional gate` 不是一篇只能解释 IV 的 options microstructure 摘要，而是一条值得保留的 BTC 单币短周期 raw-alpha intake；但当前证据仍停留在论文与公共 API 可复现层，尚未完成 `recent/live`、成本后、相对 `volume-shock only` baseline 的最小 A/B，因此本轮只够 `keep_P1`，不直接升 `P2`。

## 为什么不是 promote_P2
`promote_P2` 需要的不是“paper 里曾经显著”，而是“在当前 desk 的可执行口径里，已经有足够明确的最小实证，值得进入更重的 admission 流程”。这条线目前还缺最关键的一步：
- 用 recent/live Deribit public trades 聚合出 `5m/15m` bar；
- 在同一成本口径下对照 `volume shock only`、`volume shock + directional gate`、`volume shock + directional gate + vol veto`；
- 明确 direction gate 是真增益，还是只是在 paper 叙事里更好听。

在这一步没做前，直接升 `P2` 会把“结构完整、可抓数”误当成“edge 已验证”。

## 唯一合法下一步（survivor）
若后续给它唯一一次 survivor follow-up，应该直接做一件事：
- 用 Deribit 公开 recent/live option trades + BTC perp 执行腿，按 `15m` 为主、`5m` 为辅，做最小 after-cost A/B：
  1. `volume shock only`
  2. `volume shock + dir_z`
  3. `volume shock + dir_z + volinfo veto`
- 输出至少包括：触发次数、平均净收益、long/short 分解、成本后均值、`15m vs 5m` 对比。

如果这一步不能证明 direction gate 相对裸 `volume shock` 留下独立净增益，这条线就应按预算做 `keep_P1 后转 background` 收口，而不是继续停留在“options flow 很有意思”的主题层。