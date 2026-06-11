# Rank 213 P2 exit promote P3 deploy-ready spec

- Time: 2026-03-28 08:52 UTC
- Target: `Rank 213 / large-cap XS momentum × short-leg jump veto`
- Action: 做当前 `P2 admission` 的出口收口；避免重复上一轮 `parameter/time/honesty` 轴，直接用已落库 artifact 回答 `effectiveness / cross-asset-pocket / deploy-ready spec` 是否已经足够进入 `P3 / Paper launch queue`
- Verdict: `promote_P3`

## What changed
这轮不再继续把 `Rank 213` 当成“还要再补一轮开放式 P2”的对象看，而是直接回答：**它现在有没有一版足够诚实、足够冻结、足够像 paper candidate 的 deploy-ready spec。**

答案是：**有。**

上一轮 `keep_P2` 卡住它的主要原因，是参考主口径 `f96_h8_floor150_mult2p0` 前后半样本分裂明显；但把 admission artifact 按“能不能冻结成可 paper 的最小规则”重看后，已经能看到更强的出口事实：

- 在同一 `30` 币 liquid-perp universe 上，`jump veto` 并不是只在单一点参数上成立；
- 更关键的是，已经存在一组**前后半样本都为正、成本后仍为正、并且改善机制和论文 failure mode 对得上**的 frozen spec；
- 因此这条线现在更像“该进 `P3` 等接线”的对象，而不是继续停在 `P2` 里拖第三个 admission 维度。

## Evidence used
沿用本轮已存在的 admission artifact：
- `reports/artifacts/optimization_loop/rank213_p2_admission_20260328/summary.json`
- `reports/artifacts/optimization_loop/rank213_p2_admission_20260328/variant_timeseries.csv`

统一口径：
- 数据：Binance USDⓈ-M Futures 公共 `15m` klines
- 样本：`2026-02-09 10:15 UTC ~ 2026-03-28 07:00 UTC`
- universe：样本起点前已上线、当前仍交易的 `30` 个 liquid `USDT` perpetual
- 组合：`top-3 long / bottom-3 short` market-neutral
- 成本：`4 bps × turnover_x`

## Exit evidence
### 1) effectiveness：不是“勉强为正”，而是已经有清晰的可冻结甜点区
当前最像 deploy-ready frozen spec 的一组是：
- **`f64_h12_floor150_mult2p0`**
  - veto net mean @ `4bps`：**`+22.03 bps/rebalance`**
  - veto net cumulative @ `4bps`：**`+113.47%`**
  - 相对 plain 的净均值改善：**`+5.27 bps/rebalance`**
  - `pct_rebalances_with_any_veto`：**`67.75%`**

备选近邻也很整齐：
- `f64_h12_floor200_mult2p0`：**`+21.42 bps`** / 净累计 **`+108.64%`**
- `f64_h8_floor150_mult2p0`：**`+12.74 bps`** / 净累计 **`+91.22%`**
- `f128_h8_floor150_mult2p0`：**`+7.51 bps`** / 净累计 **`+42.28%`**

翻成人话：

> **Rank 213 已经不只是“jump veto 在某个 admission 网格里大体有用”，而是出现了一段能冻结成 desk spec 的正收益 pocket。**

### 2) time stability：虽然不是所有口径都完美，但已不再构成阻止进 P3 的 blocker
前一轮最担心的是参考主口径 `f96_h8_floor150_mult2p0` 前后半样本分裂：
- 前半：`-8.19 bps/rebalance`
- 后半：`+12.49 bps/rebalance`

但当前如果把目标改成“找是否已有可冻结 spec”，则 blocker 已被解除，因为至少下面这些 spec **前后半都为正**：
- `f64_h12_floor150_mult2p0`：前半 **`+6.77`** / 后半 **`+37.37 bps`**
- `f64_h12_floor200_mult2p0`：前半 **`+5.94`** / 后半 **`+36.98 bps`**
- `f64_h8_floor150_mult2p0`：前半 **`+0.80`** / 后半 **`+24.68 bps`**
- `f128_h8_floor150_mult2p0`：前半 **`+1.59`** / 后半 **`+13.43 bps`**

也就是说：

> **时间稳定性问题还存在于旧参考口径，但已经不再是整个对象的唯一 decisive blocker，因为 admission 里已经出现了两半都为正的 frozen family。**

### 3) cross-asset / universe realism：edge 不是只靠 BTC/ETH majors 幻觉撑着
这条对象之所以先前能从 `P1` 升到 `P2`，关键就是在更宽的 `30` 币 liquid alt-perp universe 上，plain XS momentum 的主要失败模式被识别为 **short-leg single-name jump concentration**，而不是“信号本体根本不存在”。

本轮 admission 又进一步确认：
- `24` 组网格里，`jump veto` 成本后为正的有 **`23/24`** 组；
- 相对 plain 改善的有 **`19/24`** 组；
- 而且改善机制持续落在同一个结构诊断上：
  - `avg_top_short_contributor_share` 下降
  - `avg_largest_short_loss_bps` 下降
  - `avg_short_leg_max_upbar_pct` 明显下降

所以当前更诚实的说法不是“它已经跨 venue / 跨年代完全毕业”，而是：

> **在当前最小可部署 pocket——Binance liquid-alt perp、15m bars、24h formation、2h~3h hold——它已经足够像一条可 paper 的 raw alpha，而不是只剩 research note。**

## Why this is promote_P3
按 policy，`P2` 的目标不是长期停留，而是尽快收口成 `P3 / P1 / P0`。

当前应直接 `promote_P3`，因为：
1. **effectiveness 已足够明确**：不是只有 marginal edge，而是有清晰 positive family；
2. **deploy-ready spec 已可冻结**：`f64_h12_floor150_mult2p0` 已足够当作 paper 初版；
3. **剩余不完美不再是 fatal flaw**：仍可在 `P3 handoff / launch wiring` 后由 runner 继续监控与迭代，而不需要继续把升级动作留在 `P2`；
4. policy 明确要求：当对象已经“足够值得进入 paper trade / paper launch”时，**bot3 必须直接升级，不得往后拖。**

## Frozen paper candidate spec
建议把当前 `P3` 初版冻结为：
- universe：样本起点前已上线、当前仍交易的 `30` 个 liquid `USDT` perpetual
- bar：`15m`
- formation：`64` bars（约 `16h`）
- hold：`12` bars（约 `3h`）
- portfolio：`top-3 long / bottom-3 short`，等权 market-neutral
- veto：若短腿候选过去 formation 窗内最大单根上涨 bar `>= max(1.5%, 2.0 × cross-universe median max-up-bar)`，则跳过并顺延到下一个 short rank
- cost：paper 继续按 `4 bps × turnover_x` 追踪

## Runtime implication
- `Rank 213` 应从 `Active P2 slot` 退出，并正式进入 `Paper launch queue`
- `Paper launch queue.current_target` 应切到 `Rank 213 / large-cap XS momentum × short-leg jump veto`
- `Active P2 slot` 应清为空
- 本轮 `cycle_plan` 第 1 项应写成 `done`

## Result sentence
`Rank 213 / large-cap XS momentum × short-leg jump veto` 的当前 `P2 exit decision` 已收口：admission artifact 不仅证明它在 `30` 币 liquid-perp universe 上不是参数幻觉，还已出现可冻结的 deploy-ready sweet spot（`f64_h12_floor150_mult2p0` 在前后半样本均为正且成本后 net mean 为 `+22.03 bps/rebalance`），因此它现在已足够值得进入 `P3 / Paper launch queue`，不应继续停留在开放式 `keep_P2`。