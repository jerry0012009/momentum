# 别把这份今天新建的 Kraken Frost repo 只读成 hackathon demo：对 short-cycle desk，更该先测的是「Asian-session 20-bar MA deviation fade × ATR/trend veto × mean-target exit」这条完整 raw alpha——但代码阈值口径明显比注释更紧，edge 很薄且强依赖低成本

- 时间：2026-04-04 09:05 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `src/frost_kraken.py` + `src/agent.py` + `test_frost.py`）+ Kraken 公共 `15m` recent-window 最小便携性快检（2026-03-27 21:00 UTC ~ 2026-04-04 09:00 UTC，`XBTUSD/ETHUSD`）
- 主题类型：raw alpha
- 基础 alpha：**亚洲时段里，若价格相对 `20 x 15m` 均线出现“足够大、但又没大到 breakout”的偏离，且波动不过热、斜率不显著趋势化，则反手做均值回复，目标吃掉约 `80%` 的回归路径。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/single-asset/asian-session/ma-deviation/range-condition/atr-filter/trend-slope-veto/mean-target/time-stop/kraken-spot/btc/eth/15m/5m/3m/1m/repo/public-data/cost/risk
- 证据类型：repo 源码证据 + 公共数据最小便携性快检

## 1. 这次为什么选它

这轮我刻意没有继续补 pairs / funding / OBI，而是补一条**最朴素、最能直接落地的单币均值回复壳**。

原因很简单：

> **它不是 filter，不是 overlay，而是一条从 entry / exit / risk / timeout 都写出来了的完整 raw alpha。**

而且它是今天刚建的新 repo，主题又正好贴着我们默认关心的 `15m`：

- 只做 `15m`
- 只盯 `XBTUSD / ETHUSD`
- 只在 `00:00–05:30 UTC` 入场
- 只在“偏离均线但不是强趋势”时反手

对 short-cycle desk 来说，这种材料的价值不在于“复杂”，而在于：

> **它足够清楚，能最快做最小实验。**

## 2. 先回答最重要的一句：base alpha 是什么？

一句话版：

> **base alpha 就是：亚洲时段里的中等幅度偏离，不追，反而做回均线。**

更具体一点：

1. 用 `20` 根 `15m` K 线算均线；
2. 如果当前价格离均线够远，说明短时拉开了；
3. 但如果又远到像趋势启动 / breakout，那不碰；
4. 再用 ATR 和最近 10 根的线性斜率排除“太吵”或“太顺”的环境；
5. 最后赌价格回去吃掉约 `80%` 的偏离距离。

所以这轮主题非常明确：

- **不是**“AI agent 自动交易”
- **不是**“Kraken 接口工程”
- **而是**一条**session-bound mean reversion raw alpha**

## 3. repo 真正给了哪些完整策略部件

### 3.1 Entry
`src/frost_kraken.py` 的入场骨架非常完整：

- 频率：`15m`
- 标的：`XBTUSD`、`ETHUSD`
- 时段：`00:00–06:00 UTC`，但 `05:30 UTC` 后禁止新开仓
- 均线：`MA_PERIOD = 20`
- 波动过滤：`ATR_PERIOD = 14`
- 趋势过滤：最近 10 根收盘价做线性拟合，若绝对 slope 超阈值就跳过
- 方向：
  - 价格高于均线太多 → `SELL`
  - 价格低于均线太多 → `BUY`

### 3.2 Exit
源码不是“看对了就一直拿”，而是直接写了完整退场逻辑：

- **TP**：吃掉约 `80%` 的回均线路径
- **SL**：在偏离距离外再多给一个 buffer
- **最低 RR**：`MIN_RR = 0.4`
- **最长持有**：`MAX_CANDLES_HOLD = 16`

换成人话：

> 这不是纯主观“均值总会回来”，而是一个**有止损、有目标、有 time stop** 的完整壳。

### 3.3 Sizing / Risk / Cost
repo 里 sizing 很简单：

- `agent.py` 默认 `volume = 0.001`
- 没有 fancy allocator
- 但风险骨架已经有：`SL / TP / RR / cutoff / session filter`

这对我们反而是优点：

> 第一版复现不需要先卷仓位优化，先验证 alpha 是否存在即可。

## 4. 这份 repo 最值钱、也最该警惕的地方

### 4.1 值钱的地方：它真的是一条完整 raw alpha
它满足这轮优先级里最重要的几项：

