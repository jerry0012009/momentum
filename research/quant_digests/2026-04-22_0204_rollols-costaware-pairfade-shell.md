# 别把这份 crypto stat-arb repo 只读成“又一个 pairs 回归模板”：对 short-cycle crypto desk，更该先拆的是「rolling-OLS residual z-score fade × cost-aware notional scaling × split-local state machine」这条完整 raw alpha 壳
- 时间：2026-04-22 02:04 UTC
- 类型：2026 GitHub repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：先用 rolling OLS 估计两腿相对定价关系；当 residual / spread 的 z-score 偏离足够深时做 **long cheap leg / short rich leg**，赌价差向局部中枢回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / rolling-ols / residual-zscore / cost-aware-sizing / split-local-state / roll-slippage / Binance / 15m / 5m / repo / public-data
- 证据类型：工程实现 + repo 完整策略壳 + public-data first probe

## 1. 这次看了什么
这次看的是 2026 GitHub repo **Rah9742 / Crypto-Stat-Arb**。如果只看标题，它像一份普通的 crypto stat-arb 课程仓；但真正值得 desk 保留的，不是“pair trading 这四个字”，而是它把一条 **更接近可实盘研究流程的完整 shell** 写得很清楚：

1. **先做 pair admission**：rolling formation window 里评估 cointegration / hedge ratio 稳定性；
2. **再做 strategy sweep**：对 `formation / z-window / entry / exit / stop / max-hold` 做 train / validation / test；
3. **split-local state machine**：每个 split 内单独生成信号，不让 train 状态泄露到 validation / test；
4. **cost-aware position sizing**：不是所有 entry 都打满仓，而是看“预期回归幅度相对 round-trip cost 值不值”；
5. **最后单独重跑 cost stage**：用 Roll slippage 估计做 gross vs net 分离。

这比我们前面见过的很多 pairs repo 更像一个真正能进入 desk intake 的“研究骨架”。

## 2. 一句话核心结论
这篇东西的真正价值，不是再次证明“spread 会回归”，而是把 **pair MR 从信号研究推进到 cost-aware deployment shell**：

> **rolling residual z-score fade 这条 raw alpha 本身不新，但“split-local 防泄露 + cost-aware 缩仓 + asset-level Roll slippage”这一整套，明显比只写 `|z|>2 就进` 的 pairs 模板更有迁移价值。**

## 3. 它是怎么证明这点的
不是靠一句“我们做了 stat-arb”，而是直接把研究流程拆成可检查的代码和产物：

- `src/crypto_trader/signals/pairs.py`
  - `build_pair_research_frame(...)`：rolling OLS hedge ratio → spread → rolling mean/std → z-score
  - `generate_pair_signal_state(...)`：entry / exit / stop / max-hold 的状态机
  - `build_pair_target_notionals(...)`：把 **expected move / cost** 变成实际 target notionals
- `src/crypto_trader/analysis/pairs_research.py`
  - `build_split_local_signal_frame(...)`：在 warmup / train / validation / test 内分别生成信号，避免状态穿越
- `data/processed/pairs/strategy/pairs_comparison_summary.csv`
  - 给出 shortlisted pair 的 train/validation/test 指标
- `data/processed/costs/roll_slippage_summary.csv`
  - 给出 asset-level Roll slippage
- `README.md`
  - 明确区分原始 strategy sweep 与独立 rerun 的 cost-adjusted comparison

也就是说，这个 repo 不是“有个 idea”，而是把 **alpha → state → sizing → cost rerun** 这条链条都摆出来了。

## 4. base alpha 到底是什么
先把话说死一点：

- **base alpha 不是** “cointegration 这个词”；
- **base alpha 也不是** “cost-aware sizing”；
- 这篇东西的 **base alpha** 是：

> **当两腿 residual 相对其 rolling 中枢出现异常偏离时，做 spread mean reversion。**

