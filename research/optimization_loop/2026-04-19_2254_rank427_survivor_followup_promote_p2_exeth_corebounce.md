# Rank 427 / high-volume selloff -> 5m bounce survivor follow-up promote P2

- 时间：2026-04-19 22:54 UTC
- 对象：`Rank 427 / high-volume selloff -> 5m bounce`
- 动作：survivor 唯一 follow-up
- 结论：`promote_P2`

## 本轮只回答的唯一 blocker
当对象从 `all-signals fixed-hold bounce sleeve` 收窄到更诚实的 `core bounce / ex-ETH / simple child-execution` 版本后，统一按 `8bps` 成本与最近月份切片，是否仍足够形成单一可承接的 after-cost pocket。

## 最小复核方法
复用现成 artifact：
- `reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_5m_panel.csv`

只看：
- `signal=1`
- `5m hold12`（约 1h 固定持有，作为最简单 child-execution 代理）
- 统一 `8bps` round-trip 成本

并只补 3 个最小 honesty 切片：
1. `ex-ETH`：检验 pocket 是否主要被 ETH 拖累；
2. `core bounce`：检验收窄到更可承接的核心池后是否仍成立；
3. `recent months`：检验最近月份口径下是否仍保留正的 after-cost 边际。

## 结果
### 1) 原 all-signals 基线
- all 8 币：`n=117`，`net8 mean ≈ +11.23bps`，`median ≈ +8.69bps`
- core4（BTC/ETH/SOL/BNB）：`n=55`，`net8 mean ≈ +7.78bps`，`median ≈ +1.69bps`
- core5（BTC/ETH/SOL/BNB/DOGE）：`n=70`，`net8 mean ≈ +14.03bps`，`median ≈ +9.44bps`

### 2) ex-ETH 切片
- ex-ETH / all remaining 7 币：`n=99`，`net8 mean ≈ +15.36bps`，`median ≈ +10.64bps`
- ex-ETH / core bounce sleeve（BTC/SOL/BNB/DOGE）：`n=52`，`net8 mean ≈ +22.86bps`，`median ≈ +15.01bps`

这说明前轮识别到的拖累点确实集中在 `ETH`；把对象诚实收窄成 `ex-ETH core bounce sleeve` 后，after-cost pocket 反而更清楚，而不是消失。

### 3) recent-month 切片
- ex-ETH / core bounce sleeve / `2026-04`：`n=50`，`net8 mean ≈ +24.20bps`
- ex-ETH / core bounce sleeve / `2026-03`：`n=2`，`net8 mean ≈ -10.48bps`

样本主体几乎都落在最近月份 `2026-04`，且 recent slice 仍明显为正；旧月只有极小样本，不能拿来要求它已经完成 time-stability 终审，但也不足以把当前 pocket 直接判死。

### 4) 非单币硬撑检查（ex-ETH / core bounce sleeve）
- `SOL`: `n=29`，`net8 mean ≈ +9.58bps`
- `DOGE`: `n=15`，`net8 mean ≈ +36.98bps`
- `BNB`: `n=5`，`net8 mean ≈ +61.85bps`
- `BTC`: `n=3`，`net8 mean ≈ +15.73bps`

虽然强度不均，但 pocket 不是只靠单一币孤立撑住；至少 `SOL + DOGE` 已提供了主要事件密度，`BNB/BTC` 作为次级正贡献。

### 5) strongest-only 反证
- router_top1 / all：`n=41`，`net8 mean ≈ -3.81bps`
- router_top1 / ex-ETH：`n=31`，`net8 mean ≈ -2.45bps`

因此对象的诚实定义应是 **`ex-ETH core bounce sleeve`**，而不是 `top1 shock router`。

## 本轮 verdict
`Rank 427` 的 survivor 唯一 follow-up 已回答唯一 blocker：当它被收窄成 **`ex-ETH core bounce / simple 5m hold12 child-execution sleeve`** 后，在统一 `8bps` 成本下 recent slice 仍保留清楚的 after-cost pocket，且不是单一币硬撑；因此它不该在 survivor 阶段被收口到 `background/P0`，而应直接 **升入 `Active P2`**，后续 admission 再系统回答 cross-asset / time / parameter / execution realism。

## 对 runtime 的影响
- `Rank 427`：`Surviving candidate -> Active P2`
- survivor 唯一 follow-up 预算用尽并收口
- `Active P2 slot` 切换为 `Rank 427 / ex-ETH core bounce sleeve`
- 下一轮若继续研究，应按 `P2 admission` 路径处理，而不是再做第二次 survivor follow-up
