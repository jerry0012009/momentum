# 别把这篇 BTC→ALT 传导论文只读成“市场微观叙事”：对 short-cycle crypto desk，更该先拆的是「BTC 冲击 × 低交易笔数 ALT 延迟跟随」这条 raw alpha
- 时间：2026-04-20 00:28 UTC
- 类型：2026 *Asia-Pacific Financial Markets* 论文全文 audit + Binance Spot `1m` 最近 `7d` 轻量 portability probe（`BTC/QKC/PIVX/CITY/BIFI/GNO`）
- 主题类型：raw alpha
- 基础 alpha：**当 BTC 在上一分钟出现足够大的方向性冲击时，交易笔数更低、反应更慢的小市值 ALT 往往会在接下来 `1~3m` 补跟；因此可以做“BTC 先动，低流动性 ALT 延迟同向跟随”的 lead-lag raw alpha**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/lead-lag/btc-alt/low-liquidity/trade-count/information-delay/spot-crypto/binance-spot/1m/3m/5m/paper/fulltext/public-data/cost/risk
- 证据类型：论文全文 + 公开现货数据快检 + 最小可执行策略重写

## 1. 这次看了什么
先回答 base alpha：**这不是 filter，不是宏观解释，更不是“BTC 会带动山寨”这种空话；它可以直接写成一条可交易 raw alpha。**

主材料是：
- **Tomoki Kurihara, Takuji Matsumoto (2026)**
- *Price Transmission from Bitcoin to Altcoins: High-Frequency Evidence and Implications for Trading Strategy*
- *Asia-Pacific Financial Markets*
- DOI：`10.1007/s10690-026-09589-z`

这篇 paper 本体做了三层事：
1. 用 Binance `1m` 数据检验 **BTC 收益是否会滞后传导到 ALT**；
2. 检验 **交易笔数更低的币，是否更容易慢半拍**；
3. 把这件事写成一个带 fee 的 **实际 trading simulation**。

对我们 desk 最值钱的读法，不是照抄“学术上证明了信息传导”，而是把它改写成一句更实盘的话：
> **如果 BTC 先在 `t-1` 出现冲击，而某个小币因为交易笔数少、信息反映慢，在 `t` 还没完全跟上，那下一两分钟它继续补涨/补跌的概率会更高。**

也就是说，这轮 intake 最值得保留的是：
- **母信号**：BTC 上一分钟冲击
- **交易对象**：低 trade-count ALT
- **交易方向**：跟随 BTC 冲击方向
- **alpha 本质**：信息传导延迟，而不是 ALT 自己的趋势信号

## 2. 核心结论
- **一句话结论：** 这篇 paper 最值得 intake 的不是“BTC 影响山寨”这件众所周知的事，而是它把这件事明确压缩成了一个 **可复现、可收费后评估、可继续工程化的 lead-lag raw alpha**：**BTC 先动，低交易笔数 ALT 后动，做后者的延迟补跟。**
- **一句话证据：** 论文里，`trade count` 与“即时反应强弱”指标在 Bull / Bear 两个 regime 下都显著正相关；同时 BTC→ALT 的 Granger 因果在所有样本对上都显著。最近 `7d` Binance Spot 轻量快检里，`QKC/GNO/PIVX` 也仍能看到 **lag1 强于 lag0** 或至少保留明显 1 分钟跟随痕迹。

最关键的数据点：
1. **论文的流动性-反应速度证据很硬。** 交易笔数的对数与 ISI（即时敏感度指标）相关系数在 **Bull = `0.561`、Bear = `0.483`**，对应 t 值 **`12.987` / `10.740`**，都显著到 `<1e-16`。翻成人话：**越活跃的币越不会慢半拍；越冷的币越容易被 BTC“带着走一拍”。**
2. **BTC→ALT 的方向性也不是嘴炮。** 论文 Table 3 里，Bull regime 下 **BTC→QKC F=`706.5`**、**BTC→GNO F=`2109.4`**、**BTC→PIVX F=`2003.9`**，Bear regime 也都极显著（多数 `<1e-16`）。
3. **策略层不是只有入场，没有出场。** 论文做了 fee-aware 二分类框架，最优阈值表现出一个很清楚的风格：**entry threshold 在 Bull/Crash 为 `0`，Sideways 为 `0.0001`；hold threshold 在三个 regime 都是 `-0.0001`。** 翻成人话就是：**入场不必太苛刻，但出场要更谨慎，避免被交易费来回磨死。**
4. **最近 `7d` spot 快检还没死。** 我用 Binance Spot `1m` 对 `QKC/PIVX/CITY/BIFI/GNO` 做了极轻量 probe：
   - `QKCUSDT`：平均每分钟成交笔数约 **`1.75`**，`corr(BTC_t, ALT_t)=0.0293`，但 `corr(BTC_{t-1}, ALT_t)=0.0641`
   - `GNOUSDT`：平均每分钟成交笔数约 **`1.81`**，`lag0=0.0348`，但 `lag1=0.1098`
   - 用最粗的 shock-follow 口径（BTC 前一分钟绝对收益超过 `97.5%` 分位时，同向做 ALT 下一分钟），`QKC/GNO/PIVX` 的 next-`1m` gross 仍有约 **`+5.0 / +5.0 / +4.9 bps`**

