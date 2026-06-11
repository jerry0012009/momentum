# 2026-04-04 21:12 UTC — Rank 6 park reframe review

## 为什么本轮选 Rank 6
- 本轮按 `bot6` 约束仅处理 `Rank 1~37` 中已 `park` 的 1 条。
- `Rank 6` 上次 park-reframe 是 `2026-03-23 05:04 UTC`，已超过 7 天。
- 期间出现了新的旁证：`2026-03-26_2233_btc-ada-57s-tick-lag-alpha.md`，可用于判断这条线是“可窄救”，还是应继续保留 park。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-16_2149_intraday-tsmom-session-park.md`（用于回看 Rank 5/6 邻近语境）
- `research/park_reframe/2026-03-23_0504_rank6-park-reframe.md`
- `research/quant_digests/2026-03-26_2233_btc-ada-57s-tick-lag-alpha.md`

---

## 1) 原 Rank 为什么 park？
`Rank 6` 的原命题是把 `BTC -> COIN/MSTR(或外部 proxy)` 写成可直接交易的 lag-trade / lead-follow entry。

被 park 的核心原因没有变：
- 低成本下只剩薄 pocket；
- 一抬成本就明显失真；
- 时段稳定性与跨标的稳定性不够，难以支撑“可独立承压”的 queue-facing alpha。

换成人话：不是“完全没同步信息”，而是“把同步关系直接当主入场”这层职责过重了。

## 2) 它更像 hard park 还是 soft park？
本轮判断：**soft park（但更偏硬）**。

- soft 的原因：主题层面（外部市场先发现价格）仍有信息残余；
- 偏硬的原因：这个残余越来越不支持 `15m` 级 direct lag-trade 读法。

## 3) 有没有“可救信号”？
有，但是“主题外流型”可救信号，不是原 rank 本体可救。

新增旁证（2026-03-26）把 lead-lag 明确量化到 **秒级（约 16~118 秒，均值约 56.5 秒）**，对 desk 的直接含义是：
- 若还存在边际 alpha，更像 `1m/3m` 的 event-driven catch-up / spread pocket；
- 而不是继续放在 `15m` 上写成慢速、共享、可普适的 direct lead-follow 入场。

所以“可救信号”存在，但它在语义上更像：
- **支持新 microstructure / faster-clock raw-alpha family**，
- 而不是支持再给旧 `Rank 6` 派生一条同语义 `Rank 6c`。

## 4) 最值得改的唯一一刀是什么？
唯一诚实的一刀仍是既有那条：

**把 `direct lag-trade entry` 降级为外部 lead-strength 的 context / overlay 角色（不再当主触发）。**

本轮新证据只是在这条轴上进一步收紧：
- “外部领先”若有效，可能需要更快时钟（1m/3m）与更执行导向的表达；
- 这不是第二条新主轴，而是对原有降级轴的强化。

## 5) 是否值得形成新的 derived hypothesis？
**结论：不值得；本轮 `keep_park`。**

原因：
1. 原 `park` 审计意义仍成立，不能推翻；
2. 唯一可救语义已被既有 `Rank 6b`（角色降级）覆盖；
3. 新增秒级 lead-lag 证据把主题继续外流到更快执行层 raw-alpha family，不再诚实属于旧 `Rank 6` 的窄派生。

---

## 本轮模板回答（简版）
- 原 rank 为什么 park：direct lag-trade 在成本与稳定性上不够诚实。
- hard/soft：soft park（偏硬）。
- 可救信号：有，主要是 lead-lag 主题在更快时钟仍可能有 residual。
- 唯一一刀：继续坚持“从 direct entry 降级成 context/overlay”。
- 是否派生：否，`keep_park`。

## 最终结论
- verdict: **`keep_park`**
- note: 原 `park` 保留；新增证据不支持再派生 `Rank 6c`，只强化“该主题应迁移到更快时钟 raw-alpha/execution family 或继续停留在既有 `Rank 6b` 的角色降级语义”。

## Git/执行备注
- 本轮只做最小必要文档改动。
- 工作区存在大量无关脏文件；为避免混提，本轮不做 selective commit。