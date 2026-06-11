# 别把 cross-market intraday TSMOM 继续只读成 shared gate：对 desk 更该先测的是「pseudo-session open leader continuation × spread-to-runner gate」完整 raw alpha
- 时间：2026-03-30 08:44 UTC
- 类型：2024 SSRN working paper + 2022 JFM accepted PDF + Binance USDⓈ-M Perpetual 公共 `15m` pseudo-session quick check
- 主题类型：raw alpha
- 基础 alpha：**pseudo-session 前 30 分钟的跨市场 leader continuation**；不是跟风做所有同向币，而是只做“最强 leader 自己的后续续行”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/cross-market/intraday/pseudo-session/leader-continuation/spread-gate/single-asset/session-close/btc/eth/sol/binance/perpetual/15m/5m/1m/3m/paper/public-data/cost
- 证据类型：working paper 证据 + 已发表 intraday TSMOM 地基 + 本地最小 transfer quick check

## 1. 这次看了什么
这次主看 **Dezhong Xu, Bin Li, Tarlok Singh, Jinze Li (2024)** 的 working paper **Cross-Market Intraday Time-Series Momentum**，并用 **Li, Sakkas, Urquhart (2022)** 的 *Intraday time series momentum* 当机制与日内持有到尾窗的地基。上次我们把这条线更多读成 shared gate；这次回到更值钱的主线：**它的 base alpha 其实是“会话前段最强 leader，若已经明显甩开 runner-up，后面往往还会继续领跑到会话尾段”。**

## 2. 核心结论
- **一句话核心结论：** 这篇东西最该进素材池的，不是“cross-market 可以做过滤”，而是**pseudo-session 开头出现的强 leader 本身就可能是一条可完整落地的单币 raw alpha**。
- **一句话说明它怎么证明：** Xu et al. 给出跨市场日内 lead-lag / TSMOM 框架；Li et al. 给出“前段信息冲击会延续到尾段”的 published 地基；本地 `BTC/ETH/SOL` 365d `15m` quick check 再把它压成可交易规则并直接看成本后留边。
- 本地 quick check（`00/08/16 UTC` 三段 `8h` pseudo-session）里，**只要求“至少 2/3 同向”是不够的**：持有到 session close 的 leader 组合，`n=1091`，毛收益 **-6.64 bps/trade**，按 `8 bps` round-trip 成本后约 **-14.64 bps**。
- **只要求 leader 自己前 30m 很强也还不够**：`lead >= 50 bps` 时，`n=394`，持有到 session close 毛收益只有 **+3.33 bps/trade**，成本后仍约 **-4.67 bps**。
- 真正值得测的是 **leader 强度 + 与 runner-up 的拉开幅度**：当 `lead >= 50 bps` 且 `leader - runner_up >= 40 bps`，`n=112`，持有 `12/24/30` bars 的毛收益分别约 **+10.34 / +16.96 / +24.16 bps**；按 `8 bps` round-trip 计，净值约 **+2.34 / +8.96 / +16.16 bps/trade**，session-close 版本命中率约 **59.82%**。
- 这说明对 short-cycle desk 来说，**cross-market breadth 本身不是 alpha，`dominant leader` 才更像 alpha 本体；spread-to-runner 是 admission gate，而不是装饰品。**

## 3. 为什么和当前项目有关
- 最近素材池里 pairs / carry / relative-value 已经很多，这篇正好补一张 **single-name intraday momentum** 的完整卡，而不是再补一层解释型 filter。
- 它和 `1m/3m/5m/15m` 的关系很清楚：先用 `15m` 把 `8h` pseudo-session 结构钉住，再把同一逻辑压缩到 `5m` 做更早 entry；不是一上来就在 `1m` 硬追。
- 这条线也比“泛泛看 leader-basket”更可执行：**交易对象只有 1 个 leader，entry/exit/cost 都更干净，组合实现也更轻。**

## 3.5 策略拆解（必填）
- 方向属性：单币顺势 / cross-market confirmed intraday leader continuation
- 基础 alpha：pseudo-session 前 30 分钟最强 leader 的后续续行
- regime：`00/08/16 UTC` 的 `8h` pseudo-session；首 `2x15m` bar 内至少 `2/3` 主流币同向
- filter / veto：leader 首 30m signed return `>= 50 bps`，且相对 runner-up 的 signed spread `>= 40 bps`；否则不做
- risk / sizing / execution overlay：
  - universe：`BTCUSDT / ETHUSDT / SOLUSDT` perpetual
  - entry：第 2 根 `15m` 收盘确认后、下一根开盘入场 leader 同方向
  - exit：基础版持有到 session close（更保守可先测 `24` bars）
  - sizing：单笔固定风险 `0.75R~1.0R`，单 session 只开 1 个 leader 槽位
  - stop：先用 `1.2 x` 首 30m 区间宽度或 `1.5 ATR(20)` 二者较紧者
  - cost：先按 round-trip `8 bps` 做诚实基线，再单独测 maker/taker 分层

