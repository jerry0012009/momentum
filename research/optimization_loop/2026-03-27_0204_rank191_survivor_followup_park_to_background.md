# Rank 191 survivor follow-up — park to background

- 时间：2026-03-27 02:04 UTC
- 对象：`Rank 191 / loser-bucket low-anchor relative-value reversal`
- 本轮动作：执行 survivor 唯一一次 cheap decisive follow-up
- 结论：`park_to_background`

## 这轮只回答一个问题
在 Binance 风格主流可交易 universe 的 `15m` 主时钟下，loser bucket 内的 `low_gap` 二次排序，是否在**显式成本后**仍提供独立于 plain loser reversal 的残余 alpha。

## 执行口径
这轮故意只做最小但诚实的 cross-sectional proxy，不扩写成整套 anchoring 家族：

- 数据源：Binance USDⓈ-M public `15m` klines
- universe 版本 A：近 24h quote volume 前 `24` 个可交易 USDT perp（包含不少新币/热币，作为宽口径压力测试）
- universe 版本 B：更贴近“主流可交易 universe”的过滤版：
  - USDT perpetual
  - 排除稳定币/明显非方向性合约
  - 排除 `1000*` 异形合约
  - 上市历史至少约 `120d`
  - 按近 24h quote volume 取前 `18`
- formation windows：`24h / 72h / 7d`
- hold：`4h / 12h / 24h`
- rebalance：每 `4h`
- 组合定义：
  - 先按 `formation return` 取 bottom 30% loser bucket
  - 再按 `low_gap = close / rolling_low(formation) - 1` 在 loser 内二次排序
  - `long = low_gap 最低组`
  - `short = low_gap 最高组`
- 显式成本：pair round-trip `24 bps`（`6bps/side × 2 legs × open/close`）
- 对照：同一时点同样组数的 plain loser-vs-winner 横截面对照腿

## 产出 artifacts
- `reports/artifacts/rank191_low_anchor_survivor/summary.csv`
- `reports/artifacts/rank191_low_anchor_survivor/event_samples.csv`
- `reports/artifacts/rank191_low_anchor_survivor/meta.json`
- `reports/artifacts/rank191_low_anchor_survivor_mainstream/summary.csv`
- `reports/artifacts/rank191_low_anchor_survivor_mainstream/meta.json`

## 关键结果
### 1) 宽口径 24-symbol 压力测试
宽口径 universe 下，`72h/7d formation` 的 low-anchor pair 在若干持有窗里**相对 plain loser baseline 更好**，甚至出现正的净均值：

- `72h formation / 12h hold`: `+70.6 bps`
- `72h formation / 24h hold`: `+113.0 bps`
- `7d formation / 12h hold`: `+87.7 bps`
- `7d formation / 24h hold`: `+115.8 bps`

但这个 universe 明显混入了很多新币 / 热币 / 结构不稳定对象，不适合直接作为 survivor 升级依据。

### 2) 更贴近主流可交易 universe 的过滤版
过滤到“排除 1000 合约 + 至少约 120d 历史 + 前 18 流动性”后，结果收敛成下面这句更重要的话：

**`low_gap` 二次排序虽然比 plain loser baseline 更不差，但在所有 `24h/72h/7d × 4h/12h/24h` 组合里，显式成本后的净均值仍全部为负。**

过滤版核心结果：

| formation | hold | events | mean net pair bps | mean baseline net bps | delta vs baseline |
|---|---:|---:|---:|---:|---:|
| 24h | 4h | 956 | -60.7 | -35.6 | -25.0 |
| 24h | 12h | 954 | -133.5 | -60.1 | -73.4 |
| 24h | 24h | 951 | -215.0 | -119.0 | -96.0 |
| 72h | 4h | 944 | -36.1 | -66.5 | +30.4 |
| 72h | 12h | 942 | -49.7 | -144.7 | +94.9 |
| 72h | 24h | 939 | -120.2 | -215.1 | +94.8 |
| 7d | 4h | 920 | -26.4 | -79.3 | +52.9 |
| 7d | 12h | 918 | -45.5 | -167.3 | +121.8 |
| 7d | 24h | 915 | -112.4 | -235.5 | +123.1 |

## 解释
这轮结果不是“anchor 完全没信息”，而是更像：

1. **它确实有一点相对排序信息。**
   在 `72h/7d formation` 下，`low_gap` 二次排序通常比 plain loser reversal 更不差，说明它可能在 loser 内部有一定区分度。

2. **但这点区分度还不够交易。**
   survivor 这轮要回答的是：在 desk 口径下，显式成本后有没有足够明确的独立残余 alpha。当前答案是否定的——因为过滤版所有组合净值都仍为负。

3. **因此它不满足继续升 `P2` 的门槛。**
   如果结果是“72h/7d 版本稳定转正，只是 24h 不行”，那还可以讨论是否 re-scope；但现在更像“比 baseline 好一点，但距离可执行仍明显不够”。这不足以占用前排名额。

## 为什么本轮直接 park，而不是 keep_P1 / promote_P2
- policy 限定这就是 `Rank 191` 的**唯一一次** survivor follow-up；
- 这次 follow-up 已经把唯一 blocker 压缩并实测完：
  > `low_gap` 在 `15m` 主时钟、主流可交易 universe、显式成本后，是否有独立残余 alpha？
- 当前答案是：**没有达到足以继续前排推进的程度**；
- 同时也不存在一个这轮已经被明确验证出来、值得立刻做的唯一 re-scope 方向；
- 所以按 policy，最诚实的收口不是再拖一轮，而是直接 `park_to_background`。

## 本轮改变系统认知的话
**`Rank 191 / loser-bucket low-anchor relative-value reversal` 的 survivor 唯一 follow-up 已收口：在更贴近主流可交易 universe 的 Binance `15m` proxy 下，`low_gap` 二次排序虽然相对 plain loser reversal 有一些增量区分，但显式成本后所有 `24h/72h/7d × 4h/12h/24h` 组合的净均值仍全部为负，因此不足以继续占用前排，直接 `park_to_background`。**
