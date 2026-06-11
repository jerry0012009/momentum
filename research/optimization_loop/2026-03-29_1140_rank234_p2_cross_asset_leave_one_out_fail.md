# Rank 234 / multiday MAX lottery XS continuation — P2 admission 首项（effectiveness / cross-asset）

- 时间：2026-03-29 11:40 UTC
- 执行角色：bot3
- 当前执行小点：`Rank 234 / multiday MAX lottery XS continuation`
- 动作：在统一 liquid USDT perp 口径下，对当前最强候选格优先 `24h formation × 4h holding`，并并排检查 `24h × 8h`，回答收益是否主要由少数币支撑、以及 leave-one-out / major-coin 口径下是否仍保留可交易的 long-short 净边。
- 产出 artifact：
  - `reports/artifacts/rank234_p2_cross_asset/summary.csv`
  - `reports/artifacts/rank234_p2_cross_asset/coin_contrib_summary.csv`
  - `reports/artifacts/rank234_p2_cross_asset/leave_one_out.csv`
  - `reports/artifacts/rank234_p2_cross_asset/detail_maxrank_24h_4h.csv`
  - `reports/artifacts/rank234_p2_cross_asset/detail_maxrank_24h_8h.csv`

## 本轮正式结论
**本轮结论：`Rank 234` 的 P2 admission 首项没有通过 cross-asset 收口；当前净边主要由单一小币 pocket（尤其 `SIRENUSDT`）支撑，离开该 pocket 后不再保留可交易的 long-short 净边，因此它现在更接近 `P1/P0`，还不能按“已具备 P3 主线”来写。**

这不是说整条对象立刻判死，而是说：
- 之前看到的 `24h × 4h`、`24h × 8h` 正净边，**并不是 major-coin / 广义 liquid universe 上都能站住的 continuation**；
- 当前更像是 **少数极端 lottery-style 小币持续贡献的窄 pocket**；
- 所以从 admission 角度看，这一轴给出的不是 `promote_P3` 信号，而是一个明确的负面约束：**若后续时间/参数/诚实口径也不能把它收回到稳定对象，就更应走 `P2 -> P1 re-scope` 或 `drop_to_background`。**

## 怎么做的
沿用上一轮 survivor follow-up 已落地的数据口径：
- 数据：Binance USDⓈ-M perpetual 公共 `1h` klines
- universe：上一轮已冻结的 top-24 liquid USDT perp universe
- 执行：`next-bar open`、`no-overlap`
- 成本：`5 bps/side`
- 本轮只检查 `MAX rank`
- 主看格子：`24h × 4h`；并排确认 `24h × 8h`

然后补两类 cross-asset honesty 检查：
1. **coin contribution 分解**：累计每个币在 long/short 两腿上对组合净 spread 的贡献；
2. **leave-one-out 重算**：每次排除 1 个 symbol 后，整条策略重新做完整横截面回测；
3. **major-coin 子宇宙**：只保留 `BTC/ETH/SOL/DOGE/XRP/BNB/ADA/LINK/BCH/DOT` 这组 desk 更容易接受的老币/主流币，再重算同口径结果。

## 关键结果

### 1) 原始 top-24 universe 的 headline 仍然是正的
上一轮的最强两格本轮复核一致：
- `24h × 4h`: `+34.42 bps/trade`
- `24h × 8h`: `+75.37 bps/trade`

所以 headline 本身没有因为复跑而消失。

### 2) 但收益集中度极高，几乎被 `SIRENUSDT` 一只币决定
`coin_contrib_summary.csv` 显示：

#### `24h × 4h`
- `SIRENUSDT`: `+9787.87 bps`，占全部绝对贡献的 **63.9%**
- 第二名 `PTBUSDT`: `+1461.06 bps`
- 其余大多数币种的净贡献都只剩几百 bps 量级

#### `24h × 8h`
- `SIRENUSDT`: `+10439.15 bps`，占全部绝对贡献的 **65.1%**
- 第二名 `PTBUSDT`: `+1154.82 bps`
- 主流币贡献普遍很小，更多像噪音而不是支柱

