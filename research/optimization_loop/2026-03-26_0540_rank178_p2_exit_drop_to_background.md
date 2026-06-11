# Rank 178 / cross-chain-attention-spread-alpha — P2 exit 收口（drop_to_background）

- Time: 2026-03-26 05:40 UTC
- Target: `Rank 178 / cross-chain-attention-spread-alpha`
- Slot before action: `Active P2 slot`
- Verdict: `drop_to_background`

## 本轮只回答的一句话
`Rank 178` 当前这条进入 P2 的对象——`leader-chain attention shock -> long leader / short equal-weight rival basket` 的 **5-leg baseline**——在 intake artifact 上看起来很厚，但一旦按同步 Binance 公共数据 replay 到更接近执行的统一口径，未来 1h spread 只剩个位数 bps、扣保守多腿成本后转负，且在 BTC 相对平静窗口里同样不成立，因此这次 admission 应诚实收口为 `drop_to_background`，而不是继续把未锁死 spec 的毛边当成 paper-launch 候选。

## 这次 admission 真正回答了什么
这轮不是再补一个开放式 evidence axis，而是直接回答 `Rank 178` 作为当前 `Active P2` 是否已经足够进入 `P3 / paper launch queue`。

答案是否定的，原因不是“还差一点点文档”，而是 **当前被保留到 P2 的 baseline 本体没有通过更诚实的 spec lock / replay reconciliation**。

## 关键证据
### 1) intake artifact 的强 shock 结果很亮眼，但它本身不足以直接支撑 P3
来自 intake digest / event panel 的强 shock 版本（`lead_z >= 2.0`、`vol_ratio >= 1.5`、`lead_gap >= 1.5%`）：
- 事件数：`423`
- 未来 `1h` 的 `long leader / short equal-weight rivals` 平均 spread：`+87.01 bps`
- 胜率：`69.98%`

这说明 **raw idea 值得看**，但 P2 admission 关心的不是“idea 有没有故事”，而是 **当前 baseline 能不能在统一、诚实、接近执行的口径下站住**。

### 2) 一旦切到同步 replay 的统一执行口径，5-leg baseline 的边显著塌缩
`tmp_rank178_followup_metrics.txt` 给出的 replay 指标：
- `full_n = 428`
- `full_avg_spread = +9.21 bps`
- `full_win = 48.36%`
- `full_net30bps_avg = -20.79 bps`
- `full_net30bps_win = 38.55%`

也就是说，**5-leg baseline 的 gross edge 在 replay 口径下只剩个位数 bps，远不足以覆盖保守多腿 round-trip 成本。**

### 3) 不是“等市场平静一点就好”——BTC quiet 子样本同样不成立
同一份 replay：
- `full_quietbtc_n = 383`
- `full_quietbtc_avg = +4.79 bps`
- `full_quietbtc_net30bps = -25.21 bps`

这说明它的问题不只是“被 BTC beta 污染”；即使把 BTC 未来 1h 相对平静的窗口单独拿出来，**可执行的净边依然不够。**

### 4) 3-leg 压缩版也不能拿来救这次 admission
同一份 replay：
- `compressed_avg_spread3 = +10.58 bps`
- `compressed_net18bps_avg = -7.42 bps`
- `compressed_quietbtc_avg = +5.33 bps`
- `compressed_quietbtc_net18bps = -12.67 bps`

所以当前也不能把 `3-leg compression` 当成“其实已经成立，只是 5-leg 不方便执行”。**它同样没有在保守成本后留下可直接 paper trade 的净边。**

## 为什么这次不是 `keep_P2`
policy 已经写明：若 admission 的主问题已经能回答，就不该继续开放式拖在 `P2`。

这里不存在一个足够明确、且仍值得继续占用前排资源的“唯一剩余 blocker”。
因为当前 admission 看到的不是某个单独小洞（例如只差一个参数稳定性表），而是：
- `effectiveness / expected return`：统一 replay 后 gross edge 太薄；
- `honesty / execution realism`：扣保守多腿成本后转负；
- `cross-asset / time`：至少在当前 replay 样本里，没有显示出足够厚的稳健净边来支持继续前排推进。

换句话说，**主问题已经被回答成“不足以前排继续”**，不是“再补一轮也许就行”。

## 为什么这次也不是 `one-time P2->P1 re-scope`
`P2 -> P1` 只允许在存在**唯一明确 re-scope 方向**时使用。

本轮确实看到了局部口袋：
- `leader3 ARBUSDT` 的 compressed replay 平均约 `+31.96 bps` gross；
- `leader3 ETHUSDT` 也为正，但样本仅 `14` 次。

但这些都已经不是当前进入 P2 的那条 baseline：
- 原对象是 **`5-leg leader / equal-weight rivals baseline`**；
- 当前正值 pocket 更像 **特定 leader 子集 / 特定压缩版 / 更窄条件集**；
- 它们还没有被证明是同一条 alpha 的唯一明确 re-scope，而更像是**新的、范围更窄的候选假设**。

因此这次更诚实的处理不是勉强把它改写成一次 `P2->P1 re-scope`，而是：
- **当前 baseline 退出前排，回到 background**；
- 若后续要研究 `ARB-led compressed cross-chain spread` 之类更窄 pocket，应按新的/重开的对象重新 intake，而不是把这次 admission 失败伪装成“还在同一条线里轻微收窄”。

## 对 runtime 的直接影响
- `Active P2 slot`：清空为 `none`
- `Rank 178`：移入 `Background pool`
- 本轮明确被否定的是：
  - `leader-chain attention shock -> long leader / short equal-weight rival basket` 这条 **5-leg baseline** 已足够进入 paper launch
- 本轮没有被证明成立、因此不得顺手保留的是：
  - `3-leg rival basket compression` 已成立
  - `某个局部 leader 子 pocket` 足以作为同一对象的自动 re-scope

## 单句结果（供 state / cycle_plan 回写）
`Rank 178 / cross-chain-attention-spread-alpha` 的 P2 admission 已诚实收口为 `drop_to_background`：当前进入 admission 的 `5-leg leader-vs-rival attention spread baseline` 在统一 replay 与保守成本口径下不再保有足够净边，尚不足以进入 `P3 / paper launch queue`，且现有正值 pocket 更像新的窄对象而不是本次可直接沿用的一次性 re-scope。