- 能独立跑
- 能直接写成策略
- 不是只给一个 filter
- 数据公开可得
- 与 `15m` 直接贴合

### 4.2 最该警惕的地方：代码阈值和注释口径不一致
这是这轮最值得摘出来的一点。

repo 注释写的是：

- `MIN_DEVIATION_PIPS = 50` ≈ BTC 偏离 `$50`
- `MAX_ATR_PIPS = 600` ≈ ATR `$600`

但源码同时又写了：

- `POINT_MAP["XBTUSD"] = 0.1`
- `POINT_MAP["ETHUSD"] = 0.01`
- 偏离计算方式：`deviation = (current_price - ma_value) / point`

这会导致实际口径变成：

### BTC (`point = 0.1`)
- `MIN_DEVIATION_PIPS = 50` 实际只等于 **$5**
- `MAX_DEVIATION_PIPS = 1000` 实际只等于 **$100**
- `MAX_ATR_PIPS = 600` 实际只等于 **$60**

### ETH (`point = 0.01`)
- `MIN_DEVIATION_PIPS = 50` 实际只等于 **$0.50**
- `MAX_DEVIATION_PIPS = 1000` 实际只等于 **$10**
- `MAX_ATR_PIPS = 600` 实际只等于 **$6**

也就是说：

> **如果只看 README / 注释，你会以为它在抓“大偏离回归”；但按真实代码口径，它抓的是更细、更容易被手续费吃掉的短偏离。**

这点非常关键，因为它直接决定：

- 交易频率会不会过高
- 触发是不是太容易
- 最终是 raw alpha，还是被 costs 吃成假象

## 5. 最小便携性快检：最近 721 根 Kraken `15m` 上，这条线到底厚不厚？

我按 repo 的真实代码口径，做了一个 recent-window 粗快检：

- 数据：Kraken public OHLC
- 标的：`XBTUSD`、`ETHUSD`
- 时间：`2026-03-27 21:00 UTC ~ 2026-04-04 09:00 UTC`
- 口径：
  - 只在 `00:00–05:30 UTC` 开仓
  - 下一根开盘入场
  - 之后按 `TP / SL / 最长 16 根` 出场
  - 成本先看 round-trip `4 / 8 / 12 bps`