这说明当前净边不是“广泛的 MAX continuation”，而是**被单一小币 pocket 拉起来**。

### 3) leave-one-out 一旦去掉 `SIRENUSDT`，两格都从正变负
`leave_one_out.csv` 给出的最关键结果：

#### `24h × 4h`
- 全样本：`+34.42 bps/trade`
- 去掉 `SIRENUSDT`：**`-3.18 bps/trade`**

#### `24h × 8h`
- 全样本：`+75.37 bps/trade`
- 去掉 `SIRENUSDT`：**`-1.30 bps/trade`**

这已经足够改变层级判断：

> 当前看到的正净边并不是 leave-one-out 稳健的横截面现象；它对单个币 pocket 高度敏感，去掉头号贡献币后就不再可交易。

### 4) major-coin 子宇宙下，continuation 直接转负
只保留 `BTC/ETH/SOL/DOGE/XRP/BNB/ADA/LINK/BCH/DOT` 后：
- `24h × 4h`: **`-7.80 bps/trade`**
- `24h × 8h`: **`-9.87 bps/trade`**
- `72h × 4h`: `-12.01 bps/trade`
- `72h × 8h`: `-12.34 bps/trade`

这说明 `Rank 234` 目前**完全不能写成 major-coin continuation alpha**；它更像是“在含若干极端小币的 liquid-perp 宇宙里，偶尔由超强 pocket 支撑的 MAX lottery continuation”。

## 对 admission 的含义
按 P2 admission 的问题定义，本轮已经回答了最关键的一半：

- **effectiveness**：headline 在全 universe 里为正，但可交易性不具备广泛性；
- **cross-asset stability**：没有通过。收益不是分散在多资产上的，而是被 `SIRENUSDT` 这种单点 pocket 主导；
- **leave-one-out robustness**：没有通过。去掉头号币后即失效；
- **major-coin portability**：没有通过。主流币子集下全面转负。

因此，当前更诚实的系统认知应该是：

> `Rank 234` 虽然还有 headline 正净边，但它暂时不能被描述成“保留进入 P3 的 admission 主线”；相反，它已经暴露出一个会把它推向 `P1/P0` 的明确风险——alpha 主要是单币 pocket，而不是跨资产 continuation。

## 本轮不直接降级的原因
这只是 `P2 admission` 的第一项，还不是完整出口轮：
- 仍未完成 `time stability / parameter stability / honesty-execution realism` 的第二项收口；
- policy 明确要求 bot3 按 `cycle_plan` 逐个执行，而本轮只执行排在最前的这一小点；
- 所以本轮最诚实的 runtime 写回应是：**记录 `cross-asset` 这一轴未过，提升退出压力，但暂不在这一小点里单独改层级。**

如果下一项时间/参数/诚实口径也不能给出足够强的补救证据，那么 `Rank 234` 就不该继续开放式 `keep_P2`，而应尽快收口到：
- `one-time P2 -> P1 re-scope`（如果能明确重写成 small-cap pocket / specific universe 对象），或
- `drop_to_background`（如果连 re-scope 也不诚实）。

## 应写回 runtime 的一句话
`Rank 234 / multiday MAX lottery XS continuation` 在 liquid USDT perp 的 `24h × 4h / 8h` headline 虽仍为正，但净边主要由 `SIRENUSDT` 单币 pocket 支撑：leave-one-out 去掉该币后两格都转负，major-coin 子宇宙也全面转负，因此本轮 `effectiveness / cross-asset` admission 未过，当前更接近 `P1/P0` 而不是 `P3` 主线。

## 一句话 result
`Rank 234` 的 `24h × 4h / 8h` 正净边被 `SIRENUSDT` 单币 pocket 主导，去掉该币后两格均转负且主流币子宇宙全面失效，因此本轮 `effectiveness / cross-asset` admission 未过，层级判断已明显从 `P3` 倾向拉回到 `P1/P0` 风险侧。
