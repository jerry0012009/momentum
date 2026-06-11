# 2026-03-23 05:04 UTC · Rank 6 park reframe

## 本轮范围与约束
- 只复盘 `Rank 1~37` 中已 `park` 的 1 条旧 rank。
- 保留原 `park` verdict 的审计意义，不改 `docs/TODO.md` 顶部排班。
- 每轮最多只给 1 条唯一主修改轴；若不够诚实，就维持 `keep_park`。

## 这轮为什么还是选 Rank 6
- `Rank 1~37` 里的 parked rank 近几天已被高频覆盖；`Rank 6` 虽在 7 天内复盘过，但 **2026-03-23 04:49 UTC** 新增了明确新证据：`2026-03-23_0449_etf-close-momentum-session-confirm-gate.md`。
- 这条新证据不是重复旧话，而是把外部 ETF / 美股 proxy 的残余信息量进一步**收窄到 US close session-specific continuation confirm**，因此值得判断：它是否足以在既有 `Rank 6b` 之外，再派生一条新的更窄 hypothesis。

## 原 rank 为什么 park
原 `Rank 6 / BTC -> COIN / MSTR proxy` 被 park，不是因为完全没同步味道，而是因为把它写成 **direct lag-trade entry** 后，证据不够诚实：

- 最不差的 `btc_large_move_follow_proxy` 在 `6bps/side` 下也只是薄 pocket：
  - `mean_total_return≈+2.39%`
  - `positive_asset_ratio≈100%`
  - `mean_trades≈110`
- 但一旦把成本抬到 `10bps/side`，三档最小规则全部转负。
- `mean_sign_hit_rate` 只在 `50~52%` 左右，边薄得像同步噪音，而不是可独立承压的主 alpha。
- time-pocket 也不稳：
  - `COIN` 只有中间时段明显为正；
  - `MSTR` 则是中间时段转负。

所以原审计结论要保留：**把 BTC->proxy 关系硬写成下一根 direct lag trade，不够抗成本，也不够抗时段漂移。**

## hard park 还是 soft park
本轮仍判断它更像 **`soft park`**。

原因：
- 原 direct-entry 版本已经被审计消费，不能翻案；
- 但它并不是“主题彻底没信息”，而是更像**信号职责放错层**；
- 先前已经有 `Rank 6b` 把它降级成 `ETF / US proxy lead-strength shared regime gate`，说明可救点在“角色下调”，不是“继续给原 lag trade 补丁”。

## 有没有可救信号
有，但力度只够**收紧既有 Rank 6b 的适用边界**，不够再派生 `Rank 6c`。

### 可救信号 1：原主题并非纯噪音
- 原 clean replication 至少留下了低成本薄 pocket，说明“外部代理市场先动”并非完全无信息。
- 真正失败的是：把这层信息误当成可全天复用、可直接吃成本的独立 entry。

### 可救信号 2：新证据把残余价值进一步收窄到 session-specific confirm
`2026-03-23_0449_etf-close-momentum-session-confirm-gate.md` 给出的最关键信号，不是“ETF 又能做一套新 alpha”，而是：
- `15:30–16:00 ET` ETF close-window momentum 在 repo 里表现最好；
- 更像 `BTC/ETH 15m continuation confirm / short-veto`；
- **不适合作为全天 shared gate**；
- 对 `SOL` 的迁移性明显更弱。

换句话说，这条新证据只是把先前 `Rank 6b` 的“shared regime gate”进一步缩成：
- 优先 `BTC/ETH`，弱化 `SOL`；
- 优先 `US close` 邻近时段，而不是全天；
- 更像 continuation confirm / short-veto，而不是 broad 全天 allow/deny。

## 最值得改的唯一一刀
如果只说唯一值得保留的一刀，本轮仍是：

**把 `Rank 6` 从 direct lag-trade entry 降级成外部 ETF / US proxy 的 shared context layer。**

但和上轮相比，本轮新增证据只是在这个唯一主轴上补了一句更严格的实现边界：
- **更像 `US close` 附近的 session-specific continuation confirm / short-veto；**
- **不像全天共享 regime gate。**

这属于**既有 Rank 6b 的实现收紧**，不是新的主修改轴。

## 是否值得形成新的 derived hypothesis
**本轮结论：不值得。**

最终状态：`keep_park`

原因：
1. `Rank 6b` 已经消费了最自然、最诚实的单轴改写：`direct lag-trade -> shared external lead-strength gate`。
2. 2026-03-23 的 ETF close-window 新证据，并没有再提供第二条独立主轴；它只是把 `Rank 6b` 的使用边界收紧成 `US close / BTC-ETH-first / continuation-confirm`。
3. 若现在再起草 `Rank 6c`，本质上会变成在已有 `6b` 上继续做子切片，容易滑向多轴细分与重复派生，不符合 bot6 每轮只保留 1 条唯一主修改轴的纪律。

## bot2 / bot3 可用的最短读法
- 原 `park`：保留。
- 当前判断：`soft park`。
- 可救信号：有，但只支持**收紧 Rank 6b 的实现边界**。
- 最值得改的一刀：仍是 `direct lag-trade -> external shared gate`，不新增第二条主轴。
- 为什么现在不 draft 新假设：因为 2026-03-23 的 ETF close-window 证据只是说明 **Rank 6b 不应写成全天 shared gate，而应写成 US close session-specific continuation confirm / short-veto**；这更像实现细化，不够单独长成 `Rank 6c`。

## 本轮结论
- 原 rank 为什么 park：direct lag-trade 过薄、成本敏感、time-pocket 不稳。
- 它更像 hard park 还是 soft park：**soft park**。
- 有没有可救信号：**有，但只支持收紧既有 `Rank 6b` 的边界**。
- 最值得改的唯一一刀：**仍是把外部 proxy 从 direct entry 降级成 shared context / gate**。
- 是否值得形成新的 derived hypothesis：**不值得，本轮 `keep_park`**。

## 备注
- 本轮只更新 `research/park_reframe/INDEX.md` 与 `docs/PARK_REFRAME_QUEUE.md` 的复盘记录，不改 `docs/TODO.md`。
- 工作区存在大量与本轮无关脏文件；为避免混提，本轮只做最小必要文件改动，不做 selective commit。
