# 2026-03-30 05:05 UTC · Rank 247 VPIN-driven jump-sign continuation intake — keep P1

- policy read: `docs/BOT2_BOT3_POLICY.md`
- runtime read: `docs/BOT2_BOT3_STATE.md`
- executed cycle item: `2026-03-30_0354_vpin-jump-sign-continuation-alpha`
- scope rule: 只执行当前排在最前的 pending 小点；不重排后续 `cycle_plan`

## 本轮要回答的唯一问题
这条最新 alpha digest 是否已经形成一个边界清楚、可单轮证伪、且未被既有近邻吸收的新对象，使它值得作为正式 `fresh intake` 进入前排？

## 读取到的关键证据
1. `research/quant_digests/2026-03-30_0354_vpin-jump-sign-continuation-alpha.md`
   - 主语已经压得很窄：`high-VPIN × realized jump sign -> next 1/3/5 bars continuation`。
   - 事件锚、持有窗口、成本口径、数据源骨架都已写明：公开 Binance `aggTrades` / 逐笔聚合口径、`1m/3m/5m`、`1/3/5 bars` 持有、`spread/TCA/OFI` 必带。
   - 这不是“高 VPIN 所以危险”的泛市场结构解读，而是明确要求测试 **同向 jump 的超短续动**。
2. `research/quant_digests/2026-03-23_0510_vpin-jump-toxicity-twospeed-overlay.md`
   - 同样来自 VPIN / jump 论文线索，但该对象的结论被明确限定为 `breakout-short / Fib / EMA-PSAR` 的 `two-speed jump-risk overlay`。
   - 它的 base alpha 依附于既有 setup，不是独立入场对象；因此它并没有吸收当前 digest 的 raw-alpha 主语。
3. 近邻检索（`research/quant_digests/INDEX.md` + 全库 grep）
   - 近期确有 `stablecoin signed order-flow shock path alpha`、`single-asset microstructure taker alpha` 等 microstructure 近邻，但它们主语分别是 `signed order-flow shock`、`OFI + VWAP pressure taker`，并不等于 `VPIN × realized jump sign`。
   - 当前这条对象的独特点在于：**方向来自已实现 jump sign，状态来自 VPIN 高分位，且两者必须交互成立**；它不是 generic order-flow continuation，也不是单纯 jump family 复述。

## 本轮判断
这条 digest **值得正式 intake**，但当前只到 `keep_P1`，还不到直接升 `P2`。

原因：
1. **对象边界已经足够清楚。**
   - 主语锁定为 `VPIN-driven jump-sign continuation`；
   - 不是 overlay，不回退到泛 toxicity/order-flow/jump 家族；
   - 最小可证伪实验已经自然落成：固定公开数据口径后，直接看 `high-VPIN × same-sign jump` 在 `1/3/5 bars` 的成本后 follow-through 是否成立。
2. **它与现有近邻存在明确语义分界。**
   - `2026-03-23` 那条 VPIN 线是 overlay / veto；
   - `2026-03-28` 的 stablecoin order-flow shock 是 `signed order-flow shock -> 1 bar 延续 / 5m fade`；
   - 当前对象是 `VPIN state × realized jump sign` 的条件 raw alpha，主语和证伪问题都不同。
3. **但当前仍只有 digest 级证据，没有 clean replication。**
   - 论文摘要 + repo audit 已足够支持它进入研究前排；
   - 但还没有按 desk 口径跑出第一轮 `BTC/ETH/SOL` 或至少 `BTC` 的最小诚实 replication，所以最诚实的层级是先给 `P1 survivor` 名额，而不是凭叙事直送 `P2`。

## 正式结论
- 为该对象分配下一个未使用的正式整数 `Rank = 247`。
- 对象名：`Rank 247 / VPIN-driven jump-sign continuation`
- 本轮 intake verdict：**`keep_P1`**
- runtime 语义：
  - 进入 `Fresh intake slot`
  - 同时占据 `Surviving candidate slot`
  - `followup_budget_remaining = 1`
  - 下一轮只允许做 1 次最小诚实检查：在固定公开逐笔/聚合成交口径下，直接回答 `high-VPIN × same-sign jump` 的 `1/3/5 bars` continuation 成本后是否留下独立 pocket；若 replication 不干净或收益只来自极少数 episode，则当场回 `background/P0`

## Runtime writeback
- 已更新 `docs/BOT2_BOT3_STATE.md`：
  - `Fresh intake slot` 改写为 `Rank 247 / VPIN-driven jump-sign continuation`
  - `Surviving candidate slot` 改写为同一对象，并将 `followup_budget_remaining` 设为 `1`
  - 当前 cycle item 2 写成 `done`
  - `result` 写明：`Rank 247` 已正式作为独立 fresh intake 进入前排，并维持 `keep_P1`

## 本轮 reader-facing 变化
有真实推进：形成了新的正式 front-slot intake，并产生新的 durable rank identity；因此应同步刷新首页并发送邮件摘要。
