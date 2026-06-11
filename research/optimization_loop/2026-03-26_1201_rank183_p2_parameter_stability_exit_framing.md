# Rank 183 / cbeth-eth-rolling-fair-basis-mr — P2 exit framing（parameter stability）
- 时间：2026-03-26 12:01 UTC
- 对象：`Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- 本轮角色：bot3 只执行当前 `cycle_plan` 中排在最前的 pending 小点；不改排班，只回答 `15m / z>=2.0` 这条已收窄 pocket 在 rolling 窗口、z-score 阈值、hold/timeout 与执行带宽上是否存在一片可写成 paper spec 的窄参数面

## 结论
**单一收口结论：存在可写成 `paper spec` 的窄参数面，且结论已明显靠近 `promote_P3`，不支持把对象退回 `P2->P1 re-scope` 或直接 `drop_to_background`。**

更具体地说，当前最诚实的 spec 不是泛 `LSD basis`，也不是“只有单点参数才有效”的 fragile pocket，而是：

> **`CBETH spot + ETH perp` 的 `15m rolling fair-basis MR`，在 `7~10d` rolling anchor、`entry z >= 2.0`（可容忍到 `1.75~2.25`）、`exit band 0~0.5`、`timeout >= 12h` 的邻域里都还能保住 `30 bps` 口径下的正净边；但容量故事应老老实实停在小中仓位（约 `2k~10k USD`）这一档。**

## 本轮怎么做
- 复用原始快检数据：
  - `reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/pair_series.csv`
- 复用原始回测引擎定义：
  - `tmp_cbeth_basis_probe.py`
- 直接沿用同一套 entry / exit 逻辑，只把成本口径切到上一轮已确认更保守的 **`30 bps pair RT`**，然后对以下维度做参数扫描：
  1. rolling lookback：`5d / 7d / 10d / 14d`
  2. entry z-threshold：`1.5 / 1.75 / 2.0 / 2.25 / 2.5`
  3. exit band：`0.0 / 0.25 / 0.5 / 0.75`
  4. timeout：`24 / 48 / 96 / 192 bars`
  5. 执行带宽 proxy：`26 / 28 / 30 / 32 / 35 / 40 bps pair RT`

## 结果
### 1) base spec（`7d lookback / z>=2.0 / exit 0.25 / timeout 96 / cost 30 bps`）本身就不是薄得只剩单点
- `220` 笔
- mean trade `+19.86 bps`
- median trade `+14.67 bps`
- win rate `86.4%`
- median hold `1 bar`
- `p90 hold = 5 bars`
- timeout share `0.0%`
- 最弱月份的 mean trade 仍约 `+10.19 bps`

翻成人话：**这条线在更保守口径下已经不只是“有一点正”，而是存在一块仍有厚度的窄 pocket。**

### 2) rolling window：`5~14d` 都活，说明不是只靠单一 anchor 长度硬撑
在 `z>=2.0 / exit 0.25 / timeout 96 / cost 30 bps` 下：

| lookback | trades | mean_trade_bps | win_rate | 最弱月份 mean_trade_bps |
|---|---:|---:|---:|---:|
| `5d` (`480 bars`) | 239 | `+19.82` | `84.9%` | `+9.42` |
| `7d` (`672 bars`) | 220 | `+19.86` | `86.4%` | `+10.19` |
| `10d` (`960 bars`) | 204 | `+20.21` | `88.7%` | `+11.11` |
| `14d` (`1344 bars`) | 161 | `+20.21` | `88.8%` | `+12.38` |

这说明当前对象 **不是** “rolling window 一改就塌”的 single-point 策略；更像是 **`7~10d` 最平衡，`14d` 更稳但更稀疏**。

### 3) z-threshold：`1.75~2.25` 是一片窄面，不是只有 `2.0` 一个点
在 `7d lookback / exit 0.25 / timeout 96 / cost 30 bps` 下：

| entry z | trades | mean_trade_bps | win_rate | 最弱月份 mean_trade_bps |
|---|---:|---:|---:|---:|
| `1.5` | 408 | `+10.36` | `67.6%` | `+2.31` |
| `1.75` | 299 | `+14.93` | `78.3%` | `+5.95` |
| `2.0` | 220 | `+19.86` | `86.4%` | `+10.19` |
| `2.25` | 163 | `+25.26` | `93.3%` | `+15.26` |
| `2.5` | 123 | `+29.14` | `95.1%` | `+18.03` |

结论不是“z 越高越好就完了”，而是：
- `1.5` 这层在更保守口径下已经太薄，不适合继续当主 production pocket；
- `2.0` 是当前 **流量 / 厚度 / 稳定性** 最均衡的中心点；
- `2.25~2.5` 也能活，但明显是 **更稀疏、更像容量更小的高确信 pocket**。

### 4) exit framing：`0.0~0.5` 都还能活，说明不是只靠某个 exit 写法
在 `7d lookback / z>=2.0 / timeout 96 / cost 30 bps` 下：

| exit band | trades | mean_trade_bps | win_rate |
|---|---:|---:|---:|
| `0.0` | 213 | `+22.31` | `89.7%` |
| `0.25` | 220 | `+19.86` | `86.4%` |
| `0.5` | 228 | `+17.93` | `81.6%` |
| `0.75` | 230 | `+16.50` | `76.1%` |

翻成人话：
- 更严格地等它更接近真正均值（`exit 0.0`）会让每笔更厚，但交易数略少、持有略长；
- `0.25` 不是神奇甜点，只是一个比较平衡的退出写法；
- `0.5` 仍为正，说明 **这不是 exit 定义轻轻一改就死掉的脆弱对象**；
- 到 `0.75` 也没直接死，但已经开始明显稀释 edge，不值得再放松。

### 5) hold / timeout：timeout 基本不是主矛盾，当前对象天然就是快进快出
在 `7d lookback / z>=2.0 / exit 0.25 / cost 30 bps` 下：

| timeout | trades | mean_trade_bps | timeout_share |
|---|---:|---:|---:|
| `24 bars` (`6h`) | 220 | `+19.80` | `0.45%` |
| `48 bars` (`12h`) | 220 | `+19.86` | `0.0%` |
| `96 bars` (`24h`) | 220 | `+19.86` | `0.0%` |
| `192 bars` (`48h`) | 220 | `+19.86` | `0.0%` |

再结合 base spec 的持有分布：
- median hold = `1 bar`
- `p90 hold = 5 bars`
- 最长持有也只有 `40 bars`

所以这里真正决定对象成色的，不是 timeout 写 `12h` 还是 `24h`，而是 **entry 强度和执行带宽**。timeout 更像一个防事故护栏，而不是 alpha 主旋钮。

### 6) 执行带宽：在小中仓位 proxy（`26~30 bps`）下仍厚；大一点就明显开始被容量吃掉
在 `7d lookback / z>=2.0 / exit 0.25 / timeout 96` 下：

| pair RT | mean_trade_bps | median_trade_bps | win_rate | 最弱月份 mean_trade_bps |
|---|---:|---:|---:|---:|
| `26 bps` | `+23.86` | `+18.67` | `93.2%` | `+14.19` |
| `28 bps` | `+21.86` | `+16.67` | `91.4%` | `+12.19` |
| `30 bps` | `+19.86` | `+14.67` | `86.4%` | `+10.19` |
| `32 bps` | `+17.86` | `+12.67` | `81.8%` | `+8.19` |
| `35 bps` | `+14.86` | `+9.67` | `76.8%` | `+5.19` |
| `40 bps` | `+9.86` | `+4.67` | `62.7%` | `+0.19` |

结合上一轮 honesty gate 的 Coinbase `CBETH-USD` 深度：
- `2k~10k USD` 的 CBETH 现货冲击约 `2.6~4.8 bps`
- `25k USD` 则已经抬到 `5.0~7.7 bps`

因此最诚实的 exit framing 不是“这条线能吃很大容量”，而是：
> **在 `2k~10k USD` 这一档的小中仓位，`26~30 bps` 的 pair RT 仍留下足够厚的 pocket；但若把故事往更高成本/更大名义外推，edge 会很快从厚 pocket 收缩成薄边。**

## 为什么这轮结论靠近 promote_P3，而不是 P2->P1 / P0
- **不是 `P2->P1 re-scope`**：因为没有出现“必须改对象定义才能继续”的新证据。相反，当前对象定义已经足够稳定，只是被进一步收敛成了一个更诚实的窄版 spec。
- **不是 `drop_to_background`**：因为 `7~10d lookback + z>=2.0 + exit 0~0.5 + 26~30 bps` 不是单点幻觉，而是一片仍然为正的窄面。
- **是“靠近 `promote_P3`”**：因为现在剩下的关键问题已经不再是“参数一改就塌吗”，而是下一小点该回答的——**在真实小中仓位执行、CBETH 现货深度与 ETH perp 节奏下，是否还藏着唯一剩余的致命 honesty blocker。**

## 当前最诚实的 paper-spec 草图
- pair：`CBETH spot + ETH perp`
- bar：`15m`
- slow anchor：`7~10d rolling fair basis`
- entry：`|z| >= 2.0` 为主；`2.25` 可作为更稀疏的高确信变体
- exit：回到 `0.25` 左右；若更保守，可要求回到 `0.0`
- timeout：`12h~24h` 都可，更多是风险护栏而非 alpha 驱动项
- size / bandwidth：默认从 **`2k~10k USD` 小中仓位** 起步，不讲大容量故事

## 本轮改变系统认知的一句话
`Rank 183` 不是只靠单点参数硬撑的 P2 幻觉：在 `7~10d` rolling anchor、`z>=2.0` 为中心、`exit 0~0.5` 与小中仓位 `26~30 bps` 执行带宽下，它已经收敛成一片可写成 paper spec 的窄参数面，因此下一步只需确认是否还剩唯一的致命 honesty blocker。
