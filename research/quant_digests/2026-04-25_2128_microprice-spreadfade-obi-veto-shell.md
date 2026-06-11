# 别把这个 2025 `Crypto_Stat-Arb_HFT_Model` 仓只读成“又一个配对回归 demo”：对 short-cycle crypto desk，更该先拆的是「microprice spread fade × order-book imbalance veto」这条完整 raw alpha 壳
- 时间：2026-04-25 21:28 UTC
- 类型：GitHub / repo
- 主题类型：raw alpha
- 基础 alpha：两条高相关/协整 perp 的相对价差如果在短时间内偏离到历史尾部，后续更容易向均值回归；交易上对应 short rich leg / long cheap leg 的 spread fade
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 已给出完整壳；但我本轮 public-data probe 只先验证了 base alpha，本轮还没把历史 OBI filter 一并做完）
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / microstructure / microprice / order-book-imbalance / spread-zscore / 1m / 3m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：工程源码审计 + public-data portability probe

## 1. 先回答：这篇东西的 base alpha 是什么？
**base alpha 不是 OBI，也不是微价格本身。**
它的 alpha 本体是：**pair spread overextension mean reversion**。

更直白地说：
- 先找两条平时经常一起动的币；
- 如果某一刻它们的相对价格关系突然“拉太开”；
- 那后面几分钟里，常见路径是 leader 回一点、lagger 跟一点，spread 往回收；
- `OBI / microprice` 在这里更像**入场确认 / 执行 veto**，不是 alpha 本体。

所以它属于：
- **主题类型：raw alpha**
- 不是纯 filter 文
- 但实现里带了一个很实用的 microstructure admission 层

## 2. 这次看了什么
这次看的是 2025 GitHub repo：**SamarthChaudhary-22 / Crypto_Stat-Arb_HFT_Model**。

- Authors / Year / Title / Venue：SamarthChaudhary-22 (2025), *Crypto_Stat-Arb_HFT_Model*, GitHub repo
- Repo URL：<https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model>
- Readable URL：<https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/README.md>
- 关键源码：
  - <https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/analyzer.py>
  - <https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/data_loader.py>
  - <https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/book_recorder.py>
  - <https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/main.cpp>
  - <https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/strategies.json>
  - <https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/fix_strategies.py>

repo 不算学术化，也谈不上工程成熟，但优点是**壳非常完整**：
1. `data_loader.py`：拉 Binance USDⓈ-M `1m` K 线；
2. `analyzer.py`：先做相关性 + OLS + ADF + half-life，筛 pair；
3. `book_recorder.py`：抓 top-5 depth，算 `obi` 和 `micro_price`；
4. `main.cpp`：实时算 spread z-score，用 `OBI` 做 admission，再下单；
5. `RiskEngine`：单仓亏损阈值 + 全局 kill switch。

这就是它比很多“只有 notebook 没有交易壳”的 repo 更值得 intake 的地方。

## 3. 一句话核心结论
**一句话核心结论**：这仓真正值得 desk 借的，不是“协整检测”本身，而是把一条朴素的 spread fade，往前推进成了**可直接部署的短周期完整策略壳：`pair admission -> spread signal -> OBI veto -> sizing -> exit -> kill switch`**。

## 4. 它是怎么证明这件事的
**一句话说明它怎么证明**：不是靠论文统计表，而是靠一套可读源码把研究、筛选、实时信号、执行和风控串成了完整流程；我又额外用 Binance 公共 `1m` 数据做了一个最小 portability probe，先确认这条 base alpha 最近是否还有“几分钟内回归”的形状。

## 5. repo 到底写了什么（拆成人话）

### 5.1 Pair admission：先别乱配
`analyzer.py` 的逻辑不是“看到两条线像就上”，而是：
- 先抓 top 50 liquid USDT perp；
- 用 1 年 `1m` 数据；
- 为了加速，把序列 resample 到 `1h` 做 pair scan；
- 只保留：
  - correlation > `0.85`
  - ADF p-value < `0.05`
  - half-life < `240` 分钟
  - overlap > `1000` 小时