剩下这些东西都属于“把 raw alpha 变得更像可交易系统”的二层组件：
- pair admission
- split-local state machine
- max-hold / stop
- cost-aware sizing
- Roll slippage cost stage

所以它符合这轮优先级：**raw alpha 候选，而且是能直接落地成完整策略的 raw alpha 壳。**

## 5. repo 里最值得学的，不是 pair entry，而是这三个细节

### 5.1 split-local signal frame：防止 state leakage
`build_split_local_signal_frame(...)` 的核心思想很朴素，但非常值得 desk 直接抄：

- `warmup / train / validation / test` 四段分开跑状态机
- 每段内部各自决定 entry / exit / holding period
- 不允许 train 的持仓状态直接“带进” validation / test

这件事听起来像卫生习惯，但很多 pair / trend 回测仓都没做干净。对 **有状态策略**（尤其是 MR 和 trailing stop）来说，这个细节很关键。

### 5.2 cost-aware target notionals：不是每个 z-score 都值得打满
repo 的 sizing 不是简单 fixed gross，而是：

- 先算 `expected_move ≈ (|z|-exit_z) × spread_std`
- 再除以当前 pair gross reference，得到一个近似 `expected_return`
- 再和 `round_trip_cost_rate` 比，得到 `cost_efficiency`
- 再结合 `conviction = min(|z| / entry_threshold, 2) / 2`
- 最后决定一个 `scale ∈ [cost_aware_min_scale, 1]`

翻成人话就是：

> **偏离没多深、预期回归没多厚时，哪怕信号触发了，也别默认打满。**

这和很多 pairs 研究的差别非常大。后者通常默认“信号是否交易”是二元的；这个 repo 则把它推进到“**信号有了，但 size 可以按 edge/cost 比例缩放**”。

### 5.3 cost stage 单独 rerun：gross / net 分开看
README 明确提醒：

- parameter sweep 里的 test return，不等于最终 cost rerun 的 net return；
- 选完策略后，会单独做一轮 Roll slippage rerun；
- 最终比较的是 gross/net/cumulative transaction cost 三套东西。

这个研究姿势是对的：
- **先找 alpha 壳**；
- **再问它能不能穿过成本**；
- 不要把两步混成一锅粥。

## 6. repo 自身给出的结果，说明了什么
README 的最终 headline：

- 最终 pairs 选中的是 **`AVAXUSDT / ICPUSDT`**
- cost rerun 后：
  - gross PnL `3816.84 USDT`
  - net PnL `2573.95 USDT`
  - gross return `38.17%`
  - net return `25.74%`
  - total transaction cost `1242.89 USDT`

更细一点看 `pairs_comparison_summary.csv` 里的最佳 run（`a00a6c7066b7`）：

- pair：`AVAXUSDT / ICPUSDT`
- formation `12096` bars
- z-score window `2016` bars
- entry `2.5`
- exit `0.25`
- max holding `48` bars
- test cumulative return `31.74%`
- test annualised return `113.06%`
- test Sharpe `1.34`
- test max drawdown `-29.82%`
- test trades `23`
- test win rate `56.5%`
- test mean trade pnl `137.99 USDT`

这组结果很有意思，因为它告诉我们两件事：

1. **pairs MR 在 repo 的 spot 样本里不是“靠高胜率小钱”活着**；
2. 它更像是 **trade count 不高，但单笔厚度足够**，再靠 max-hold 和 cost-aware sizing 把噪音削掉。

## 7. 为什么这轮值得写，而不是把它归进“又一篇 pairs”
我们最近确实已经写过不少 pairs / stat-arb，但这篇仍然值得保留，因为它补的是一个不同层级：

- 之前很多仓重点在 **admission / spread construction / entry-exit 规则**；
- 这篇重点在 **如何把 pair alpha 包成更真实的研究-部署壳**。

它最有迁移价值的，不是“AVAX/ICP 这对能不能继续赚钱”，而是下面这套方法论：

