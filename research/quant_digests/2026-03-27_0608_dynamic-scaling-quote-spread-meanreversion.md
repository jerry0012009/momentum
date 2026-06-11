# 别先训 RL：这篇 2024 论文更适合先复现的是「同币多报价价差回归 + 按 |z| 分层加仓」

- 主题类型：raw alpha
- 基础 alpha：同一底层币种在不同报价货币/稳定币交易对之间会出现短暂价差偏离，偏离扩大后通常向均值回归；更大的偏离可配更大的仓位。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 为什么这次值得进池
这篇材料的 headline 是 **RL pair trading**，但对我们 desk 更值钱的不是“上来就训 A2C/PPO”，而是它清楚给了一个更可落地的旁支：

> **base alpha 仍然是同币多报价的短周期 spread mean reversion；真正值得先复现的是“仓位随偏离强度动态缩放”，而不是先上完整 RL 栈。**

这很适合当前 `1m/3m/5m/15m` 的研发顺序：
1. 先确认同币多报价 spread 在短周期上是否真的回归；
2. 再确认 **|z| 越大，后续回归幅度是否也越大**；
3. 若成立，就先用**确定性分层 sizing**吃掉大部分 paper edge，没必要第一步就做 RL 训练、奖励塑形和高算力调参。

## 2. 论文里真正值得抄的那一段
### 2.1 核心材料
- **Authors / Year**: Hongshen Yang, Avinash Malik / 2024
- **Title**: *Reinforcement Learning Pair Trading: A Dynamic Scaling Approach*
- **Venue**: *Journal of Risk and Financial Management* 17(12):555
- **DOI**: `10.3390/jrfm17120555`
- **Readable URL**: <https://arxiv.org/abs/2407.16103>
- **Journal URL**: <https://doi.org/10.3390/jrfm17120555>
- **Repo URL**: 未见作者公开 repo（文中说明原始数据来自 Binance）

### 2.2 论文做了什么
论文在 Binance 的 **BTCGBP / BTCEUR** 上做 `1m` 高频 pairs。流程并不花哨：
- pair formation：相关性 + Engle-Granger cointegration
- spread：rolling regression + z-score
- 训练期网格搜索出的固定参数：
  - `open threshold = 1.8`
  - `close threshold = 0.4`
  - `window size = 900 intervals`
- 再比较：
  - 传统固定阈值 pairs（Gatev）
  - RL1：RL 决定 timing
  - RL2：RL 决定 timing + quantity（动态缩放仓位）

### 2.3 最重要的结果不是“RL 神奇”，而是“动态缩放有价值”
在论文的 `0.02%` 交易费假设下，测试期（2023-12）结果：
- Gatev 固定规则：**8.33%** cumulative return
- RL1（A2C）：**9.94%**
- RL2（A2C，timing + quantity）：**31.53%**

同时，RL2 的总 action count 是 **229**，低于 Gatev 的 **490**，说明论文里更像是：
- 不是靠更频繁交易赚钱；
- 而是靠**把更强的偏离打得更重**，把弱机会打得更轻。

这就是我们该拿走的 desk 分支：
**把“spread 偏离强度 → 仓位大小”做成明确 sizing ladder。**

## 3. desk 化翻译：先别复现 RL，先复现这个更小的版本
把论文翻成我们能最快上线实验的版本：

### 3.1 最小策略骨架
以同币多报价为例（例如 `BTCUSDT/BTCUSDC`、`BTCUSDT/BTCFDUSD`、`ETHUSDT/ETHFDUSD`）：
- **entry**：`|z| > z_open`
  - 若 spread 过高：short 贵的一边，long 便宜的一边
  - 若 spread 过低：反向做
- **exit**：`|z| < z_close` 或持有满 `N` 根
- **sizing**：不要一刀切；按 `|z|` 分层
  - `2.0 ~ 2.5σ`：`1.0x`
  - `2.5 ~ 3.0σ`：`1.5x`
  - `> 3.0σ`：`2.0x`
- **risk**：
  - 单对最大名义仓位 cap
  - 若稳定币自身偏离（USDC/FDUSD 脱锚）超阈值，直接停
  - 若盘口深度不足或手续费档位不够低，停
- **cost**：这是这类 alpha 的生死线；若是 taker 四腿硬吃，很多 edge 会被磨平

## 4. 我们自己的最小快检（Binance Spot 公共 5m 数据，近 45 天）
### 4.1 数据口径
- **数据源**：Binance Spot public `api/v3/klines`
- **公开性**：公开可得，无需 key
- **频率**：`5m`
- **样本**：近 `45d`
- **pair**：
  - `BTCUSDT / BTCUSDC`
  - `BTCUSDT / BTCFDUSD`
  - `ETHUSDT / ETHUSDC`
  - `ETHUSDT / ETHFDUSD`
- **实验口径**：
  - rolling `288` 根（约 1 天）计算 z-score
  - 当 `|z| > 2` 触发事件
  - 看未来 `12` 根（约 1 小时）spread 是否回归

