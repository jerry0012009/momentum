# Rank 213 P2 admission parameter/time/honesty keep P2

- Time: 2026-03-28 08:11 UTC
- Target: `Rank 213 / large-cap XS momentum × short-leg jump veto`
- Action: 按 `P2 admission` 第一轮要求，对同一 `30` 币 liquid-perp universe 做最小但会改变层级认知的 `parameter + time + honesty` 收口；并排检查 `formation 64/96/128 × hold 8/12 × veto floor 1.5%/2.0% × median-mult 1.5/2.0`
- Verdict: `keep_P2`

## What changed
这轮 admission 解决的不是“它有没有任何 edge”这种粗问题，而是更关键的：**Rank 213 的 jump-veto 改善，到底是不是只在单一点参数和单一 pocket 里碰巧成立。**

新补的 artifact 显示，答案更接近：
- **不是单点参数幻觉**；
- 但**还没稳到可以直接升 `P3`**，因为当前优势明显偏后半段样本，时间稳定性还不够干净。

所以这轮最诚实的位置不是 `promote_P3`，也不是回退，而是：**`keep_P2`，并把剩余 blocker 收缩到“时间稳定性 / admission-ready deploy spec”这一个主问题。**

## Evidence used
新产物：`reports/artifacts/optimization_loop/rank213_p2_admission_20260328/summary.json` 与 `variant_timeseries.csv`

统一口径：
- 数据：Binance USDⓈ-M Futures 公共 `15m` klines
- 样本：`2026-02-09 10:15 UTC ~ 2026-03-28 07:00 UTC`
- universe：与上轮 widening follow-up 相同的 `30` 个 liquid USDT perp
- 组合骨架：`top-3 long / bottom-3 short` market-neutral
- 成本口径：`4 bps × turnover_x`
- 本轮 admission 小网格：
  - formation：`64 / 96 / 128` bars
  - holding：`8 / 12` bars
  - veto floor：`1.5% / 2.0%`
  - veto multiplier：`1.5x / 2.0x` cross-universe median max-up-bar

## Key findings
### 1) 参数稳定性：大多数网格都活，不像单点 lucky hit
- 总共 `24` 组 parameter/time 变体
- `jump veto` 成本后净均值为正：**`23 / 24` 组**
- `jump veto` 相对 plain 有净均值改善：**`19 / 24` 组**

这说明一个重要变化：

> **Rank 213 已经从“可能只是 widening pocket 里的一次漂亮结果”变成“在同一对象、同一 universe 上，换几个 formation / hold / veto 阈值后依然大体成立”的 P2 对象。**

换句话说，`jump veto` 对 short-leg jump concentration 的修复，不是只靠单个参数点撑着。

### 2) 参考主口径仍然成立，但时间稳定性不够干净
为了和前一轮 survivor follow-up 保持连续，这轮把 `f96_h8_floor150_mult2p0` 作为参考主口径。

它的结果：
- plain：
  - net mean @ `4bps`：`-0.75 bps/rebalance`
  - net cumulative @ `4bps`：`-11.36%`
- veto：
  - net mean @ `4bps`：`+2.15 bps/rebalance`
  - net cumulative @ `4bps`：`+6.49%`
- 相对改善：
  - `+2.90 bps/rebalance`
  - `+17.85%` net cumulative

但把样本硬切成前后半之后，问题也很明显：
- 前半段 veto：`-8.19 bps/rebalance`
- 后半段 veto：`+12.49 bps/rebalance`

翻成人话：

> **它不是已经“随便什么时候都能拿去 paper”那种成熟度；更像是最近这半段 regime 里很有戏，但前半段还不够稳。**

### 3) 更慢一点的持有窗口通常更像它的甜点区
在本轮网格里，比较亮眼的几组大多落在 `hold=12`，尤其是 multiplier=`2.0x` 的 veto：
- `f64_h12_floor150_mult2p0`：`+22.03 bps/rebalance`，净累计 `+113.47%`
- `f64_h12_floor200_mult2p0`：`+21.42 bps/rebalance`，净累计 `+108.64%`
- `f96_h12_floor200_mult2p0`：`+13.44 bps/rebalance`，净累计 `+55.53%`
- `f128_h12_floor150_mult2p0`：`+6.05 bps/rebalance`，净累计 `+16.94%`

这不是说已经可以拍板 `12 bars` 就是 deploy spec，而是说明：

> **这个对象现在更像“需要把持有期拉到 12 bars 左右、再围绕 2.0x veto multiplier 做 admission 收口”的方向，而不是继续停在抽象的 jump-veto 概念层。**

### 4) honesty / execution realism：改善不是靠假装低成本换来的
本轮口径把 turnover 明确扣到 `4 bps × turnover_x` 后，veto 仍然在绝大多数网格为正。
同时，veto 的结构性诊断继续改善：
- short-leg 最大单名损失显著低于 plain
- short-leg max-up-bar 明显被压下去
- top short contributor share 普遍下降

这说明它的改善仍然来自 paper 指向的**short 侧单名 jump concentration 被减轻**，而不是只是把收益从 gross 挪到表面上。

## Why this is keep_P2, not P3
虽然参数网格结果比预期强，但现在直接升 `P3` 仍然太早，原因只有一个主 blocker：

### 时间稳定性还没诚实收口
- 参考主口径在前后半样本的分裂仍明显；
- 这意味着当前优势仍可能是最近 regime 更适合，而不是 admission 已足够完整；
- 还没有一个明确冻结的 deploy-ready spec（例如 `hold=12` 是否正式替代 `hold=8`、veto 阈值是否固定 `2.0x`、资产准入是否仍用当前静态 `30` 币池）。

因此，当前更诚实的系统认知是：

> **Rank 213 已经证明“jump veto 不是参数幻觉”，但还没有证明“现在就值得直接 paper launch”。**

## Why this is not P2->P1 or background
也不该回退：
- 没有出现 fatal flaw；
- 没有出现只能靠 re-scope 才能活的证据；
- 相反，当前对象的主线 spec 更清晰了：**大 universe XS momentum + short-leg jump veto，优先看稍慢持有窗口与时间稳定性。**

所以这轮不该 `P2 -> P1`，更不该 drop。

## Runtime implication
- `Rank 213` 保持在 `Active P2 slot`
- `p2_consecutive_keep_p2` 应更新为 `1`
- `p2_rounds_since_level_change` 应更新为 `1`
- 最新 evidence axis 应切到 `p2_admission_parameter_time_honesty_grid`

## Result sentence
`Rank 213 / large-cap XS momentum × short-leg jump veto` 的首轮 `P2 admission` 已确认：在同一 `30` 币 liquid-perp universe 上，`24` 组 formation/hold/veto 网格里 `jump veto` 有 `23/24` 组成本后为正、`19/24` 组相对 plain 改善，说明它不是单点参数幻觉；但参考主口径前后半样本仍呈明显时段分裂，因此本轮最诚实结论是 `keep_P2`，暂不升 `P3`。
