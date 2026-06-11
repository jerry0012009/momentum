# 别把 `go-trader` 里的 `range_scalper` 只读成“又一个布林带小指标”：对 short-cycle crypto desk，更该先拆的是「低波动静默区间 × band-touch fade」这条 raw alpha 壳
- 时间：2026-04-22 00:38 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `shared_strategies/range_scalper.py` + `shared_strategies/registry.py`）+ Binance USDⓈ-M public-data portability probe（8 个 liquid majors，`5m/15m`）
- 主题类型：raw alpha
- 基础 alpha：低波动、低成交量的窄幅区间里，价格触碰布林带边缘后更容易向区间中轴回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / mean-reversion / range / bollinger-band / rsi / low-volume / router / binance-perpetual / 5m / 15m / repo / public-data / cost / risk
- 证据类型：工程经验 + public-data portability probe

## 1. 这次看了什么
看的是 `richkuo/go-trader` 这个 2026 仍在活跃维护的仓。它不是单一策略 repo，但其中 `shared_strategies/range_scalper.py` 给了一个很清楚、很适合短周期 desk 拆开的 raw alpha 壳：先用 **Bollinger bandwidth 很窄 + 当前成交量低于均量** 定义“安静横盘”，再在 **触上/下轨 + RSI 极值** 时做反向回归。

## 2. 核心结论
- **一句话核心结论：** 这不是“所有 BB touch 都做”的老派均值回归，而是先要求市场进入“安静、拥挤、还没启动趋势”的窄箱体，再去吃边缘回摆。
- **一句话证明方式：** repo 直接把 alpha 写成可运行规则；我再用 Binance USDⓈ-M 8 个 liquid majors 做了 `5m/15m` 公开数据快检，看信号后几根 bar 的漂移与一个最小 midline-exit 壳是否站得住。
- repo 默认参数很直接：`bb_period=14`、`bb_std=1.5`、`bw_threshold=0.008`、`vol_ratio=0.8`、`rsi_period=7`、`rsi_ob/os=70/30`。它的真正价值不在 RSI，而在 **先做 range admission，再做边缘 fade**。
- `15m` 全池（8 majors，45d）一共只有 `70` 个信号，说明它本来就不是高频主引擎，更像 **high-selectivity range router**。按“下一根开盘进场、向 signal-bar `bb_mid` 回归、1R 对称止损、`4` bar timeout”的最小壳，gross 约 **`+7.67 bps/笔`**，胜率约 **`64.3%`**。
- `5m` 全池（30d）有 `376` 个信号，但同一最小壳 gross 只约 **`+0.59 bps/笔`**，明显太薄；更像 child execution / symbol router，而不是 taker 版 standalone alpha。
- pocket 很不均匀：`SOLUSDT 15m` 约 **`+24.2 bps/笔`**, `77.8%` 胜率；`BNBUSDT 15m` 约 **`+11.8 bps/笔`**；`LINKUSDT 5m` 约 **`+4.49 bps/笔`**。这说明它更像“**特定币种 + 特定 regime**”的 pocket，而不是 broad basket 同权策略。
- 但如果粗扣单笔 round-trip `8 bps` taker 成本，`15m` 全池基本只剩接近打平，`5m` 明显转负；所以 first verdict 不是“均值回归成立了”，而是 **range admission 这层值得保留，但 execution 不能太粗糙**。

## 3. 为什么和当前项目有关
这条线和 desk 现在的意义很直接：它补的是 **raw alpha 素材池里的“静默区间回摆”**，不是又一个趋势/突破模板。对我们现在的 `1m/3m/5m/15m` 短周期研发，更值钱的不是“BB+RSI”四个字，而是这句拆法：

1. 先判断现在是不是 **窄波动、低参与度、未展开趋势的箱体**；
2. 再在箱体边缘做 **band-touch fade**；
3. 最后把它和已有趋势/突破 alpha 做 **router / veto** 分工，而不是混成一锅。

换成人话：有些时候价格碰上轨/下轨不是要追，而是说明它在一个很安静的小箱子里“撞墙了”，这时候更适合赌它弹回中间。

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 单资产 mean reversion
- 基础 alpha：low-volatility range oscillation × band-touch fade
- regime：Bollinger bandwidth 压缩 + 当前量能低于均量
- filter / veto：RSI 极值确认；若 bandwidth 扩张或放量，不做 fade
- risk / sizing / execution overlay：更适合 maker-first / passive reversion；可加 `midline TP + timeout + spread/fee veto`

## 4. 可复刻的最小实验
**研究假设：** 当 `bb_bandwidth < 0.008` 且 `volume < 0.8 * vol_sma` 时，边缘触带后的回归胜率会显著高于不加 range admission 的普通 BB fade。

**一个可计算定义：**
- long：`close` 下穿 `bb_lower`，且 `RSI(7) < 30`，且 `in_range=True`
- short：`close` 上穿 `bb_upper`，且 `RSI(7) > 70`，且 `in_range=True`
- 最小壳：下一根开盘入场；目标 `signal-bar bb_mid`；止损设为与目标距离对称的 `1R`；`15m` 先测 `4~6` bar timeout，`5m` 先测 `6~12` bar timeout
- 样本：Binance USDⓈ-M `BTC/ETH/SOL/XRP/DOGE/ADA/LINK/BNB`，最近 `45d`，主看 `15m`，`5m` 作为 child 版
- 最该先看：**gross bps/笔**、**成本后 bps/笔**，其次看 `midline_hit_rate`

## 5. 风险与保留意见
- 这是很典型的 **regime-sensitive** alpha：只要横盘结束、趋势启动，fade 会被一脚踩穿。
- repo 只给了信号层，没有把 exit / sizing / fee / maker-fill 讲完整，所以我不把它算作“可直接上线的完整策略”。
- 这类信号天然容易被手续费吃掉；如果不做被动挂单、spread 过滤、symbol 选择，广谱 taker 版大概率不值得。
- 因为信号数不多，`15m` 的好看 pocket 需要继续做 rolling 与 OOS，不要直接把 `SOL` 的近期表现当稳定事实。

## 6. 下一步怎么测
1. 做 **A/B**：`range_scalper admission` vs 普通 `BB touch + RSI`，直接比较 `gross/net bps`。
2. 给 `15m` 壳补 **maker-first 假设**：只统计可在下一根内以 `entry ± 0.5~1 tick` 被动成交的样本，看 net 是否能真正转正。
3. 做 **symbol router**：只保留 `SOL/BNB/LINK` 这类更厚 pocket，检验它是不是可迁移 pocket，而不是偶然样本。
4. 把这层 `in_range` gate 反向借给已有 breakout / trend alpha：箱体里别追突破，箱体外再追。

## 7. 相关产物
- Probe summary：`reports/artifacts/quant_digests/range_scalper_probe_summary_2026-04-22.csv`
- Event/trade 明细：`reports/artifacts/quant_digests/range_scalper_probe_{events,trades}_<SYMBOL>_<INTERVAL>_2026-04-22.csv`

## 8. 来源
- Rich Kuo. (2026). **go-trader**. GitHub repo.  
  Repo URL: `https://github.com/richkuo/go-trader`
- Source file: `shared_strategies/range_scalper.py`  
  Readable URL: `https://raw.githubusercontent.com/richkuo/go-trader/main/shared_strategies/range_scalper.py`
- Source file: `shared_strategies/registry.py`  
  Readable URL: `https://raw.githubusercontent.com/richkuo/go-trader/main/shared_strategies/registry.py`
- Source file: `README.md`  
  Readable URL: `https://raw.githubusercontent.com/richkuo/go-trader/main/README.md`