这一步的意义很简单：
**不是所有相关 pair 都值得做，得先筛出“真有回归 tendency”的 pair。**

### 5.2 Alpha 本体：spread z-score fade
repo 在实盘里交易的是：
- `spread = log(p1) - hedge_ratio * log(p2)`
- `z = (spread - mean) / std`

入场逻辑：
- `z > 2`：spread 太高，做 `short leg1 / long leg2`
- `z < -2`：spread 太低，做 `long leg1 / short leg2`

这就是最核心的 raw alpha。

### 5.3 它真正有意思的地方：不是裸 z-score，而是加了 microstructure veto
`main.cpp` 里不是直接拿 mid price，而是先算一个**微价格（microprice）**：

`weighted_price = (best_bid * ask_vol + best_ask * bid_vol) / (bid_vol + ask_vol)`

直觉上，它是在问：
- 如果买盘更厚，真实短时公允价往往更偏向 ask；
- 如果卖盘更厚，真实短时公允价往往更偏向 bid。

然后再算每条腿自己的盘口失衡：
- `obi = (bid_vol - ask_vol) / (bid_vol + ask_vol)`

repo 的 admission 是：
- 若 `z > 2`，准备做 `short leg1 / long leg2`，那就希望：
  - `leg1` 不要也在强买盘里继续被顶；
  - `leg2` 不要还在强卖盘里继续被砸；
- 反过来若 `z < -2` 也一样。

源码里的默认阈值：
- `OBI_LONG_THRESHOLD = -0.2`
- `OBI_SHORT_THRESHOLD = 0.2`
- `Z_ENTRY = 2.0`
- `Z_EXIT = 0.5`

换成人话就是：
**只有当 spread 已经偏了，而且盘口短时力量也不反着你时，才让你进。**

这层设计对短周期 desk 很重要，因为它解决的是：
- 价差确实“看起来偏了”，
- 但你一进场就继续被 order-flow 顶飞/砸穿

也就是很多 pair fade 策略最常见的“看对均值、死于路径”的问题。

## 6. 为什么这篇对当前项目有价值
这仓和当前 `momentum` 项目有直接关系，不是因为它写得多漂亮，而是因为它补的是一个很清楚的缺口：

1. **它是 raw alpha，不是纯解释文**
   - alpha 本体很清楚：spread fade；
   - filter 也清楚：OBI veto；
   - 可以明确拆层。

2. **它是完整策略壳，不只是信号片段**
   - 有 pair admission
   - 有 entry / exit
   - 有 sizing
   - 有 risk engine
   - 有 execution queue

3. **它能下沉到 `1m / 3m / 5m`，再向上映射到 `15m`**
   - microstructure 层天然更适合 `1m/3m`
   - spread fade 本体则可以用 `5m/15m` 先做慢一点的 honest first verdict

4. **它比“又一篇普通 pair z-score 文”多了一层真正可研究的执行 veto**
   - 当前 desk 最近 pairs digest 已经不少；
   - 但这仓多出来的价值，是把 **L2 盘口方向确认** 明确放进了 pair fade 的 admission。

## 7. 我补做的最小 portability probe（诚实版）
为了不被 repo 的“实盘感”迷惑，我先只做了一个**不带历史 OBI 的 base-alpha probe**：

### 数据与口径
- 数据源：Binance USDⓈ-M public `1m` klines
- 公开性：公开可得，无需私有数据
- 更新频率：`1m`
- 样本：最近约 `8 * 1500 ≈ 12000` 根 `1m` bars（约 8 天）
- 测试 pair：
  - `LINKUSDT / SOLUSDT`（repo `strategies.json` 已给）
  - `ENAUSDT / XRPUSDT`（repo `strategies.json` 已给）
