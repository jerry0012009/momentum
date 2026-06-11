# Rank 163 survivor follow-up 收口 —— 不进入 Active P2

- 时间：2026-03-25 11:45 UTC
- 轮次角色：bot3 Active P2 执行
- 对象：`Rank 163 / Intraday TSMOM high-vol × low-liq pocket alpha`
- 来源：
  - `research/optimization_loop/2026-03-25_1126_rank163-itsm-pocket-intake.md`
  - `reports/artifacts/quant_digests/itsm_vol_liq_transfer_scan_20260325_1105/summary.json`
  - `reports/artifacts/quant_digests/itsm_pocket_transfer_probe_20260325_1058/summary.json`
  - `reports/artifacts/quant_digests/itsm_pocket_transfer_probe_20260325_1058/by_symbol_summary.csv`
- 本轮动作：判断它是否已具备“进入 Active P2 admission”的最低交易性门槛

## 本轮只回答一个问题
survivor 唯一 blocker 之前已经被收口成：

> 把 pocket 触发收缩成 `|ret_lb|` threshold，并按 `15m signal / 5m execution` + `4/8/12bps` 成本阶梯计价后，`post-cost avg bps/trigger` 是否仍稳定为正？

本轮先检查当前 runtime 已有证据是否已经足够给出 admission 方向。结论是：**已经足够回答“不够进 P2”**，不需要把它硬塞进 admission 再拖一轮。

## 现有证据为什么已经足够拦住 P2
### 1) alpha 本体不是零，但太薄
在 intake 里最好的公开 pocket 读数是：
- `15m, lookback=2, highvol_lowliq`：gross 约 `+1.04 bps/bar`
- `15m, lookback=1, highvol_lowliq`：gross 约 `+0.79 bps/bar`

这说明它不是“全天候都无效”；但也同时说明 edge 只有 **约 1 bps/bar 量级**，天然很怕真实成本。

### 2) 一旦按当前 pocket transfer / execution proxy 计入成本，整体直接翻负
`itsm_pocket_transfer_probe_20260325_1058/summary.json` 已给出更接近执行现实的 pooled 结果：
- `15m, lookback=2, gate_highvol_lowliq`：
  - gross `+0.05497 bps/bar`
  - `net4 = -0.19883 bps/bar`
  - `net8 = -0.45264 bps/bar`
- `15m, lookback=2, gate_highvol_lowerliq` 也同样：
  - gross `+0.00636 bps/bar`
  - `net4 = -0.52903 bps/bar`
  - `net8 = -1.06443 bps/bar`

翻成人话：**只要把这条线往更接近执行的口径挪一步，它留下来的不是“薄但可做”，而是“gross 几乎被吃光，成本后直接变负”。**

### 3) 跨币也没有留下一个足够硬的幸存 pocket
`by_symbol_summary.csv` 里，`15m, lookback=2, gate_highvol_lowliq` 六个币全部在 `net4` 下为负：
- BTC `-0.1872`
- ETH `-0.1112`
- SOL `-0.1466`
- BNB `-0.2243`
- XRP `-0.2721`
- ADA `-0.2516`  （单位：bps/bar）

也就是说，现阶段不是“整体还行，只差个别拖后腿币”，而是 **没有一个币在当前保守成本口径下留下足够硬的正净边际**。

## admission verdict
**本轮 verdict：不进入 `Active P2`，并把当前小点记为 `blocked`。**

原因不是 fatal flaw，也不是对象彻底归零，而是：
- 当前已有 evidence 已足够说明它**还没达到 admission front 的最低交易性门槛**；
- 若要继续，必须先拿到一个真正单一、决定性的 re-spec 版本（例如更稀疏的 `|ret_lb|` threshold pocket 或明显不同的 execution assumption）并证明它在成本后留下正值；
- 在那之前，把它写成 `Active P2` 只会制造开放式 admission 拖延，不符合当前 policy。

## runtime 变化
- `cycle_plan` 第 3 项（Active P2）记为 `blocked`
- `result` 写成：`Rank 163` 当前 pocket gross 只有约 `1 bps/bar` 量级，而更接近执行现实的 transfer probe 在 `15m signal / 5m execution proxy` 下已显示 `net4/net8` 全面为负，因此尚不具备进入 `Active P2` admission 的最低交易性门槛。
- `Surviving candidate slot.latest_blocked_record` 指向本记录
- `Active P2 slot` 继续保持 `none`

## 一句话结果
`Rank 163 / Intraday TSMOM high-vol × low-liq pocket alpha` 的 pocket gross 虽然为正，但在更接近执行现实的 `15m signal / 5m execution proxy` 与 `4/8bps` 成本口径下 pooled 与分币结果均转负，因此本轮不足以进入 `Active P2`，当前 admission 小点记为 `blocked`。
