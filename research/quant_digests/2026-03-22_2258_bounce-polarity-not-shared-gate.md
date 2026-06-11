# 别把 retest 后那根 bounce candle 写成“必须收阳/收阴”：`same-direction body` 在 15m 更像 late-chase，不是 Fib / EMA / breakout-short 的 shared hard gate
- 时间：2026-03-22 22:58 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/bounce-candle/body-polarity/reclaim/confirmation/filter/repo/crypto/15m
- 证据类型：仓库实现 + 本地最小复核

## 1) 这次看了什么
这轮主看一个很新的仓库 **TheVision333 / trading-bot (2026)** 里 `retest_signals.py` 的一个小分支：
> breakout 之后，回踩再收回去那根 bounce candle，是否必须是**同方向实体**（long 要阳线、short 要阴线）？

这不是 repo 里最显眼的 headline 规则，但它很像我们 desk 容易顺手照搬的“确认层小审美”。我用 `BTC/ETH/SOL` 的 Binance Spot 公共 `15m` 数据做了一个最小 proxy check：先用 `20-bar` 前高/前低突破 + breakout bar `body%/CLV` 找 breakout，再看 `8` 根内 retest→close reclaim，比较 **有无 same-direction body** 的后续 first-hit 表现。

## 2) 核心结论（先说人话）
- **一句话结论：** `bounce candle 必须收阳/收阴` 不该直接升成 `Fib retest_hold / EMA continuation / breakout-short follow-up` 的 shared hard gate；在 15m proxy 里，它整体更像 **更晚、更激进的追单**。  
- **一句话证据：** repo 只是把这条规则写进状态机；而本地快检显示，带同方向实体的 bounce 并没有让 retest 后路径更“干净”，反而把 pooled continuation 压低、fail 拉高。

### 关键数据点（本地最小快检）
样本口径：`BTCUSDT / ETHUSDT / SOLUSDT`，Binance Spot 公共 `15m`，最近 `120d`；事件数 `n=1126`。

1. **pooled 上，same-direction body 比 plain close reclaim 更差**
   - `same_body=False`：`n=541`，`continue 40.7% / fail 57.7% / timeout 1.7%`
   - `same_body=True`：`n=585`，`continue 35.4% / fail 63.2% / timeout 1.4%`

2. **long 侧最明显，不像值得给 Fib / EMA long 直接加这道门**
   - `long, same_body=False`：`continue 43.1% / fail 55.1%`
   - `long, same_body=True`：`continue 32.7% / fail 65.1%`

3. **short 侧也没有 shared uplift，最多只是“几乎没帮助”**
   - `short, same_body=False`：`continue 38.3% / fail 60.2%`
   - `short, same_body=True`：`continue 37.9% / fail 61.5%`

4. **它更快给出判决，但快的是坏消息，不是更稳的确认**
   - `mean decision bars`：`same_body=False = 1.97`，`same_body=True = 1.60`

> 人话：第一根“看起来像样”的反弹/反抽实体，并不等于更好的 hold；它更像把你带进了更后手、也更容易被反打的位置。

## 3) 为什么这题比继续泛找更值得
它直接服务当前三条收口线，而不是岔开：
- **Fib confirmation / retest_hold**：这轮最直接帮的是这条线——别把“收回线 + 阳/阴实体”直接当诚实确认；
- **EMA / PSAR raw alpha focus**：如果 raw alpha 已经容易在回踩里被磨死，再加这条 gate 很可能只是把 entry 推迟到更差价位；
- **V3 breakout-short follow-up**：也顺手给 short 侧做了反证——long 风格的 bounce 审美，不该自动镜像到 breakout-short。

所以它不是离开主线，而是在帮 desk 删掉一个**看起来合理、但很可能是坏默认值**的小规则。

## 4) 最小可复现实验口径（建议下一步真测）
下一步不要把 `same-direction body` 再当 hard gate 继续写进规则，而是做一个很小的三臂 A/B/C：

1. **A = baseline close reclaim**
   - 只要求回踩后重新 `close back above/below level`
2. **B = close reclaim + same-direction body**
   - 也就是 repo 里的这条规则
3. **C = close reclaim + 2-close persistence**
   - 不看第一根 bounce 的颜色，改看“收回去后下一根有没有继续站住”

先只在：
- `Fib retest_hold long`
- `EMA continuation long`
上做 first pass；
统一比较：
- `post-cost expectancy`
- `false_follow_ratio`
- `trade_retention`
- `time_to_decision`

如果 `B` 继续像这轮 proxy 一样**更低 continuation、更高 fail**，就该把它从 shared gate 候选里直接划掉；若 `C` 更稳，再把确认从“看这一根像不像”改成“看收回去后能不能继续站住”。

## 5) 风险与保留意见
- 这轮是 **proxy event test**，不是完整 walk-forward 回测；
- breakout / retest 定义是为了快速检 repo 里的 branch idea，不是 production 规则；
- 用的是 Binance Spot 公共 `15m`，不是 perp 交易成本口径；
- repo 很新、star 很少，这轮真正值得偷的不是整套策略，而只是它把“bounce candle polarity”明确写成一个可单独验证的分支。

## 6) 来源
1. **TheVision333. (2026). _trading-bot_. GitHub Repository.**
   - Authors / Org: TheVision333
   - Year: 2026（created_at `2026-02-23`）
   - Title: trading-bot
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/TheVision333/trading-bot>
   - Repo URL: <https://github.com/TheVision333/trading-bot>
   - 关键文件：`strategy/retest_signals.py`
   - 最值得复用的点：不是整套策略，而是把 `bounce candle must be bullish/bearish` 单独写成可测试的状态机分支。

2. **Binance Open Platform. (2026). _Spot REST API – Kline/Candlestick Data_.**
   - Authors / Org: Binance
   - Year: 2026 access
   - Title: Kline/Candlestick data
   - Venue: Binance Developers Docs
   - DOI: N/A
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>
   - Repo URL: N/A

## 7) 产出文件（本轮）
- `scripts/build_quant_digest_bounce_polarity_proxy.py`
- `reports/artifacts/quant_digests/bounce_polarity_proxy_20260322/events.csv`
- `reports/artifacts/quant_digests/bounce_polarity_proxy_20260322/summary_by_bounce_polarity.csv`
- `reports/artifacts/quant_digests/bounce_polarity_proxy_20260322/side_summary.csv`
- `reports/artifacts/quant_digests/bounce_polarity_proxy_20260322/symbol_side_summary.csv`
- `reports/artifacts/quant_digests/bounce_polarity_proxy_20260322/metadata.json`