- 信号：
  - 用 repo 提供的 `hedge_ratio`
  - rolling `60` 分钟 spread z-score
  - 当 `|z| >= 2 / 2.5 / 3` 时，做反向 spread fade
- 评估：看未来 `1/3/5` 分钟 spread 是否向回收，单位是 **spread-space gross bps**
  - 这里只是先看 alpha 形状，**还不是完整实盘净收益**

### 核心结果
`LINKUSDT / SOLUSDT`
- `|z|>=2`：未来 `3m` 平均回归约 **`+1.09 bps`**，胜率 **`57.4%`**
- `|z|>=2.5`：未来 `5m` 平均回归约 **`+2.65 bps`**，胜率 **`58.0%`**
- `|z|>=3`：未来 `3m` 平均回归约 **`+4.81 bps`**，胜率 **`65.3%`**；未来 `5m` 约 **`+5.64 bps`**，胜率 **`64.7%`**

`ENAUSDT / XRPUSDT`
- `|z|>=2`：未来 `3m` 平均回归约 **`+1.23 bps`**，胜率 **`55.4%`**
- `|z|>=2.5`：未来 `5m` 平均回归约 **`+1.74 bps`**，胜率 **`54.0%`**
- `|z|>=3`：未来 `3m` 平均回归约 **`+3.05 bps`**，胜率 **`59.9%`**；未来 `5m` 约 **`+4.15 bps`**，胜率 **`58.0%`**

### 先怎么解读
这组结果说明三件事：
1. **base alpha 不是空壳**：极端 spread 偏离后，后面几分钟确实更常往回走；
2. **阈值越高，单位机会厚度越明显**：`|z|>=3` 明显比 `|z|>=2` 更像样；
3. **这也正说明 OBI veto 有研究价值**：如果 base alpha 只有几 bps 厚，那你更需要 admission 层把“最容易继续跑偏的 entry”踢掉。

但也要诚实：
- 这些数字目前还是 **gross spread-space edge**；
- 没扣双腿手续费、滑点、冲击成本；
- 也没做真正的历史 depth replay；
- 所以它现在更像：**alpha 形状存在，execution / filter 是否能把它救到可交易，要继续测。**

## 8. 策略拆解（按可直接复现口径写）

### Base alpha
- 高相关/协整 pair 的 spread 短时过度偏离，未来几分钟更容易均值回复。

### Entry
- 先做 pair admission：相关性、ADF、half-life 过滤；
- 实时计算 `spread z-score`；
- `z > +z_th`：`short leg1 / long leg2`
- `z < -z_th`：`long leg1 / short leg2`
- 只有当两条腿的 `OBI` 没有明显反着你时才入场。

### Exit
- z-score 回到 `0.5` 附近先止盈/平仓；
- repo 原版没有特别优雅的 spread stop，而是更多依赖单仓 PnL kill；
- 对 desk 来说，更好的版本应再补：`time stop + spread stop + liquidity break stop`。

### Sizing
- repo 默认 `BET_SIZE = 1000 USD`，两腿按价格和 `hedge_ratio` 换算张数；
- 第一版完全可以用 dollar-neutral notional；
- 第二版再换成 residual-vol targeting / pair-level vol targeting。

### Risk
- repo 已有：
  - 单仓亏损阈值（`MAX_LOSS_PER_POS = -20 USD`）
  - 全局 kill（`GLOBAL_PNL_KILL = -100 USD`）
- 但 desk 更该补：
  - 单 pair 并发限制
  - 同 sector pair 冲突净额控制
  - OBI 反转后的早退条件
  - spread 再扩张到 `4σ` 以上的硬止损

### Cost
- 这是成败关键。
- 这类两腿策略最怕：
  - 双腿 taker 费
  - 薄腿滑点
  - 一腿成交、一腿没成交的 legging risk
- 所以 OBI veto 的真正使命，不只是“提高胜率”，而是**提升单位机会厚度，让 gross edge 更有机会穿过成本门槛。**

