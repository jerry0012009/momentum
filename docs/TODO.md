# TODO

> 这是 `jerry/momentum` 当前的人类可读项目板。
> bot2 / bot3 的固定规则看 `docs/BOT2_BOT3_POLICY.md`；运行状态看 `docs/BOT2_BOT3_STATE.md`。
> 若本页摘要与 runtime 有出入，以 `docs/BOT2_BOT3_STATE.md` 为准。

## TRADING DESK BOARD

> Last review: 2026-05-10 03:34 UTC

### Paper / 待开启自动运行
- none

### Paper / 正在自动运行
- ~~Rank 32b~~ — 永久停用 (2026-05-04)：lookahead bias + warmup inflation；详见 `research/strategy_review/2026-05-04_rank32b_decommission.md`
- ~~Rank 154 / Crypto-Stat-Arb~~ — **已归档 / no-go** (2026-05-10)：原 combined carry+momo+breakout 长历史失败；154b funding-only young-coin lead 有轻微 price IC，但扣 funding / 真实成本后不过关。入口：`docs/RANK154_ARCHIVE_CLOSEOUT.md`，网页：`paper/rank154_archive_closeout.html`。
- EMA / PSAR raw alpha focus
- Rank 151 / EWMAC breakout band-pass gate
- Rank 2 / Rank 17 / Rank 29 / narrow paper lanes
- Rank 122 / paper sidecar

### 当前前排摘要
- 当前 active P2：`Rank 441 / 7d vol-scaled TSMOM × shared cost budget`
  - 以 `docs/BOT2_BOT3_STATE.md` 为 runtime truth。
  - 下一步 admission 聚焦 child execution、ETH 是否剔除、真实 friction/time/parameter stability。
- `Rank 154 / Crypto-Stat-Arb` 已关闭，不再是 active P2 / release candidate。
  - 原 Rank154：`ARCHIVED / failed release candidate`
  - Rank154b：`ARCHIVED / research lead only / no paper lane`
  - 不再做原 combined 权重、buffer、TopN、holding period 参数优化。
- 当前 fresh intake：open / 以 `docs/BOT2_BOT3_STATE.md` 为准。
- Background pool：不自动回前排。

### 当前 desk 判断
- `Rank 154 / Crypto-Stat-Arb` 的 P2/P3 路径已正式关闭：旧 paper runner 与网页仅作为历史证据保留，不代表当前可推进状态。
- 当前队列应回到 runtime state 的 active P2 / survivor / fresh intake，不应继续把 154 当作 release gate 候选。
- 若未来重新研究 funding-age 现象，必须新建 rank/name，并以 predeclared regime + after-funding + after-cost 为最低门槛。

---

## 🔥 当前重点研究线：涨幅榜事件 Alpha（Event Study v1.6）

> Last review: 2026-05-12
> 起点：v1.5 日频事件研究已完成，确认「结构 × funding × 成交量」三维组合有厚 alpha 信号，但日频精度不够、事后偏差是瓶颈。
> 目标：用小时 K 线 + 逐笔 funding 结算数据，在日内级别发现可交易的 alpha。

### 阶段规划

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 1 | 数据基建：批量下载 1h klines + fundingRate 历史（Binance S3） | 🔄 进行中 |
| Phase 2 | 小时级事件解剖：峰值定位、结构重分类、funding settlement 效应、成交量衰减 | 待 Phase 1 |
| Phase 3 | 信号发现：事件日即时预测特征、funding 动态入场、volume decay 出场 | 待 Phase 2 |

### Phase 1 详细说明
- **1h klines**：为 v1.5 全部 32,860 个事件下载 ±3 天的小时 K 线（OHLCV + taker_buy_quote_volume）
  - 来源：`data.binance.vision` S3 monthly archive
  - ~6,300 个 (symbol, month) 组合，~126MB
  - 已有缓存 146 个，需下载 ~6,300 个
- **fundingRate 历史**：已全部存在（16,325 个 zip，679 个 symbol，2020-01 至今）
  - 列：`calc_time, funding_interval_hours, last_funding_rate`
  - ⚠️ 周期动态：同一 symbol 可能在不同时间段有不同的 funding_interval_hours（如从 8h 变为 4h）
- **产物**：合并后的小时级事件面板 pickle，每行 = (symbol, hour_ts, ohlcv, funding_rate, funding_interval, event_meta)

### 关键假设（待 Phase 2/3 验证）
- H1: 前 4 小时决定后续走势（4h 内回撤 < 3% + 量能持续 → continuation）
- H2: Funding settlement 时点是入场/出场锚（极端负 funding → 结算前做多、结算后减仓）
- H3: 量能衰减速度是退出信号（小时量跌至事件小时 50% → 离场）
- H4: Taker Buy Ratio 是真实买盘指标
- H5: 入场时机优化（事件后 2-4h 入场 vs 事件日收盘入场）

### 产物索引
- 脚本：`scripts/prepare_hourly_event_data_v1_6.py`
- 数据：`reports/artifacts/binance_hourly_event_study_v1_6/`
- 报告：（Phase 2 产出）

## 当前目标
- 持续 intake 新策略 / 新论文 / 新 repo / 新 alpha
- 用最小但诚实的验证快速给出 verdict
- 把真正存活的候选推进到 `P2 -> P3 -> Paper launch queue -> handoff`
- handoff 完成后，继续寻找下一条新策略

## 当前文档分工
- 固定规则：`docs/BOT2_BOT3_POLICY.md`
- 运行状态：`docs/BOT2_BOT3_STATE.md`
- live payload 模板：
  - `docs/AUTO_OPTIMIZATION_CRON_PROMPT.txt`
  - `docs/BOT2_STRATEGY_REVIEW_CRON_PROMPT.txt`
- 项目板：`docs/TODO.md`
- Rank154 归档入口：`docs/RANK154_ARCHIVE_CLOSEOUT.md`
- 长期/历史参考：
  - `docs/ROADMAP.md`
  - `docs/TODO_ARCHIVE_2026-03-24.md`

## 当前阅读顺序
1. 先看 `docs/BOT2_BOT3_POLICY.md`
2. 再看 `docs/BOT2_BOT3_STATE.md`
3. 需要项目导航时再看 `docs/TODO.md`
4. 若查 Rank154 系列，只看 `docs/RANK154_ARCHIVE_CLOSEOUT.md` 作为最终状态入口
5. 只有回看长期/历史时才打开 `docs/ROADMAP.md` 或 `docs/TODO_ARCHIVE_2026-03-24.md`

## 配套规划文档 / Site mirrors
- `docs/TODO.md`
  - 站点镜像：`https://jp.jerrypsy.top/momentum/plans/momentum_todo.html`
- `docs/RANK154_ARCHIVE_CLOSEOUT.md`
  - 站点镜像：`https://jp.jerrypsy.top/momentum/paper/rank154_archive_closeout.html`
- `docs/RESEARCH_TRENDLINE_EVENT.md`
  - 站点镜像：`https://jp.jerrypsy.top/momentum/plans/trendline_event_research.html`
- `plans/report.html`
  - 目录页：`https://jp.jerrypsy.top/momentum/plans/report.html`