- **train / validation / test 分层挑参数**
- **split-local state generation**
- **cost-aware sizing instead of binary full-size**
- **独立 cost rerun**

这四块可以迁到：
- pairs
- basis fade
- spread residual basket
- cross-sectional loser→winner fade
- 甚至 trend 里的 re-entry / partial sizing

## 8. 这轮 public portability probe：迁到 Binance USDⓈ-M `15m/5m` 后像什么
为了不只复述 repo，我额外做了一个很轻的 public-data probe：

- 数据：Binance USDⓈ-M perpetual `AVAXUSDT / ICPUSDT`
- 周期：`15m` 与 `5m`
- 样本：最近约 `120d`
- 口径：沿用 repo 思路做 rolling-OLS residual z-score fade
- 但把窗口缩到更适合短样本 first verdict 的量级：
  - `15m`：formation `8064` bars，z-window `1344`，entry `2.5`，exit `0.25`，timeout `48`
  - `5m`：formation `12096` bars，z-window `2016`，entry `2.5`，exit `0.25`，timeout `48`

结果：

- `15m`
  - trades：`5`
  - avg gross：`+190.50 bps/笔`
  - win rate：`80.0%`
  - avg hold：`48.0 bars`
  - timeout rate：`100%`
- `5m`
  - trades：`43`
  - avg gross：`+10.57 bps/笔`
  - median gross：`-3.61 bps/笔`
  - win rate：`48.8%`
  - avg hold：`47.37 bars`
  - timeout rate：`97.7%`

我对这组 first verdict 的读法是：

### 8.1 `15m` 看起来“厚”，但样本太稀，而且几乎全靠 timeout
`15m` 的单笔 gross 很厚，但只有 `5` 笔，而且 **全部靠 timeout 才出来**。这更像：
- 偶尔出现的大 residual excursion 被吃到；
- 但不是一个已经成熟到可直接 child-exec 的高频 pocket。

### 8.2 `5m` 有交易频率，但厚度明显不够舒服
`5m` 有 `43` 笔，看起来比 `15m` 更像研究对象；但：
- 平均 gross 只有 `10.57 bps/笔`
- 中位数已经是负的
- 绝大多数交易还是靠 timeout 出场

也就是说：

> **在 perp `5m` 上，这条 residual fade 还没表现出“自然回中枢”的干净结构，更像是要么需要更强 admission，要么需要更厚 entry，要么干脆需要 maker-first / microstructure veto 才能成立。**

### 8.3 成本敏感度仍是第一风险
repo 自己给的 Roll slippage（15m，spot）是：
- `AVAX`：约 `4.32 bps`
- `ICP`：约 `11.31 bps`

如果按双腿 round-trip 粗看，单次完整进出就是 **低双位数到三十多 bps 量级的摩擦**。这当然不能直接照搬到 Binance perp，但它至少提醒一件事：

- `5m` probe 的 `+10.57 bps/笔` gross，**厚度明显不保险**；
- `15m` 虽然 gross 很厚，但 trade count 太低、timeout 过高，不像稳健 pocket。

所以当前 first verdict 不是“这条 alpha 死了”，而是：

> **raw alpha 还在，但短周期迁移后更像“需要更强 admission + 更真实 execution”的 sparse RV shell，而不是可以直接 taker 化的分钟级主策略。**

## 9. desk 最该怎么复用这篇东西
如果把这篇 repo 当作 desk 组件库，我最想保留的不是某个固定 pair，而是下面三层：

### 9.1 raw alpha 层
- rolling-OLS residual z-score fade
- entry：深偏离才进
- exit：center reclaim / stop / timeout

### 9.2 research hygiene 层
- split-local state machine
- validation evidence gate
- 不把 sweep return 和 cost rerun 混读

### 9.3 deployment shell 层
- cost-aware sizing
- gross exposure cap
- asset-level slippage rerun
- max-holding escape hatch