## 3. 为什么和当前项目直接相关
这条线和 desk 当前需求是直接对上的：
- 它是 **raw alpha**，不是解释层；
- 它天然适配 `1m / 3m / 5m`，不是只能日频/小时频；
- 它补的是最近 digest 相对少一点的 **lead-lag / 信息延迟** 素材；
- 它还能顺手服务于别的 raw alpha：
  - 做 **entry confirmation**：BTC 已先冲击、ALT 仍未完全反应，才允许追单；
  - 做 **router**：同样的 BTC shock，只优先交易 lag 更明显的币；
  - 做 **regime split**：trade-count 很高的大币，别硬套这条线；低活跃尾部币更像主战场。

更重要的是，它不是“我们也许可以试试”的空灵想法，而是已经有完整研究链条：
> 先有 delay 证据，再有 liquidity 解释，再有 fee-aware strategy simulation，再能被我们改写成更适合 desk 的最小实验。

## 3.5 策略拆解（必填）
- 方向属性：单资产 / 小篮子，lead-lag，方向跟随
- 基础 alpha：BTC 在 `t-1` 先发生冲击，低 trade-count ALT 在 `t~t+2` 继续向 BTC 冲击方向补跟
- entry：
  - 先看 `|r_BTC,t-1|` 是否超过阈值（如过去 `3d` 的 `97.5%~99%` 分位）
  - 再看 ALT 是否仍处于“未完全跟上”状态：
    - `sign(r_ALT,t-1) != sign(r_BTC,t-1)`，或
    - `|r_ALT,t-1| < k * |r_BTC,t-1|`（如 `k=0.3~0.6`）
  - 满足则按 `sign(r_BTC,t-1)` 在 `t` 开仓
- exit：
  - 最小版先用 **固定持有 `1m / 3m`**
  - 第二版按 paper 思路，用单独 `hold` 模型决定是否续持到 `t+2 / t+3`
  - 也可加“冲击已被 ALT 完成补跟”即平仓
- sizing：
  - 初版 equal risk / fixed notional
  - 单币权重与 `1 / realized_vol` 或 `1 / spread_proxy` 相关
  - 低流动性币需要更严 participation cap
- risk：
  - 不在超大点差、低盘口深度时段强做
  - 单币单次持有时间上限很短，防止 lead-lag 变成纯噪声回吐
  - 事件性异常（上所/下所公告、极端 news）单独 veto
- cost：
  - 这条线很吃实现成本；`1m` 裸 taker 很容易被吃掉
  - 更现实的是 **`1m` 母信号 + `3m/5m` child execution**，或 maker-first / queue-join

## 4. 可复刻的最小实验
### 4.1 数据源、公开性、更新频率、实验口径
- 论文数据源：Binance API `1m` close + trade count
- 本轮快检数据：Binance Spot 公共 `1m` K 线（无需私钥）
- 公开性：公开可得
- 更新频率：`1m`
- 最小实验口径：
  - universe：先从最近仍有交易、且 trade count 明显偏低的 ALT 开始，如 `QKC/PIVX/GNO/CITY/BIFI`
  - signal：`btc_shock = |r_BTC,t-1| > q97.5~q99`
  - admission：ALT 前一分钟尚未完全反应
  - direction：跟随 `sign(r_BTC,t-1)`
  - hold：`1m / 3m / 5m`
  - execution：先 `lag1`，避免同 bar 幻觉
  - 评估：gross bps、cost 后 bps、fill-rate、holding-time、shock-decay 曲线