## 9. 最值得复用 / 借鉴的部分
如果把这仓当素材库，而不是当成可直接上线代码，最值得借的是这 5 件事：

1. **pair admission 和实盘执行是分开的**
   - 研究层先筛 pair，实时层只交易已准入组合。

2. **spread 信号和 microstructure veto 是分层的**
   - 这让你后续可以单独替换 OBI / CVD / OFI，而不用重写 alpha 本体。

3. **microprice 比 mid 更适合短周期 entry 视角**
   - 它不是万能，但比裸 last/mid 更接近“盘口当前更想往哪边走”。

4. **execution queue + risk engine 的架子是对的**
   - 即便实现还粗糙，结构上已经比很多 notebook 仓前进一步。

5. **它天然适合做 `1m/3m` 研究，再向 `5m/15m` 做 slower projection**
   - 也就是：先测更快的 alpha 形状，再看慢一点的可部署版。

## 10. 最小可复现实验怎么做
如果下一轮直接复现，我建议别一次把 HFT 壳全抄完，先做三个层次：

### 实验 A：只测 base alpha（最快）
- 数据：Binance `1m` klines
- pair：从 top-liquidity universe 里筛 20~40 组
- signal：rolling spread z-score
- threshold：`2 / 2.5 / 3`
- exit：`1/3/5/10m` fixed hold + `z -> 0.5` crossing
- 输出：trade count / gross bps / win rate / pair ranking

### 实验 B：给 base alpha 加一个“伪 OBI”层
- 若还拿不到历史 depth，可先用：
  - taker buy ratio
  - micro-return burst
  - quote imbalance proxy
- 目标不是完美替代，而是先看 **admission layer 能不能筛掉最差 entry**。

### 实验 C：再上真实 L2 admission
- 数据：Binance depth websocket 或定频 snapshot 录制
- 对齐方式：entry 前 `1~5s` 的 top-of-book / top-5 depth
- 检查：
  - OBI 阈值是否真能提升 markout
  - microprice vs mid 哪个更稳
  - 只 veto 最差样本，还是能显著抬高整组 alpha

## 11. 下一步怎么测
下一步不要再泛泛地讲“pairs + microstructure 很有道理”，直接测这 4 件事：

1. **先把 OBI 从“叙事层”拉到统计层**
   - 对每次 spread entry，记录入场前 `1s/3s/5s` 的 `obi1/obi2`
   - 比较 `OBI-aligned` 与 `OBI-opposed` 两组未来 `1m/3m/5m` 的 spread markout

2. **把 `|z|>=3` 做成主样本，而不是默认 `|z|>=2`**
   - 当前 probe 很清楚：极端样本明显更厚
   - OBI filter 应优先服务于厚样本，而不是稀释到所有普通偏离

3. **做一版成本梯子**
   - `4 / 8 / 12 / 16 bps` 四档总成本
   - 分别看 maker-first、maker+taker、双腿 taker 是否还能活

4. **做 pair router，不做 always-on 全开**
   - 这条线很可能不是“所有 pair 全天候都有效”
   - 更像是：少数 liquid pair、少数极端 spread、少数 order-book 配合时段，才有 pocket

## 12. 风险与边界
- repo 的工程风格比较粗，很多参数是 demo 级，不应直接照搬；
- `strategies.json` 里也能看到部分离谱 hedge ratio / pair 组合，说明 pair discovery 仍需要更严格的 sanity check；
- 当前我还没做历史 depth replay，所以 **OBI 这层目前仍是高潜力假设，不是已验证事实**；
- 如果最终发现只有 base alpha 有一点 edge，但 OBI 提升不明显，那它就应被降级为：
  - `spread fade raw alpha`
  - + 一个未过检的 microstructure filter 候选

## 13. 本地实验产物
- `reports/artifacts/quant_digests/2026-04-25_microprice_obi_pairfade_probe_summary.csv`