对我们当前素材池来说，这层壳不只服务 pairs，也很适合迁去：
- spot-perp basis fade
- perp-calendar spread fade
- cross-sectional residual baskets
- dual-anchor fair-value residual systems

## 10. 最小可复现实验
### 数据源
- Binance USDⓈ-M 公共 K 线：`/fapi/v1/klines`
- 标的：`AVAXUSDT / ICPUSDT`，后续可扩到 `SOL/ADA`、`XRP/DOGE`、`LTC/LINK` 一类替代 pair
- 公开性：公开可得
- 更新频率：分钟级
- 可映射周期：`5m / 15m`（如需更快可继续压到 `1m / 3m`，但要先补 execution realism）

### 最小实验口径
1. 用 rolling OLS 估 hedge ratio，构造 spread 与 z-score；
2. entry 先测 `|z| >= 2.5 / 3.0 / 3.5`；
3. exit 对照：
   - `|z| <= 0.25`
   - `|z| <= 0.5`
   - `timeout 24 / 48 / 96 bars`
4. admission 对照：
   - cointegration / p-value gate
   - hedge-ratio stability gate
   - spread-std / liquidity gate
5. execution/cost：
   - taker flat fee
   - maker-first
   - slippage ladder（`4 / 8 / 12 / 20+ bps` per round-trip per pair）
6. 统计：
   - `trade_count`
   - `gross_bps / net_bps`
   - `timeout_rate`
   - `center-reclaim rate`
   - `median trade bps`
   - `per-pair contribution`

## 11. 这轮我保留的判断
这份 repo 不是“最性感的新 alpha”，但它很适合进研究池，因为它补的是 **如何把 raw alpha 壳做得更像能部署的研究单元**。我当前更愿意把它定义成：

> **一条仍值得保留的 pairs raw alpha shell，但它真正的增量在 cost-aware deployment design，而不是在 pair entry idea 本身。**

再直白一点：

- 如果你想找“又一个 pair 入场规则”，这篇不是最该记住的；
- 如果你想找“怎么把 pair MR 做成更可靠的 research shell”，这篇很值。

## 12. 下一步怎么测
1. **先测更厚 entry**：`2.5 -> 3.0 -> 3.5`，看能不能明显降低 timeout-rate，别让交易几乎都靠 time-stop 出。
2. **把 admission 放到前面**：不要只看 z-score，要联合看 `hedge-ratio stability / spread volatility / liquidity`。
3. **做 maker-first 对照**：如果 `5m` gross 本来就薄，必须直接问 execution 能不能救，而不是继续假设 taker 也行。
4. **把 pair alpha 和 sizing 分开评估**：先看 fixed-size 是否有 edge，再看 cost-aware sizing 是否只是“把亏损缩小”，还是能真正改善 net efficiency。
5. **扩成多 pair pocket test**：优先找 alt-alt 里更容易出现稳定 residual excursion 的组合，不要被 `AVAX/ICP` 单一案例锁死。

## 13. 来源
- Rahman, R. (GitHub user `Rah9742`) (2026), **Crypto Trading Research Repo / Crypto-Stat-Arb**. Repo URL: <https://github.com/Rah9742/Crypto-Stat-Arb>
- Readable README URL: <https://raw.githubusercontent.com/Rah9742/Crypto-Stat-Arb/main/README.md>
- Source audit 文件：
  - `README.md`
  - `config/default.yaml`
  - `src/crypto_trader/signals/pairs.py`
  - `src/crypto_trader/analysis/pairs_research.py`
  - `data/processed/pairs/strategy/pairs_comparison_summary.csv`
  - `data/processed/costs/roll_slippage_summary.csv`
- 本地 artifacts：
  - `reports/artifacts/quant_digests/rollols_pairfade_probe_2026-04-22.py`
  - `reports/artifacts/quant_digests/rollols_pairfade_avax_icp_probe_2026-04-22.csv`
  - `reports/artifacts/quant_digests/rollols_pairfade_avax_icp_trades_2026-04-22.csv`