### 4.2 结果：偏离越大，1 小时回归幅度通常越大
#### BTCUSDT / BTCUSDC
- `|z| ∈ [2, 2.5)`：平均 1h 回归 **0.91 bp**，胜率 **84.0%**
- `|z| ∈ [2.5, 3)`：平均 1h 回归 **1.10 bp**，胜率 **84.9%**
- `|z| ≥ 3`：平均 1h 回归 **1.74 bp**，胜率 **96.5%**

#### ETHUSDT / ETHFDUSD
- `|z| ∈ [2, 2.5)`：平均 1h 回归 **1.26 bp**，胜率 **71.7%**
- `|z| ∈ [2.5, 3)`：平均 1h 回归 **1.64 bp**，胜率 **77.9%**
- `|z| ≥ 3`：平均 1h 回归 **2.20 bp**，胜率 **80.2%**

### 4.3 结果：简单分层 sizing，相比固定 1x 有明显提升
用最粗糙的确定性 size ladder：
- `[2, 2.5)` → `1.0x`
- `[2.5, 3)` → `1.5x`
- `[3, +∞)` → `2.0x`

在同样的事件集上，按“未来 1 小时 spread 收敛 bp × 仓位权重”算，较固定 `1x` 的 gross convergence-unit 提升：
- `BTCUSDT/BTCUSDC`：**+31.2%**
- `BTCUSDT/BTCFDUSD`：**+37.7%**
- `ETHUSDT/ETHUSDC`：**+31.9%**
- `ETHUSDT/ETHFDUSD`：**+35.5%**

这不是正式回测，但已经足够说明：
**论文里最值得先搬的，很可能不是 RL 本身，而是“强偏离打更大、弱偏离打更小”的 sizing 逻辑。**

相关 artifact：
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/rl2_dynamic_sizing_quote_spread_probe_20260327_0608/sizing_comparison.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/rl2_dynamic_sizing_quote_spread_probe_20260327_0608/bucket_convergence.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/rl2_dynamic_sizing_quote_spread_probe_20260327_0608/summary.json`

## 5. 这东西怎么直接落成完整策略
### entry
- universe：同币多报价 / 多稳定币报价对
- 先做 liquidity gate：只保留最深的 2~4 个报价腿
- `spread = log(p_a / p_b)`
- rolling mean/std 生成 z-score
- `|z| > 2` 入场

### exit
- `|z| < 0.5` 平仓
- 或 `max_hold = 12~24 bars`
- 或当 z-score 继续恶化并触发 stop band

### sizing
- 先别 RL，先 deterministic ladder
- 之后再试：
  - 连续仓位函数（如 `size ∝ min(|z|-2, cap)`）
  - RL / contextual bandit / ordinal classifier

### risk
- quote leg 单边风控：防稳定币脱锚和单腿流动性塌陷
- pair cap + cluster cap：防多组 pair 实际都在押同一个 quote shock
- event veto：大新闻、交易所维护、稳定币异常链上事件暂停

### cost
- 这类 alpha 的核心不是方向，而是 **净点差 - 手续费 - 冲击成本**
- 若你的真实执行接近 taker/taker，两边各进各出，paper edge 很容易被吃光
- 因此默认优先：
  - maker 优先
  - 零费/低费档位
  - 盘口挂单成交率先评估

## 6. 我会怎么排“下一步怎么测”
### P0：先做 deterministic 版本，不碰 RL
1. 用 `1m / 3m / 5m` 分别跑同币多报价 pairs
2. 固定 `z_open ∈ {2.0, 2.25, 2.5}`，`z_close ∈ {0.25, 0.5, 0.75}`
3. 对比两种 sizing：
   - fixed `1x`
   - ladder `1x/1.5x/2x`
4. 输出：净收益、每事件净 bp、胜率、平均持有时间、手续费敏感性

### P1：验证“仓位随偏离增大”到底是不是稳的
把样本按：
- 白天/夜间
- 高波动/低波动
- 稳定币 pair（USDT/USDC/FDUSD） vs 法币 quote pair
- BTC vs ETH
做分层，确认“`|z|` 越大 → 回归越强”是否跨 regime 稳定。

### P2：再决定是否值得上 ML / RL
只有在下面三条都成立时，才值得往 RL 走：
- 固定 threshold raw alpha 已经为正
- size ladder 对 fixed 版有稳定增益
- 增益不是纯样本内现象，而是 walk-forward 也保得住

否则，RL 大概率只是把一个本来就薄的 alpha 包装得更复杂。

## 7. 一句话结论
这篇 2024 新论文对我们最值钱的不是“用 RL 预测交易动作”，而是更朴素的那句：

> **同币多报价 spread 回归这件事，仓位不该一刀切；越极端的偏离，越值得给更大的 size。**

对短周期 desk 来说，这已经足够成为一个可独立复现、可直接落地的完整策略版本，而且第一步完全不需要先上 RL。
