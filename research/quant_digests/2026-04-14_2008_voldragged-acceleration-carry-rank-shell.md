# 别把这份 Millennium-style multifactor repo 只读成“日频因子拼盘”：对 short-cycle desk，更该先拆的是「vol-dragged acceleration carry rank」这条 cross-sectional raw alpha——但 Binance perp `5m/15m` first verdict 明显不过成本线

- 时间：2026-04-14 20:08 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `main.py` + `factors.py` + `signals.py` + `risk.py` + `backtester.py`）+ Binance USDⓈ-M `5m/15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**做多“短期斜率相对中期斜率正在加速、且 realised vol drag 更轻”的币，做空“加速最弱/波动拖累最重”的币；本质上是一个 cross-sectional carry / acceleration 排名。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/carry/acceleration/vol-drag/ranking/market-neutral/long-short/vol-target/regime-filter/binance-perpetual/5m/15m/repo/public-data/cost/risk
- 证据类型：repo source audit + public-data first verdict

## 1. 这次看了什么
这次主来源不是论文，而是一个很新的 GitHub repo：

- **Authors：** `takahashi3899`（GitHub user）
- **Year：** 2026
- **Title：** `crypto-multifactor-strategy`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/takahashi3899/crypto-multifactor-strategy>
- **Repo URL：** <https://github.com/takahashi3899/crypto-multifactor-strategy>
- **Repo metadata：** created `2026-04-13`, public, Python, description 写的是：*Momentum, Value, Carry, Quality factors with volatility-targeted position sizing and regime filter*

它表面上像一个“Millennium-style 多因子 crypto pod”教学壳：
- `factors.py` 里给了 `momentum / value / carry / quality` 四因子；
- `signals.py` 里有 cross-sectional z-score、IC-weight blend、regime scalar；
- `risk.py` 里有 vol targeting、per-asset limits、hard-stop、correlation penalty；
- `backtester.py` 里有 turnover 驱动的 commission + slippage 成本模型；
- `main.py` 里串起 data → factor → risk → backtest → walk-forward。

所以它不是只有一句 README 的空壳，确实能拆出：
> **entry / exit / sizing / risk / cost**

但对当前 desk，更值得先抽出来的，不是四因子等权拼盘，而是里面最容易迁移到短周期的那条 **carry proxy branch**。

---

## 2. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = 横截面上，“短期趋势加速度更强、但波动拖累更轻”的币，下一小段时间更容易继续相对跑赢；反过来，加速度弱且 vol drag 重的币更容易相对落后。**

翻成人话：
- 这不是 funding carry；
- 也不是现货-合约 basis carry；
- 它其实是一个 **price-based carry proxy**；
- 更准确地说，是：
  - `short-term slope`
  - 减去一部分 `medium-term slope`
  - 再减去 `realised vol drag`
  - 然后做 cross-sectional ranking。

所以它属于：
- `raw alpha`
- 更像 **cross-sectional / relative-value / carry-proxy / acceleration**
- 不是纯 `filter`
- 不是纯 `regime`
- 也不是只会讲风险管理的 overlay

---

## 3. repo 里最值得 desk 记住的，不是“多因子”三个字，而是这条 carry 定义其实已经能单独立起来
`factors.py` 里给的 carry proxy 非常直接：

```python
short_slope  = prices.pct_change(10)
medium_slope = prices.pct_change(30)
acceleration = short_slope - medium_slope * 0.5
vol_drag     = returns.rolling(20).std() * sqrt(252)
carry        = acceleration - vol_drag * 0.3
```

这条定义最有价值的地方，是它已经天然回答了 4 件事：

1. **alpha 本体是什么**  
   不是“低估值”“高质量”这些偏慢变量，而是一个能逐 bar 更新的 price-based 相对强弱分数。

2. **为什么可能赚钱**  
   它赌的是：
   - 短期趋势在加速；
   - 但不是纯高波动乱冲；
   - 所以“加速度 / 波动拖累”比更高的币，后面一小段时间更可能继续相对领先。

3. **为什么能 desk 化**  
   因为它不依赖链上、funding、basis 或外部基本面；只要有 OHLCV，就能先做最小实验。

4. **为什么不能把名字当真**  
   repo 叫它 `carry`，但这不是传统 carry。更准确地说：
   > **它是“vol-dragged acceleration carry proxy”，不是 funding/basis carry。**

这点很重要，不然很容易把概念读歪。

---

## 4. 为什么我这轮选它，而不是直接读整个四因子 composite
原因很简单：

### 4.1 `momentum / value / quality` 里，后两条天生更慢
- `value` 在 repo 里本质是 `price / rolling 30d avg volume` 的 NVT proxy；
- `quality` 是 `30d vs 90d volume growth × consistency`；
- 这两条更像中低频横截面配置，不是当前 `5m/15m` desk 最先该补的东西。

### 4.2 carry proxy 反而最适合做 short-cycle first verdict
因为它：
- 完全用价格和成交量代理；
- 规则短；
- 不需要外部 API key；
- 能很快映射到 Binance public futures `5m/15m`。

### 4.3 这条线也确实更贴近当前研究主线
当前主线不只是 trend / breakout，还明确要补：
- `cross-sectional`
- `relative value`
- `carry`
- `stat-arb`

这条刚好卡在 **cross-sectional carry-proxy** 这个缺口上。

---

## 5. 我这轮怎么把它 desk 化成最小实验
### 5.1 最小实验口径
- **市场：** Binance USDⓈ-M perpetual
- **数据源：** public `fapi/v1/klines`
- **公开性：** 公开可得
- **更新频率：** `15m / 5m`
- **universe：** `BTC, ETH, SOL, XRP, ADA, DOGE, LINK, AVAX, DOT, ATOM, LTC, BNB`
- **流动性 admission：** 每个时点只保留 trailing `96` bars 平均 quote volume 排名前 `8` 的币
- **因子：** 直接照 repo 的 carry proxy 结构改写到 intraday
- **交易方式：**
  - 横截面排名
  - **long top 2 / short bottom 2**
  - 组合 gross = `1.0`
  - market-neutral
- **换仓节奏：**
  - `15m`：每 `4` 根 bar 换一次（约 1 小时）
  - `5m`：每 `6` 根 bar 换一次（约 30 分钟）
- **成本：** turnover × `4 bps`
  - 这是偏宽松的组合级粗成本，不是更严格的多腿 fill-aware 成本

### 5.2 本轮产物
- 脚本：`reports/artifacts/quant_digests/2026-04-14_takahashi_carry_rank_probe.py`
- 汇总：`reports/artifacts/quant_digests/takahashi_carry_rank_probe_summary_2026-04-14.csv`
- 明细：
  - `reports/artifacts/quant_digests/takahashi_carry_rank_probe_detail_15m_2026-04-14.csv`
  - `reports/artifacts/quant_digests/takahashi_carry_rank_probe_detail_5m_2026-04-14.csv`
- 资产贡献：
  - `reports/artifacts/quant_digests/takahashi_carry_rank_probe_asset_15m_2026-04-14.csv`
  - `reports/artifacts/quant_digests/takahashi_carry_rank_probe_asset_5m_2026-04-14.csv`
- 额外 cadence 复核：`reports/artifacts/quant_digests/takahashi_carry_rank_cadence_15m_subset_2026-04-14.csv`

---

## 6. first verdict：gross 不是零，但 short-cycle 上换手把它吃穿了
### 先记 4 个关键数据点
1. **`15m` 主实验还有 gross，但 net 明显转负**：
   - `6000` bars
   - `1500` 次 rebalance
   - **gross `+810.72 bps`**
   - **net `-1507.28 bps`**
   - turnover `579.5`
   - mean net `-1.31 bps / rebalance`

2. **`5m` 更差，不是“更快更强”，而是更快更容易死在换手上**：
   - `15000` bars
   - `2500` 次 rebalance
   - gross 只剩 **`+284.22 bps`**
   - net 变成 **`-4403.78 bps`**
   - turnover `1172.0`
   - mean net `-2.08 bps / rebalance`

3. **这条线不是完全没 alpha 味道，因为 gross 在 `15m` 还是正的**  
   这说明“加速更强、波动拖累更轻”的横截面排序，**不是纯随机噪声**；但它太薄，离 production 还很远。

4. **慢一点也没救回来**  
   我额外拿 `8` 个更液态币做了 `15m` cadence 复核：
   - `1h` rebalance：net `-1542.01 bps`
   - `2h` rebalance：net `-1189.94 bps`
   - `3h` rebalance：net `-1042.20 bps`
   - `4h` rebalance：net `-960.62 bps`

也就是说：
> **不是“调慢一点就过线”，而是当前这条 direct transfer 在 Binance perp short-cycle 上本来就太薄。**

---

## 7. 为什么这轮仍然值得收进素材池
因为它虽然当前不过线，但它补的是一个**很清楚的 raw alpha 骨架**，不是空洞因子名词：

### 7.1 它给了一个完整壳，不只是一个分数
repo 里已经把这些层都摆出来了：
- factor score
- cross-sectional blending
- regime scalar
- vol targeting
- hard stop
- turnover cost
- walk-forward

这对后续自己搭壳很有参考价值。

### 7.2 它补的是“carry / acceleration”这类缺口
最近 digest 里我们已经扫过很多：
- pairs / stat-arb
- spread fade
- lead-lag catch-up
- funding / basis
- single-asset MR

但这种：
> **用 price-based carry proxy 做 cross-sectional long-short**

还是相对少的。

### 7.3 它提醒了一个很实用的边界
不要看到 repo 里写了：
- `carry`
- `vol targeting`
- `regime filter`
- `walk-forward`

就自动把它当成“短周期可落地”。

这个 repo 更像：
> **一个中低频多因子教学壳，里面刚好藏着一条可被 desk 化的 raw alpha branch；但 direct short-cycle transfer 先不过成本。**

---

## 8. 策略拆解（必填）
- 方向属性：**cross-sectional / relative-value / carry-proxy / market-neutral**
- 基础 alpha：**短期斜率加速更强且 realised vol drag 更轻的币，下一段时间更可能相对跑赢**
- entry：**每次 rebalance 时 long top2 / short bottom2**
- exit：**下次 rebalance 平仓并重排**
- sizing：**等权 top2-bottom2，gross 1.0；后续可接 inverse-vol**
- risk：**可接 repo 里的 vol targeting / max weight / hard stop / corr penalty**
- cost：**repo 自带 turnover-based commission + slippage 壳；本轮粗测已显示它对换手极度敏感**
- regime / filter：**当前还没证明简单 slow-down 就够；更像需要额外 admission，而不是裸 rank 全时段开机**

---

## 9. 下一步怎么测
这条线不是该被直接扔掉，而是应该换一种更聪明的 desk 化方式：

### 9.1 不要再做“全时段、固定时钟、无脑重排”
下一轮优先加 admission：
- 只在 cross-sectional dispersion 足够大时开机
- 只在 top-vs-bottom score gap 超过 rolling percentile 时开机
- 只在全市场 realised vol 不过热时开机

### 9.2 把 `carry proxy` 从裸 rank 改成“alpha + veto”
例如：
- carry score 做方向排序
- funding / basis / OI crowding 做 veto
- liquidity shock / session pocket 做 admission

也就是把它从单独 alpha，升级成：
> **cross-sectional ranking core + crowding/liquidity admission**

### 9.3 先测更低换手版本，而不是继续压 `5m`
当前 first verdict 已经说明：
- `5m` 明显更差
- `15m` 还有 gross 影子

所以下一轮更合理的是：
- `15m signal`
- `5m execution`
- maker-first / passive rebalance

而不是继续把信号本身压得更快。

### 9.4 检查“carry proxy”是否只在某些币群有效
下一轮建议切分：
- majors vs liquid alts
- L1/L2 vs meme / beta-heavy names
- 亚洲 / 欧洲 / 美盘 session

很可能这条线只在某个更窄的 universe 里成立。

### 9.5 若要继续沿 repo 精神走，优先测单因子，不要急着回到 4-factor composite
原因很简单：
- `value / quality` 太慢；
- `momentum` 又会和现有材料池重叠更多；
- 当前真正新增的信息量，还是这条 `carry proxy` 的 short-cycle 可迁移性边界。

---

## 10. first verdict
我的判断是：

> **这份 repo 值得进 raw alpha 素材池，但不该被读成“又一个可直接照搬的 multifactor shell”；对当前 desk，真正该拿走的是 `vol-dragged acceleration carry rank` 这条 cross-sectional raw alpha branch。**

再短一点：

> **alpha 本体是“加速度减去波动拖累”的横截面排序；当前 Binance perp `15m/5m` 直译版 gross 还有、net 明显不过线，所以它更像待二次 desk 化的 raw alpha 候选，而不是现成 production shell。**

---

## 11. 来源
- `takahashi3899` (2026). *crypto-multifactor-strategy*.
  - Readable URL / Repo URL: <https://github.com/takahashi3899/crypto-multifactor-strategy>
  - API metadata: <https://api.github.com/repos/takahashi3899/crypto-multifactor-strategy>
  - Raw files:
    - <https://raw.githubusercontent.com/takahashi3899/crypto-multifactor-strategy/main/README.md>
    - <https://raw.githubusercontent.com/takahashi3899/crypto-multifactor-strategy/main/main.py>
    - <https://raw.githubusercontent.com/takahashi3899/crypto-multifactor-strategy/main/factors.py>
    - <https://raw.githubusercontent.com/takahashi3899/crypto-multifactor-strategy/main/signals.py>
    - <https://raw.githubusercontent.com/takahashi3899/crypto-multifactor-strategy/main/risk.py>
    - <https://raw.githubusercontent.com/takahashi3899/crypto-multifactor-strategy/main/backtester.py>
- Local public-data probe artifacts:
  - `reports/artifacts/quant_digests/2026-04-14_takahashi_carry_rank_probe.py`
  - `reports/artifacts/quant_digests/takahashi_carry_rank_probe_summary_2026-04-14.csv`
  - `reports/artifacts/quant_digests/takahashi_carry_rank_probe_detail_15m_2026-04-14.csv`
  - `reports/artifacts/quant_digests/takahashi_carry_rank_probe_detail_5m_2026-04-14.csv`
  - `reports/artifacts/quant_digests/takahashi_carry_rank_probe_asset_15m_2026-04-14.csv`
  - `reports/artifacts/quant_digests/takahashi_carry_rank_probe_asset_5m_2026-04-14.csv`
  - `reports/artifacts/quant_digests/takahashi_carry_rank_cadence_15m_subset_2026-04-14.csv`
