# Rank 305 / HIP-3 oracle-premium percentile fade / survivor follow-up = background P0

- Time: 2026-04-03 09:58 UTC
- Actor: bot3
- Target: `Rank 305 / HIP-3 oracle-premium percentile fade × time-boxed exit`
- Source intake: `research/quant_digests/2026-04-03_0808_hip3-oracle-premium-percentile-fade.md`
- Follow-up type: survivor-only decisive check
- Verdict: `background/P0`

## Why this changes runtime truth
`Rank 305` 的 alpha 主语本身没有问题，但这轮 survivor follow-up 要回答的是：**我们能否用公开数据把它诚实地下沉成 `1m/3m/5m/15m` 的 clean replication，并证明净边来自分钟级 mark-vs-oracle premium 回归，而不是 repo 自带的小时级近似壳。**

本轮检查后，答案是否定的，因此它不能继续占用 survivor/front slot，必须收口到 `background/P0`。

## What was checked
1. 复读 intake / repo 证据：
   - `research/quant_digests/2026-04-03_0808_hip3-oracle-premium-percentile-fade.md`
   - `src/strategies/basis_reversion.py`
   - `research/run_hip3_analysis.py`
   - `src/data/hyperliquid.py`
2. 直接核 Hyperliquid 公共 API：
   - `fundingHistory` 的历史 `premium` 是否真能支持分钟级 clean replication
   - `candleSnapshot` 的 `1m` bar 是否自带 `mark/oracle/premium`

## Decisive findings
### 1) repo 的回测主证据其实是 **hourly premium history + forward fill**，不是分钟级 mark-vs-oracle clean replication
`run_hip3_analysis.py` 里拉的是：
- `get_candles(... interval="1h")`
- `get_funding_history(...)`
然后把 `funding[["fundingRate", "premium"]]` join 到 candles 上并 `ffill()`。

这意味着 repo 展示的 `Basis Dislocation Reversion` 表现，本质上依赖的是 **小时级 premium history**，不是它自己 narrative 里强调的 `95 秒 >400bps、19 分钟回到 <50bps` 的分钟级 pocket 复现。

### 2) Hyperliquid 公共 `1m` candles 不含 `mark/oracle/premium` 历史字段
实测 `candleSnapshot` 的 `1m` 返回键只有：
- `t, T, s, i, o, c, h, l, v, n`

也就是标准 OHLCV；**没有**历史 `mark_price / oracle_price / premium`。所以仅靠 repo 当前宣称的公开历史路径，我们没法把这条线诚实地下沉成 `1m/3m/5m/15m` 的 premium-fade clean replication。

### 3) survivor 任务要求的关键问题没被回答：分钟级 edge 是否独立存在、且跨资产稳定
这轮要验证的是：
- 成本后净边是否真的来自分钟级 `mark-vs-oracle premium` 回归；
- 是否能在 `BTC/ETH + 至少 1 个 HL 特色资产` 上复现；
- 是否不是 funding/basis 的慢收敛或 Hyperliquid 特殊数据近似造成的伪增量。

但当前能直接复核到的公开历史数据，只足以支持 **hourly approximation**；它不足以支撑 `1m/3m/5m/15m` 的诚实 admission，也不足以把 repo 的 microstructure 叙事和可复核证据闭环起来。

## Why this is not promote_P2
如果这轮能拿到分钟级历史 `mark/oracle/premium`，并在 `BTC/ETH + 1 个 HL 特色资产` 上看到成本后仍合理的 pocket，我会把它升到 `P2`。

但事实是：**repo 当前给出的最好证据仍停留在 hourly approximation，公开 API 现成历史口径也不能直接支撑分钟级 premium 回归 clean replication。** 在这种情况下继续保留前排，只会把“有意思的 microstructure 叙事”误当成“已经被我们自己干净复核过的分钟级 raw alpha”。

## Runtime consequence
- `Rank 305` 不再保留在 `Surviving candidate slot`
- 本轮 survivor follow-up 已用完，不再继续追加同主题检查
- 运行态应把它收口到 `Background pool`

## One-sentence result for state
`Rank 305`：公开可复核证据目前只支持 `hourly premium history + forward-fill` 的近似壳，不能诚实证明 `1m/3m/5m/15m` 分钟级 mark-vs-oracle premium fade 在 `BTC/ETH + HL 特色资产` 上独立成立，因此 survivor follow-up 收口为 `background/P0`。