### 4.2 本地 first verdict
这轮我补了一个 **最近 `7d` Binance Spot `1m` 轻量 probe**，不是完整回测，但足够判断“这条线今天还有没有影子”：

1. **低成交笔数币里，确实还有 lag1 > lag0 的现象。**
   - `QKCUSDT`：`lag0=0.0293`，`lag1=0.0641`
   - `GNOUSDT`：`lag0=0.0348`，`lag1=0.1098`
   - `PIVXUSDT`：`lag0=0.0232`，`lag1=0.0367`
2. **最粗糙的 shock-follow 版本已经能看到 gross 正值。**
   - 当 BTC 前一分钟绝对收益超过 `97.5%` 分位时：
   - `QKC/GNO/PIVX` 的 next-`1m` 同向跟随 gross 约 **`+5.01 / +4.99 / +4.90 bps`**
3. **但不是所有低活跃币都适合做。**
   - `CITY` 的 lag1 反而弱于 lag0；`BIFI` 也不明显
   - 说明这条线不是“任何小币都能吃”，而是需要 **pair / coin admission**

换句话说：
> **paper 的大逻辑今天还活着，但现实里更像“先选对 lag coin，再做 BTC shock follow”，而不是无脑全尾部轮动。**

## 5. 风险与保留意见
1. **这条线非常吃币种选择。** 不是所有 low-trade-count ALT 都会稳定滞后；有的只是噪声大。  
2. **这条线非常吃成本。** 论文能做 fee-aware simulation，但我们 desk 如果用 `1m` 裸 taker，毛 edge 可能直接没了。  
3. **现货成立，不等于 perp 也原样成立。** perp 里会多出 funding、盘口结构、做市商反应速度、合约活跃度差异。  
4. **它容易被“事件驱动假象”污染。** 某些币的跟随并不是 BTC 传导，而是自己正好有独立新闻。  
5. **当全市场一起 panic / squeeze 时，lead-lag 可能压缩。** 因为所有币都同步高频反应，延迟空间变小。  

## 6. 下一步怎么测
1. **先做 coin admission。** 不要全 universe 硬做；先按 `lag1-lag0`、Granger、mean trades/min 把候选币池排序，保留最像 `QKC/GNO/PIVX` 的一小篮子。  
2. **把最小规则版跑完整。** `BTC shock threshold × ALT underreaction gate × hold 1/3/5m × cost ladder` 全扫一遍，先找 gross 和 net 最稳的 pocket。  
3. **补 perp 迁移。** 对 Binance USDⓈ-M / 其它可交易 venue，测试是否能找到“仍有足够 lag、但手续费更友好”的 ALT perp 子集。  
4. **升级成双模型版。** 按 paper 思路拆成 `entry model` 和 `hold model`，输入先从 `[r_BTC,t-1, r_ALT,t-1]` 开始，再加 trade-count / spread / quote-volume proxy。  
5. **把它做成 shared router。** 未来即便不单独做这条策略，也可以拿它给 breakout / panic-reversal / event-driven 信号做 admission：**BTC 已先动但 ALT 还没完全动，才值得追。**  

## 7. 来源
1. **Kurihara, T., & Matsumoto, T. (2026). _Price Transmission from Bitcoin to Altcoins: High-Frequency Evidence and Implications for Trading Strategy_. Asia-Pacific Financial Markets.**  
   - DOI：`10.1007/s10690-026-09589-z`  
   - Readable URL：`https://doi.org/10.1007/s10690-026-09589-z`  
   - Springer page：`https://link.springer.com/article/10.1007/s10690-026-09589-z`
2. **Crossref metadata**  
   - `https://api.crossref.org/works/10.1007/s10690-026-09589-z`
3. **本地轻量快检产物**  
   - `reports/artifacts/literature/btc_alt_lag_spot_probe_2026-04-20.csv`

## 8. 本地产物
- Digest：`research/quant_digests/2026-04-20_0028_btc-alt-lagged-transmission-alpha.md`
- Probe artifact：`reports/artifacts/literature/btc_alt_lag_spot_probe_2026-04-20.csv`
- 预期页面：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-20_0028_btc-alt-lagged-transmission-alpha.html`
