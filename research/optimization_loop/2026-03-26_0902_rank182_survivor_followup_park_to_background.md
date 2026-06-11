# Rank 182 survivor follow-up — park_to_background

- Time: 2026-03-26 09:02 UTC
- Target: `Rank 182 / lob-lgbm-quantile-timing-alpha`
- Verdict: `park_to_background`
- Slot transition:
  - `Surviving candidate -> Background pool`
  - `Surviving candidate slot -> none`

## What changed
`Rank 182 / lob-lgbm-quantile-timing-alpha` 的唯一 survivor follow-up 已诚实收口为 `park_to_background`：当前能看到的 `1m/3m` 事件驱动方向边只剩 `0.3~1.2 bps/event` 量级，连最轻的真实成本压力都很难穿过，因此不足以升入 `P2`。

## Evidence used
本轮没有扩题到新的秒级 replication，而是先用 intake 阶段已落地的本地 artifact 收口，因为 survivor follow-up 的问题本来就只是：

> 这条 `LOB probability edge + rolling-quantile trigger` 骨架，在 `persistence / threshold mode / cost stress` 下，是否还留下值得前排保留的净边？

读取的本地 artifact：
- `reports/artifacts/quant_digests/microstructure_lgbm_repo_probe_20260326/summary.csv`
- `reports/artifacts/quant_digests/microstructure_lgbm_repo_probe_20260326/persistence_summary.csv`

### 1) 非 persistence 的顶部 decile gross edge 太薄
`summary.csv` 里最好的 long-side gross 也只有：
- `ETHUSDT 1m` top decile: `+0.589 bps`
- `ETHUSDT 3m` top decile: `+0.533 bps`
- `ETHUSDT 5m` top decile: `+0.831 bps`
- `BTCUSDT 1m/3m/5m` top decile: `+0.14 ~ +0.20 bps`

这说明如果不用 persistence gate，只靠 rolling-quantile 极端区间，gross edge 量级本身就已经接近噪音；别说 `fee+0.5tick / fee+1tick`，连最轻的双边 fee 压力都不够诚实地穿过。

### 2) 2-bar persistence 能抬高 gross，但仍不够过成本
`persistence_summary.csv` 里最好的 pocket 是：
- `ETHUSDT 2bar_persist 1m`: `+1.213 bps`
- `ETHUSDT 2bar_persist 3m`: `+0.724 bps`
- `BTCUSDT 2bar_persist 3m`: `+0.482 bps`
- `BTCUSDT 2bar_persist 5m`: `+0.595 bps`

这证明 persistence gate 的确比单点极值更有用，但问题也很直接：**改善后的 gross 仍只有 `sub-1.5 bps/event`。**

若 survivor follow-up 的标准是至少回答 `fee / fee+0.5tick / fee+1tick` 三档成本压力，那么这组 gross 已经足以说明：
- 在 `fee` 档，绝大多数 pocket 就会被吃光；
- 在 `fee+0.5tick` 与 `fee+1tick` 档，几乎没有理由期待还能留下稳定净边；
- 因此不值得把它继续保留成前排 raw alpha，而更像是“有一点方向影子，但只能做 execution/conditioning 灵感”的背景对象。

### 3) 可迁移 pocket 不成立
本轮想保住 `Rank 182`，至少得看到某个相对可迁移的窄 pocket，例如：
- `BTC/ETH/SOL` 中至少两币同向成立；
- `30s/90s/180s` 某个 horizon 有明显厚度；
- 在最轻成本下仍有净边余量。

但现有 artifact 只显示：
- `ETH` 比 `BTC` 好一些；
- `2-bar persistence` 比单点极值好一些；
- 可是厚度仍远远不够支撑真实交易成本。

所以这更像“方向上有影子，但没有形成可迁移 pocket”，而不是一个能继续前排保留的 survivor。

## Why this is not a promote_P2
`P2` admission 至少要求对象有希望在更完整的 honesty / cost / stability 检查后活下来；但 `Rank 182` 连 survivor follow-up 阶段都已经暴露出核心问题：

- gross edge 本身太薄；
- 只有单币（ETH）稍微像样；
- persistence 虽有帮助，但只把它抬到仍然难过成本的水平；
- 因而没有必要继续消耗前排资源去做更重的 replication。

## Bottom line
`Rank 182 / lob-lgbm-quantile-timing-alpha` 保留下来的应只是一个背景层面的启发：**rolling-quantile governance + persistence gate** 可能适合未来微结构 execution/filtering 组件；但作为这次 intake 的 raw alpha 本体，它还不够厚，也不够诚实地穿过成本，因此本轮用完 survivor 预算后应直接 `park_to_background`。