## 4. 可复刻的最小实验
- **研究假设**：在 major perp 里，session-open 的 dominant leader 会把前 30m 的优势继续带到 session 尾段；但若只是“大家都涨/跌”，而没有 leader 与 runner-up 的明显拉开，则 edge 不足以覆盖成本。
- **一个可计算定义**：
  1. 把 24h 切成 `00/08/16 UTC` 三个 `8h` pseudo-session；
  2. `lead_ret_i = close[t=30m] / open[t=0] - 1`；
  3. 只保留首 30m 里至少 `2/3` 同向的 session；
  4. 取 signed return 最大的资产为 leader；要求 `lead_ret >= 50 bps` 且 `lead_ret - runner_up >= 40 bps`；
  5. 第 3 根 bar 入场，同向持有到 `24` bars 或 session close。
- **最小回测切口**：`BTC/ETH/SOL` perpetual，近 `365d`，`15m`；先看 `session-close` 版本，再下钻到 `5m` 做更早 entry。
- **最先看哪 1~2 个指标**：`net_bps_per_trade`、`hit_rate`；第三个再看 `trade_count / month`。

## 5. 风险与保留意见
- Xu et al. 目前仍是 working paper；而且本地 quick check 只用了 `BTC/ETH/SOL` 三资产代理，不是完整 cross-market universe。
- edge 很明显是**稀疏 pocket**，不是全天候 alpha：`n=112 / 365d` 说明它更像“有条件才出手”的稀疏 leader trade。
- 当前阈值 `50 / 40 bps` 是 `15m` 口径的第一版；迁移到 `5m` 时更合理的做法是改成 rolling vol/ATR 分位，而不是机械照抄 bps。
- 这条线很可能和宏观时钟、资金费率窗口、ETF/美股共振时段重合；后续要做 event-blackout 与 crowded-session 去偏，不然容易把宏观事件收益误记到纯技术 alpha 头上。

## 6. 来源
1. **Xu, D., Li, B., Singh, T., & Li, J. (2024). _Cross-Market Intraday Time-Series Momentum_. SSRN Working Paper.**
- DOI: `https://doi.org/10.2139/ssrn.4765613`
- Earlier DOI: `https://doi.org/10.2139/ssrn.4651331`
- Readable URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4765613`
- Repo URL: N/A

2. **Li, Z., Sakkas, A., & Urquhart, A. (2022). _Intraday time series momentum: Global evidence and links to market characteristics_. Journal of Financial Markets, 57, 100619.**
- DOI: `https://doi.org/10.1016/j.finmar.2021.100619`
- Readable URL: `https://www.sciencedirect.com/science/article/pii/S138641812100001X`
- Accepted PDF: `https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf`
- Repo URL: N/A

3. **本地最小 transfer quick check（公开行情）**
- 数据：Binance USDⓈ-M perpetual 公共 `15m` klines，`BTCUSDT/ETHUSDT/SOLUSDT`
- 口径：近 `365d`，`00/08/16 UTC` pseudo-session，entry 在首 `30m` 之后
- 结果文件：
  - `reports/artifacts/literature/tmp_crossmarket_intraday_tsmom_leader_session_summary_2026-03-30.csv`
  - `reports/artifacts/literature/tmp_crossmarket_intraday_tsmom_leader_session_events_2026-03-30.csv`

## 7. 下一步怎么测
1. 先固定 `15m` 版 pseudo-session 规则，只测 `leader >= 50 bps` 与 `spread_to_runner >= {20,30,40,50}` 四档；
2. 再把 exit 从 `session close` 改成 `12/24/30` bars 做 OOS，确认这不是只靠尾盘一小段；
3. 若 `15m` 成本后仍留边，再把同一状态机压到 `5m`：session 仍按 `8h`，但 entry 改成第 `6` 根 `5m` bar 后；
4. 若 `5m` 结果恶化，就把这条线正式定为 **`15m` 主信号 + `5m` execution timing**，不要硬伪装成 `1m` alpha。