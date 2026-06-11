# 别把这篇 2023 SSRN working paper 只读成“跨市场相关性”：对 crypto short-cycle desk，更该先测的是「8h session leader impulse × same-asset continuation」这条 raw alpha
- 时间：2026-04-10 02:48 UTC
- 类型：2023 SSRN working paper（DOI metadata）+ Binance USDⓈ-M `15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：`跨市场/跨资产的早段 price discovery 不会立刻结束；若某个 liquid major 在 8h pseudo-session 前 30 分钟明显领跑/领跌，随后 3~7.5 小时更容易继续沿原方向扩展`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-market / intraday / momentum / leader-laggard / continuation / BTC / ETH / SOL / 15m / 5m / paper
- 证据类型：论文线索 + 公开数据 portability probe

## 1. 这次看了什么
这次主看 **Dezhong Xu, Bin Li, Tarlok Singh, Jinze Li (2023), _Cross-Market Intraday Time-Series Momentum_**。它最容易被读成一句空话：市场之间会互相带动。但对我们 desk 更值钱的读法不是“把它当 shared gate”，而是先把 **`8h pseudo-session 前 30 分钟谁是 leader`** 单独拎出来，当一条可直接下单的 `15m` raw alpha。当前环境里 SSRN 正文被反爬挡住，所以我**不引用我没直接看到的论文表格数字**；证据主轴放在 DOI metadata + Binance 公共数据最小复现。

## 2. 核心结论
- **一句话核心结论：** 不是“有 leader 就都能追”，而是 **只有当 leader 在前 30 分钟已经跑出足够大的幅度，而且明显甩开 runner-up 时，leader 自己后面几个小时的 continuation 才更像可交易 alpha。**
- **一句话证明方式：** 我把 `BTC/ETH/SOL` 的 Binance USDⓈ-M `15m` 数据切成 `00:00/08:00/16:00 UTC` 三档 `8h` pseudo-session，先看前两根 `15m` 谁的绝对收益最大，再按 leader 同方向在下一根开盘进场，比较 `12/24/30` 根持有窗的成本前后收益。
- 若只要求“至少两币同向”（`aligned>=2`），这条线并不值钱：近 `365d`、约 `1020` 个 session 上，`12bar` 平均 gross 只有约 `-1.46bps`，粗扣 `8bps` round-trip 后约 `-9.46bps`。
- 但若只保留 **`lead>=50bps` 且 `领先 runner-up >=40bps`** 的强 session，结果会明显变样：近 `365d` 约 `116` 笔，`12bar` 平均 gross 约 `+15.23bps`、net 约 `+7.23bps`，胜率约 `58.6%`；`24bar` 仍约 `+0.59bps` net，`30bar` 基本打平（约 `+0.11bps` net）。
- 这说明更像 **“强 leader 早段冲击后的 3 小时 continuation”**，不是全天随便追。最佳持有窗当前更偏 `12bar=3h`，不是越长越好。
- 信号并不均匀：强 cohort 里约 `83/116` 笔是 `SOL` 做 leader，`32` 笔是 `ETH`，`BTC` 几乎没有；其中 `SOL` leader 的 `12bar` gross 约 `+25.47bps`，而 `ETH` leader 更像慢一点的延续，`12bar` 偏弱、`30bar` 才转好。**结论：这不是“BTC 带全市场”的老故事，更像 alt leader 的 intraday discovery / participation alpha。**

## 3. 为什么和当前项目有关
这条线和 `momentum` 当前主线是直接对口的，因为它补的是 **cross-market / relative-strength continuation** 素材，而不是再绕回 breakout / retest 细节：
- 它本体就是一条 `15m` 可下单 raw alpha，而不是只能做过滤器；
- 它天然适合 desk 的双层节奏：`15m` 负责定义 leader session，`5m` 负责做 child entry / execution；
- 它和我们最近的 funding fade、pairs mean reversion 是互补的：前者赚“拥挤回归”，这条赚“price discovery 继续扩散”。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / cross-market continuation
- 基础 alpha：`早段最强 leader 的方向延续`
- regime：`8h` pseudo-session 前 `30m` 已出现显著领跑/领跌
- filter / veto：`lead_bps >= 50`、`spread_vs_runner >= 40`、只做 `BTC/ETH/SOL` 等高流动 majors
- risk / sizing / execution overlay：下一根 `15m` 开盘进场；基线先持有 `12` 根 `15m`；每个 pseudo-session 最多一笔；先按 `8bps` round-trip 验活，再做 symbol 分层仓位与 `5m` child execution

## 4. 可复刻的最小实验
- **研究假设：** 若某个 liquid major 在 `8h` pseudo-session 前 `30m` 明显领先且拉开差距，它后面 `3h` 仍更容易续行。
- **一个可计算定义：**
  - 会话锚：`00:00 / 08:00 / 16:00 UTC`
  - `lead_bps_i = abs(close_t+30m / open_t - 1) * 1e4`
  - 选 `lead_bps` 最大者为 leader，方向取其符号
  - 仅当 `lead_bps >= 50` 且 `lead_bps - runner_up_bps >= 40` 时，在下一根 `15m` 开盘按同方向买/卖 leader
  - 基线出场：持有 `12` 根 `15m`；对照再看 `24/30` 根
- **最小回测切口：** Binance USDⓈ-M `BTC/ETH/SOL`，先跑近 `365d` 的 `15m`；然后把 entry 精炼成 `5m` 里的第一次同向小回踩/小盘整突破，比较是否能把 `12bar` 的净收益再抬高。
- **最该先看 2 个指标：**
  1. `post-cost mean bps/trade`
  2. `按 leader symbol 分层后的稳定性`（别让单一 `SOL` 贡献掩盖全局）

## 5. 风险与保留意见
- 当前环境下 SSRN 正文没有直接抓到，所以**不应把论文自身样本结论说成已完成全文复刻**；目前更像“paper-based hypothesis + public-data first verdict”。
- 结果明显集中在 `SOL` leader，说明这条线可能强依赖 alt participation，而不是全市场统一规律。
- pseudo-session 锚到 `8h` funding clock 是可解释的，但也可能带时间切分偏差；下一步必须做 `UTC rolling anchor` 或 `4h` 对照。
- 若把成本从 `8bps` 提到 `10~15bps`，`24/30bar` 的边际优势可能迅速消失，所以现阶段更像 **短持有 continuation**，不是全天趋势跟随。

## 6. 来源
1. **Xu, D., Li, B., Singh, T., & Li, J. (2023). _Cross-Market Intraday Time-Series Momentum_. SSRN Electronic Journal.**
   - DOI: `10.2139/ssrn.4651331`
   - Readable URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4651331`
   - DOI URL: `https://doi.org/10.2139/ssrn.4651331`
2. **Binance USDⓈ-M public market data**
   - Klines: `https://fapi.binance.com/fapi/v1/klines`
3. **本地 portability artifacts**
   - `reports/artifacts/literature/crossmarket_intraday_tsmom_leader_probe_summary_2026-04-10.csv`
   - `reports/artifacts/literature/crossmarket_intraday_tsmom_leader_probe_2026-04-10.csv`