- 工件路径：
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/kraken_frost_recent_720bar_probe/summary.json`

### 5.1 BTC：gross 还行，但 4bps 后就翻负
`XBTUSD` 结果：

- 交易数：`16`
- 胜率：`68.8%`
- gross：`+36.8 bps`
- `4bps` round-trip 后：`-27.2 bps`
- 单笔平均 gross：`+2.30 bps`

翻成人话：

> **BTC 这条线在最近样本里方向不算错，但厚度太薄，连 4bps round-trip 都扛不住。**

### 5.2 ETH：gross 更好，但也只在很低成本下勉强存活
`ETHUSD` 结果：

- 交易数：`39`
- 胜率：`79.5%`
- gross：`+194.3 bps`
- `4bps` round-trip 后：`+38.3 bps`
- `8bps` round-trip 后：`-117.7 bps`
- 单笔平均 gross：`+4.98 bps`

所以 ETH 的结论不是“能上实盘”，而是：

> **如果你真能拿到很低的总成本，这条壳在 ETH 上还值得继续测；但只要成本往上抬一点，edge 很快就没了。**

### 5.3 这份 recent probe 真正告诉我们的是什么
不是“Frost 可直接上线”，而是：

1. **它不是完全没东西**——因为两边胜率都不差；
2. **但 edge 真的很薄**——尤其 BTC；
3. **它更像低成本均值回复壳，而不是高摩擦环境也能随便跑的 alpha。**

## 6. 这条主题和当前 desk 的关系

它为什么比继续补一个 filter 更值得？

因为它直接补的是当前素材池里始终应该保留的一类：

> **简单、可独立、可完整落地的单币 raw alpha 壳。**

我们最近 intake 了很多：

- pairs / stat-arb
- carry / funding
- cross-sectional
- microstructure

这些都重要，但如果没有一批像 Frost 这样足够“笨但能跑”的单币 raw alpha，对比就不完整。

这条材料最适合放在：

- **15m 单币均值回复 sleeve**
- 以及后续 `5m` transfer 的基础模板

## 7. 和 `1m / 3m / 5m / 15m` 的关系怎么理解

### `15m`
这是原生战场。

不要硬把它改写成别的东西：

- `20 x 15m` 均线 = 5 小时上下的锚
- 亚洲时段约束也是围绕 `15m` 写的
- 最大持有 `16` 根 = 最多约 4 小时

### `5m`
可以迁移，但要**保时间长度，不要只保 bar 数**。

也就是：

- 如果 `15m` 用 `20` 根均线 ≈ 5 小时
- 那 `5m` 第一版更该先试 **`60` 根均线**，而不是机械地继续 `20` 根
- `MAX_CANDLES_HOLD = 16` 对应约 4 小时，所以 `5m` 第一版更该先试 **`48` 根**

### `3m / 1m`
不建议直接把这套原封不动搬下去。

更合理的读法是：

- `3m / 1m` 可把它降级成 **HTF mean-reversion context**
- 也就是：
  - 当前价格是否已显著偏离 5 小时锚
  - 当前是不是 range 而不是 trend
  - 当前是不是已经太晚，不再开新仓

## 8. 我对这条材料的结论

### 8.1 值得 intake 吗？
**值得。**

因为它满足：

- raw alpha
- 可独立复现
- 能直接落成完整策略
- 数据公开可得
- 与当前 `15m` desk 足够贴近

### 8.2 现在就能当 production 吗？
**不能。**

原因也很明确：

1. 代码阈值和注释口径不一致；
2. 最近窗口里 BTC 明显过薄；
3. ETH 也只在低成本假设下勉强活；
4. 目前只有 repo 工程证据，没有严肃 walk-forward 证据。

### 8.3 最准确的 desk 化定位
我会把它定位成：

> **中优先级 raw alpha 候选：先做“参数口径纠偏 + 低成本生存线”验证，再决定是独立 alpha，还是降级成 mean-reversion sleeve 的 context shell。**

## 9. 下一步怎么测

### 实验 A：先修阈值口径，再跑一次
第一优先不是优化，而是**修口径**。

至少要做两版并排：

- **版本 1：按 repo 当前真实代码口径**
- **版本 2：按注释意图重标阈值**
  - BTC 先把偏离和 ATR 阈值整体上调 10 倍做对照
  - ETH 单独重新标定，不要直接照搬 BTC 口径

目的：

> 看这条 alpha 到底是“真有 edge”，还是靠过紧阈值制造高频假繁荣。

### 实验 B：做成本生存线
最小网格：

- 资产：`BTC / ETH`
- 成本：`2 / 4 / 6 / 8 / 10 / 12 bps` round-trip
- 入场偏离：当前值、`1.5x`、`2x`
- 时间止损：`8 / 12 / 16 / 24` 根

通过条件：

- 至少找到一块区域在 `>= 6 bps` 成本下还能活
- 否则就别把它当 production alpha，只能当研究素材

### 实验 C：做 `15m -> 5m` 保时长迁移
不要机械搬参数。

先试：

- `MA`: `20@15m` → `60@5m`
- `max hold`: `16@15m` → `48@5m`
- session 仍保持 `00:00–05:30 UTC`
- 再比较：
  - slope veto 是否要更严
  - deviation 是否要用 ATR-normalized，而不是绝对价差

### 实验 D：如果独立 alpha 不够厚，就降级成 context shell
如果最后发现：

- 单独跑收益太薄
- 但它能明显分出“range 可做 / trend 别碰”

那就不要硬撑 raw alpha 身份，直接降级成：

- `15m` mean reversion 的 context gate
- 或者别的反转策略的 allow/deny 层

这依然有价值。

## 10. 参考资料

1. **rkchellah. (2026). _QuantifyX_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/rkchellah/QuantifyX>  
   - Repo URL: <https://github.com/rkchellah/QuantifyX>

2. **Repo source files used in this digest**  
   - README: <https://raw.githubusercontent.com/rkchellah/QuantifyX/main/README.md>  
   - Frost strategy: <https://raw.githubusercontent.com/rkchellah/QuantifyX/main/src/frost_kraken.py>  
   - Agent loop: <https://raw.githubusercontent.com/rkchellah/QuantifyX/main/src/agent.py>  
   - Test harness: <https://raw.githubusercontent.com/rkchellah/QuantifyX/main/test_frost.py>

3. **Kraken Spot OHLC API**  
   - Venue: Kraken public API  
   - DOI: N/A  
   - Readable URL: <https://docs.kraken.com/api/docs/rest-api/get-ohlc-data/>  
   - Endpoint used in repo / probe: <https://api.kraken.com/0/public/OHLC>
